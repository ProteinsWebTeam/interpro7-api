from urllib.error import URLError
from webfront.views.custom import is_single_endpoint

from django.db.models import Count
from webfront.models import (
    Entry,
    EntryAnnotation,
    EntryTaxa,
    Isoforms,
    Release_Note,
    TaxonomyPerEntry,
    TaxonomyPerEntryDB,
    Taxonomy,
    ProteinExtraFeatures,
    ProteinResidues,
)
from webfront.views.custom import filter_queryset_accession_in
from webfront.exceptions import (
    EmptyQuerysetError,
    DeprecatedModifier,
    ExpectedUniqueError,
    InvalidOperationRequest,
)
from django.conf import settings

from urllib import request, parse
from json import loads
import gzip

# MAQ bypassing SSL errors
# ssl._create_default_https_context = ssl._create_unverified_context

go_terms = settings.INTERPRO_CONFIG.get("key_go_terms", {})
organisms = settings.INTERPRO_CONFIG.get("key_organisms", {})


class SmartRedirectHandler(request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return headers


def group_by_member_databases(general_handler):
    if is_single_endpoint(general_handler):
        holder = general_handler.queryset_manager.remove_filter(
            "entry", "source_database"
        )
        dbs = Entry.objects.get_queryset().values("source_database").distinct()
        qs = {
            db["source_database"]: general_handler.queryset_manager.get_queryset()
            .filter(member_databases__contains='"{}"'.format(db["source_database"]))
            .count()
            for db in dbs
        }

        general_handler.queryset_manager.add_filter("entry", source_database=holder)
        return qs


def group_by_go_categories(general_handler):
    template = '"code": "{}"'
    groups = {
        "P": "Biological Process",
        "C": "Cellular Component",
        "F": "Molecular Function",
    }
    if is_single_endpoint(general_handler):
        qs = {
            groups[cat]: general_handler.queryset_manager.get_queryset()
            .filter(go_terms__contains=template.format(cat))
            .count()
            for cat in groups
        }
        return qs


def group_by_go_terms(general_handler):
    q = "({})".format(" OR ".join(g.replace(":", "\\:") for g in go_terms))
    searcher = general_handler.searcher
    result = searcher.get_grouped_object(
        general_handler.queryset_manager.main_endpoint, "entry_go_terms", q, size=1000
    )
    return [
        (r["key"], {"value": r["unique"]["value"], "title": go_terms[r["key"]]})
        for r in result["groups"]["buckets"]
        if r["key"] in go_terms
    ]


def get_queryset_to_group(general_handler, endpoint_queryset):
    queryset = general_handler.queryset_manager.get_queryset()
    if endpoint_queryset.objects.count() == queryset.count():
        return endpoint_queryset.objects
    return endpoint_queryset.objects.filter(accession__in=queryset.distinct())


def group_by_organism(general_handler, endpoint_queryset):
    searcher = general_handler.searcher
    qs = general_handler.queryset_manager.get_searcher_query()
    tmp = [
        (
            org,
            {
                "value": searcher.count_unique(
                    qs + " && tax_lineage:{}".format(org),
                    "{}_acc".format(general_handler.queryset_manager.main_endpoint),
                ),
                "title": organisms[org],
            },
        )
        for org in organisms
    ]
    return [t for t in tmp if t[1]["value"] > 0]


def group_by_match_presence(general_handler, endpoint_queryset):
    searcher = general_handler.searcher
    qs = general_handler.queryset_manager.get_searcher_query()
    response = {
        "match_presence": {
            "true": searcher.count_unique(qs + " && _exists_:entry_acc", "protein_acc"),
            "false": searcher.count_unique(
                qs + " && !_exists_:entry_acc", "protein_acc"
            ),
        }
    }
    return response


def group_by_is_fragment(general_handler, endpoint_queryset):
    searcher = general_handler.searcher
    # qs = general_handler.queryset_manager.get_searcher_query()
    result = searcher.get_grouped_object("protein", "protein_is_fragment")

    boolean_tag = {
        "0": "false",
        0: "false",
        False: "false",
        "False": "false",
        "false": "false",
        "1": "true",
        1: "true",
        True: "true",
        "True": "true",
        "true": "true",
    }

    response = {
        "is_fragment": {
            boolean_tag[bucket["key"]]: bucket["unique"]["value"]
            for bucket in result["groups"]["buckets"]
        }
    }
    # print(response)
    return response


def group_by_is_reference(general_handler, endpoint_queryset):
    searcher = general_handler.searcher
    qs = general_handler.queryset_manager.get_searcher_query()
    response = {
        "proteome_is_reference": {
            "true": searcher.count_unique(
                qs + " && proteome_is_reference:true", "proteome_acc"
            ),
            "false": searcher.count_unique(
                qs + " && proteome_is_reference:false", "proteome_acc"
            ),
        }
    }
    return response


def group_by_annotations(general_handler):
    if is_single_endpoint(general_handler):
        queryset = EntryAnnotation.objects.values_list(
            "accession_id__source_database", "type"
        ).annotate(total=Count("type"))
        formatted_results = {}
        for source, type, total in list(queryset):
            if source not in formatted_results:
                formatted_results[source] = {}
            formatted_results[source][type] = total
        results = [(key, value) for key, value in formatted_results.items()]
        return results


def group_by(endpoint_queryset, fields):
    def inner(field, general_handler):
        if field not in fields:
            raise URLError(
                "{} is not a valid field to group entries by. Allowed fields : {}".format(
                    field, ", ".join(fields.keys())
                )
            )
        if "member_databases" == field:
            return group_by_member_databases(general_handler)
        if "go_terms" == field:
            return group_by_go_terms(general_handler)
        if "go_categories" == field:
            return group_by_go_categories(general_handler)
        if "ai_categories" == field:
            return group_by_ai_categories(general_handler)
        if "annotation" == field:
            return group_by_annotations(general_handler)
        if "tax_id" == field:
            return group_by_organism(general_handler, endpoint_queryset)
        if "match_presence" == field:
            return group_by_match_presence(general_handler, endpoint_queryset)
        if "is_fragment" == field:
            return group_by_is_fragment(general_handler, endpoint_queryset)
        if "proteome_is_reference" == field:
            return group_by_is_reference(general_handler, endpoint_queryset)
        if (
            is_single_endpoint(general_handler)
            and general_handler.queryset_manager.main_endpoint != "protein"
        ):
            qs = get_queryset_to_group(general_handler, endpoint_queryset)
            return qs.values_list(field).annotate(total=Count(field))
        else:
            searcher = general_handler.searcher
            result = searcher.get_grouped_object(
                general_handler.queryset_manager.main_endpoint, fields[field]
            )
            return result

    return inner


def sort_by(fields):
    def x(field, general_handler):
        if not is_single_endpoint(general_handler):
            # wl = {k: v for k, v in wl.items() if v is not None}
            raise URLError(
                "Sorting is not currently supported for multi-domains queries"
            )

        if field not in fields and field[1:] not in fields:
            raise URLError(
                "This query can't be be sorted by {}. The supported fields are {}".format(
                    field, ", ".join(fields.keys())
                )
            )
        general_handler.queryset_manager.order_by(field)

    return x


def filter_by_field(endpoint, field):
    def x(value, general_handler):
        general_handler.queryset_manager.add_filter(
            endpoint, **{"{}__iexact".format(field): value.lower()}
        )

    return x


def filter_by_key_species(value, general_handler):
    general_handler.queryset_manager.add_filter(
        "taxonomy", **{"accession__in": list(organisms.keys())}
    )


def filter_by_entry(value, general_handler):
    tax_id = general_handler.queryset_manager.filters["taxonomy"]["accession"]
    response = TaxonomyPerEntry.objects.filter(taxonomy__accession=tax_id).filter(
        entry_acc__accession=value.upper()
    )
    if len(response) == 0:
        response = TaxonomyPerEntry.objects.filter(taxonomy__in=tax_id).filter(
            entry_acc__accession=value.lower()
        )
        if len(response) == 0:
            raise EmptyQuerysetError("No documents found with the current selection")
    return response.first()


def filter_by_entry_db(value, general_handler):
    tax_id = general_handler.queryset_manager.filters["taxonomy"]["accession"]
    response = TaxonomyPerEntryDB.objects.filter(taxonomy__accession=tax_id).filter(
        source_database=value.lower()
    )
    if len(response) == 0:
        raise EmptyQuerysetError("No documents found with the current selection")

    return response.first()


def filter_by_min_value(endpoint, field, value, sorting_by=[], sort_pagination=True):
    def x(_, general_handler):
        general_handler.queryset_manager.add_filter(
            endpoint, **{"{}__gte".format(field): value}
        )
        sort_str = ""
        connector = ""
        for sort_field in sorting_by:
            if sort_field["direction"] in ("asc", "desc"):
                sort_str += "{}{}:{}".format(
                    connector, sort_field["name"], sort_field["direction"]
                )
            else:
                raise ValueError(
                    "{} is not a valid sorting order".format(sort_field["direction"])
                )
            connector = ","
        if len(sort_str) > 0:
            general_handler.queryset_manager.order_by(sort_str, sort_pagination)

    return x


def filter_by_boolean_field(endpoint, field):
    def x(value, general_handler):
        if value.lower() == "false":
            boolean_value = False
        else:
            boolean_value = True
        general_handler.queryset_manager.add_filter(
            endpoint, **{"{}".format(field): boolean_value}
        )

    return x


def filter_by_contains_field(endpoint, field, value_template="{}"):
    def x(value, general_handler):
        general_handler.queryset_manager.add_filter(
            endpoint, **{"{}__contains".format(field): value_template.format(value)}
        )

    return x


def filter_by_field_range(endpoint, field, value_template="{}"):
    def x(value, general_handler):
        pos = value.split("-")
        if is_single_endpoint(general_handler):
            general_handler.queryset_manager.add_filter(
                endpoint,
                **{
                    "{}__gte".format(field): value_template.format(pos[0]),
                    "{}__lte".format(field): value_template.format(pos[1]),
                },
            )
        else:
            general_handler.queryset_manager.add_filter(
                endpoint,
                **{
                    "{}_{}__gte".format(endpoint, field): value_template.format(pos[0]),
                    "{}_{}__lte".format(endpoint, field): value_template.format(pos[1]),
                },
            )

    return x


def filter_by_field_or_field_range(endpoint, field):
    def x(value, general_handler):
        minmax = value.split("-")
        if len(minmax) == 2 and minmax[0] and minmax[1]:
            filter_by_field_range(endpoint, field)(value, general_handler)
        elif len(minmax) == 1 and minmax[0]:
            filter_by_field(endpoint, field)(value, general_handler)
        else:
            raise URLError("{} is not a valid value for filter {}".format(value, field))

    return x


def get_single_value(field, from_elastic=False):
    if from_elastic:

        def x(value, general_handler):
            q = general_handler.queryset_manager.get_searcher_query()
            obj = general_handler.searcher._elastic_json_query(
                "{} && _exists_:{}&size=1".format(q, field)
            )
            total = obj["hits"]["total"]
            if type(total) == dict:
                total = obj["hits"]["total"]["value"]

            if total < 1:
                raise EmptyQuerysetError(
                    "No documents found with the current selection"
                )
            return {field: obj["hits"]["hits"][0]["_source"][field]}

        return x

    def x(value, general_handler):
        queryset = general_handler.queryset_manager.get_queryset()
        first = queryset.first()
        return first.__getattribute__(field)

    return x


def get_interpro_status_counter(field, general_handler):
    queryset = general_handler.queryset_manager.get_queryset().distinct()
    total = queryset.count()
    unintegrated = queryset.filter(integrated__isnull=True).count()
    return {"integrated": total - unintegrated, "unintegrated": unintegrated}


def filter_by_match_presence(value, general_handler):
    general_handler.queryset_manager.add_filter(
        "entry", **{"source_database__isnull": value.lower() != "true"}
    )

def filter_by_ai_entries(value, general_handler):
    if value == "MC":
        general_handler.queryset_manager.add_filter("entry", is_llm=False)
    elif value == "AI-R":
        general_handler.queryset_manager.add_filter("entry", is_llm=True, is_reviewed_llm=True)
    elif value == "AI-U":
        general_handler.queryset_manager.add_filter("entry", is_llm=True, is_reviewed_llm=False)

def group_by_ai_categories(general_handler):
    template = '"code": "{}"'
    id_to_params = {
        "MC": {"is_llm": False},
        "AI-R": {"is_llm": True, "is_reviewed_llm": True},
        "AI-U": {"is_llm": True, "is_reviewed_llm": False},
    }
    id_to_name = {
        "MC": "Manually Curated",
        "AI-R": "AI-Generated and Reviewed",
        "AI-U": "AI-Generated and Unreviewed"
    }
    if is_single_endpoint(general_handler):
        qs = {
            id_to_name[cat]: general_handler.queryset_manager.get_queryset()
            .filter(**id_to_params[cat])
            .count()
            for cat in id_to_params
        }
        return qs


def filter_by_latest_entries(value, general_handler):
    notes = Release_Note.objects.all()
    notes = notes.order_by("-release_date")
    if notes.count() == 0:
        raise ReferenceError("There are not release Notes")
    note = notes.first()
    new_entries = note.content["interpro"]["new_entries"]

    general_handler.queryset_manager.add_filter("entry", accession__in=new_entries)


def get_domain_architectures(field, general_handler):
    if field is None or field.strip() == "":
        # TODO: is there a better way to get this?
        accession = general_handler.queryset_manager.filters["entry"][
            "accession__iexact"
        ]
        return ida_search(accession, general_handler)


def filter_by_domain_architectures(field, general_handler):
    searcher = general_handler.searcher
    size = general_handler.pagination["size"]
    cursor = general_handler.pagination["cursor"]

    query = (
        general_handler.queryset_manager.get_searcher_query() + " && ida_id:" + field
    )
    endpoint = general_handler.queryset_manager.main_endpoint
    res, length, after_key, before_key, _ = searcher.get_list_of_endpoint(
        endpoint, rows=size, query=query, cursor=cursor
    )
    general_handler.modifiers.search_size = length
    general_handler.modifiers.after_key = after_key
    general_handler.modifiers.before_key = before_key
    return filter_queryset_accession_in(
        general_handler.queryset_manager.get_base_queryset(endpoint), res
    )


def get_entry_annotation(field, general_handler):
    annotation = []
    queryset = general_handler.queryset_manager.get_queryset()
    for entry in queryset:
        data = entry.entryannotation_set.filter(type=field)
        annotation.append(data[0])
    return annotation


def get_entry_annotation_info(field, general_handler):
    queryset = general_handler.queryset_manager.get_queryset()
    for entry in queryset:
        data = entry.entryannotation_set.filter(go=field).values(
            "accession", "type", "mime_type", "num_sequences"
        )
        annotation = data[0]
        return {
            "accession": annotation["accession"],
            "type": annotation["type"],
            "mime_type": annotation["mime_type"],
            "num_sequences": annotation["num_sequences"],
        }
    return {}


def add_extra_fields(endpoint, *argv):
    supported_fields = [
        f.name for f in endpoint._meta.get_fields() if not f.is_relation
    ] + list(argv)

    def x(fields, general_handler):
        fs = fields.split(",")
        other_fields = {}
        for field in fs:
            parts = field.split(":")
            f_name = parts[0]
            other_fields[f_name] = parts[1] if len(parts) > 1 else None
            if f_name not in supported_fields:
                raise URLError(
                    "{} is not a valid field to to be included. Allowed fields : {}".format(
                        field, ", ".join(supported_fields)
                    )
                )
        general_handler.queryset_manager.other_fields = other_fields

    return x


def ida_search(value, general_handler):
    searcher = general_handler.searcher
    size = general_handler.pagination["size"]
    cursor = general_handler.pagination["cursor"]

    conserve_order = "ordered" in general_handler.request.query_params
    entries = value.upper().split(",")
    exact_match = "exact" in general_handler.request.query_params
    if exact_match:
        query = "/{}/".format(
            "\-".join(
                [
                    (
                        f"PF[0-9]{{5}}\:{e}"
                        if e.startswith("IPR")
                        else f"{e}(\:IPR[0-9]{{6}})?"
                    )
                    for e in entries
                ]
            )
        )
    elif conserve_order:
        query = "ida:*{}*".format("*".join(entries))
    else:
        query = " && ".join(["ida:*{}*".format(e) for e in entries])
    if "ida_ignore" in general_handler.request.query_params:
        ignore_list = general_handler.request.query_params["ida_ignore"].split(",")
        if len(ignore_list) > 0:
            query = "({}) && ({})".format(
                query, " && ".join(["!ida:*{}*".format(e) for e in ignore_list])
            )

    return searcher.ida_query(query, size, cursor)


def get_isoforms(value, general_handler):
    isoforms = Isoforms.objects.filter(
        protein_acc__in=general_handler.queryset_manager.get_queryset()
    )
    if value is not None and value != "":
        isoforms = isoforms.filter(accession__iexact=value)
        if len(isoforms) == 0:
            raise EmptyQuerysetError(
                "There aren't isoforms with accession {}".format(value)
            )
        isoform = isoforms.first()
        return {
            "accession": isoform.accession,
            "protein_acc": isoform.protein_acc,
            "length": isoform.length,
            "sequence": isoform.sequence,
            "features": isoform.features,
        }

    return {"results": [iso.accession for iso in isoforms], "count": len(isoforms)}


def run_hmmsearch(model):
    """
    run hmmsearch using hmm model against reviewed uniprot proteins
    """
    parameters = {"seq": model, "seqdb": "swissprot"}

    enc_params = parse.urlencode(parameters).encode()
    url = "https://www.ebi.ac.uk/Tools/hmmer/search/hmmsearch"
    req = request.Request(
        url=url, data=enc_params, headers={"Accept": "application/json"}
    )
    with request.urlopen(req) as response:
        raw_results = response.read().decode("utf-8")
        results = loads(raw_results)
        return results["results"]["hits"]


def calculate_conservation_scores(entry_acc):
    """
    Get HMM Logo and convert it to conservation score
    :param pfam_acc:
    :return: list of scores
    """
    logo_data = EntryAnnotation.objects.filter(accession_id=entry_acc, type="logo")[0]
    logo_string = logo_data.value.decode("utf8")
    logo = loads(logo_string)
    max_height = logo["max_height_theory"]
    scores = []
    for pos, values in enumerate(logo["height_arr"]):
        total = 0
        for value in values:
            total += float(value.split(":")[1])
        # scale the total /max height ratio up by an order of magnitude
        score = round((total / max_height) * 10, 2)
        scores.append(score)
    return scores


def align_seq_to_model(domains, sequence):
    """
    align result of hmmscan with uniprot sequence
    """
    hmmfrom = domains["alihmmfrom"]
    hmmto = domains["alihmmto"]
    consensus = domains["alimodel"]
    aliseq = domains["aliaseq"]
    alisqfrom = domains["alisqfrom"]
    alisqto = domains["alisqto"]

    mappedseq = ""
    modelseq = ""
    if alisqfrom != 1:
        mappedseq += sequence[0 : alisqfrom - 1]
        for i in range(0, alisqfrom - 1):
            modelseq += "-"
    mappedseq += aliseq.upper()
    modelseq += consensus
    if alisqfrom != 1:
        mappedseq += sequence[alisqto : len(sequence)]
        for i in range(alisqto, len(sequence)):
            modelseq += "-"

    return mappedseq, modelseq, hmmfrom, hmmto, alisqfrom, alisqto


def get_hmm_matrix(logo, alisqfrom, alisqto, hmmfrom, hmmto, seqmotif, modelmotif):
    """
    generate sequence matrix (i.e. matrix[res] = "conservation_score_seqAA_modelposition")
    """
    matrix = {}
    count = hmmfrom - 1
    pos = 0
    logo_len = len(logo)
    for res in range(0, len(seqmotif)):
        if res < alisqfrom - 1 or count >= hmmto:
            # matrix[pos] = f"0_{seqmotif[res]}_0"
            pos += 1
        else:
            if seqmotif[res] == "-":
                count += 1
            elif modelmotif[res] == ".":
                pos += 1
                matrix[pos] = f"-1_None_0"
            else:
                logo_score = logo[count]
                seq_res = seqmotif[res]
                pos += 1
                matrix[pos] = f"{logo_score}_{seq_res}_{count}"
                count += 1
    return matrix


def format_logo(matrix):
    """
    re-arrange the data
    """
    output = []
    for res in matrix:
        score, aa, modelpos = matrix[res].split("_")
        score = float(score)
        modelpos = int(modelpos)

        output.append(
            {"position": res, "aa": aa, "score": score, "model_position": modelpos}
        )
    return output


def calculate_residue_conservation(entry_db, general_handler):
    """
    Calculate the conservancy score of each entry from entry_db matching the protein sequence
    :param entry_db: name of database to calculate entry conservation scores from
    :param general_handler:
    :return: An object with an array of hits and conservancy scores
    """
    queryset = general_handler.queryset_manager.get_queryset()
    # will always have one protein in queryset
    protein = queryset[0]

    if protein.source_database != "reviewed":
        raise InvalidOperationRequest(
            f"Conservation data can only be calculated for proteins in UniProt reviewed."
        )

    # get entries matching the sequence from the selected database
    q = "protein_acc:{} && entry_db:{}".format(
        protein.accession.lower(), entry_db.lower()
    )
    searcher = general_handler.searcher
    results = searcher.execute_query(q, None, None)
    # process each hit
    sequence = protein.sequence
    alignments = {"sequence": sequence, entry_db: {"entries": {}}}

    if (
        "hits" in results.keys()
        and "hits" in results["hits"]
        and len(results["hits"]["hits"]) > 0
    ):
        entries = results["hits"]["hits"]
        for entry in entries:
            entry_annotation = EntryAnnotation.objects.filter(
                accession_id=entry["_source"]["entry_acc"], type="hmm"
            )[0]
            model = gzip.decompress(entry_annotation.value).decode("utf-8")
            hits = run_hmmsearch(model)
            protein_dict = {x["acc"]: x for x in hits}
            protein_hits = list(filter(lambda x: x["acc"] == protein.identifier, hits))
            if len(protein_hits) > 0:
                alignments[entry_db]["entries"][entry_annotation.accession_id] = []
                logo_score = calculate_conservation_scores(
                    entry_annotation.accession_id
                )
                domains = [hit["domains"] for hit in protein_hits][0]
                for hit in domains:
                    # calculate scores for each domain hit for each entry
                    mappedseq, modelseq, hmmfrom, hmmto, alisqfrom, alisqto = (
                        align_seq_to_model(hit, sequence)
                    )
                    matrixseq = get_hmm_matrix(
                        logo_score,
                        alisqfrom,
                        alisqto,
                        hmmfrom,
                        hmmto,
                        mappedseq,
                        modelseq,
                    )
                    formatted_matrix = format_logo(matrixseq)
                    alignments[entry_db]["entries"][
                        entry_annotation.accession_id
                    ].append(formatted_matrix)
            else:
                if "warnings" not in alignments[entry_db]:
                    alignments[entry_db]["warnings"] = []
                alignments[entry_db]["warnings"].append(
                    f"Hmmer did not match Entry {entry_annotation.accession_id} with Protein {protein.identifier}."
                )
    return alignments


def get_value_for_field(field):
    def x(value, general_handler):
        queryset = general_handler.queryset_manager.get_queryset().first()
        if queryset.__getattribute__(field) is None:
            raise EmptyQuerysetError("This entity doesn't have " + field)
        return {field: queryset.__getattribute__(field)}

    return x


def get_taxonomy_by_scientific_name(scientific_name, general_handler):
    filters = general_handler.queryset_manager.filters
    filters["taxonomy"] = {"scientific_name": scientific_name}

    # Taxonomy has to be fetched before any further filters are applied
    queryset = general_handler.queryset_manager.get_queryset(only_main_endpoint=True)
    if queryset.count() == 0:
        raise EmptyQuerysetError(
            f"Failed to find Taxonomy node with scientific name '{scientific_name}'"
        )
    if queryset.count() > 1:
        raise ExpectedUniqueError(
            f"Found more than one Taxonomy node with scientific name '{scientific_name}'"
        )

    # The queryset contains the taxonomy object matching the scientific_name
    # the counters apply to the full dataset so we only return this data if
    # there are no other endpoints in the request
    if general_handler.queryset_manager.is_single_endpoint():
        return queryset

    # The counts for a member database can be fetched from TaxonomyPerEntryDB
    if "entry" in filters and bool(filters.get("entry")):
        filtered_queryset = TaxonomyPerEntryDB.objects.filter(
            taxonomy=queryset.first().accession,
            source_database=filters.get("entry")["source_database"],
        )
        if len(filtered_queryset) == 0:
            raise EmptyQuerysetError(
                f"Failed to find Taxonomy count associated with scientific name '{scientific_name}' and filters"
            )
        elif len(filtered_queryset) > 1:
            raise ExpectedUniqueError(
                f"Found more than one Taxonomy count with scientific name '{scientific_name}' and filters"
            )
        return filtered_queryset
    else:
        raise URLError(
            "scientific_name modifier currently only works with taxonomy endpoint and entry filter"
        )


def add_taxonomy_names(value, current_payload):
    names = {}
    to_query = set()
    for taxon in current_payload:
        names[taxon["metadata"]["accession"]] = taxon["metadata"]["name"]
        if "parent" in taxon["metadata"] and taxon["metadata"]["parent"] is not None:
            to_query.add(taxon["metadata"]["parent"])
        if (
            "children" in taxon["metadata"]
            and taxon["metadata"]["children"] is not None
        ):
            for child in taxon["metadata"]["children"]:
                to_query.add(child)
        if "extra_fields" in taxon and "lineage" in taxon["extra_fields"]:
            for tax in taxon["extra_fields"]["lineage"].split():
                to_query.add(tax)

    qs = Taxonomy.objects.filter(accession__in=[q for q in to_query if q not in names])
    for t in qs:
        names[t.accession] = t.scientific_name
    return names


def get_sunburst_taxa(value, general_handler):
    taxa = EntryTaxa.objects.filter(
        accession__in=general_handler.queryset_manager.get_queryset()
    )
    if taxa.count() == 0:
        raise EmptyQuerysetError("This entry doesn't have taxa")
    return {"taxa": taxa.first().tree}


def extra_features(value, general_handler):
    features = ProteinExtraFeatures.objects.filter(
        protein_acc__in=general_handler.queryset_manager.get_queryset()
    )
    payload = {}
    for feature in features:
        if feature.entry_acc not in payload:
            payload[feature.entry_acc] = {
                "accession": feature.entry_acc,
                "source_database": feature.source_database,
                "locations": [],
            }
        payload[feature.entry_acc]["locations"].append(
            {
                "fragments": [
                    {
                        "start": feature.location_start,
                        "end": feature.location_end,
                        "seq_feature": feature.sequence_feature,
                    }
                ]
            }
        )
    return payload


def residues(value, general_handler):
    residues_qs = ProteinResidues.objects.filter(
        protein_acc__in=general_handler.queryset_manager.get_queryset()
    )
    payload = {}
    for residue in residues_qs:
        if residue.entry_acc not in payload:
            payload[residue.entry_acc] = {
                "accession": residue.entry_acc,
                "source_database": residue.source_database,
                "name": residue.entry_name,
                "locations": [],
            }
        payload[residue.entry_acc]["locations"].append(
            {
                "description": residue.description,
                "fragments": [
                    {"residues": f[0], "start": f[1], "end": f[2]}
                    for f in residue.fragments
                ],
            }
        )
    return payload


def get_subfamilies(value, general_handler):
    queryset = general_handler.queryset_manager.get_queryset().first()
    entries = Entry.objects.filter(integrated=queryset.accession, is_public=False)
    if isinstance(value, str) and value.strip():
        entries = entries.filter(accession=value)
    if len(entries) == 0:
        raise EmptyQuerysetError("There is are not subfamilies for this entry")
    general_handler.modifiers.search_size = len(entries)
    return entries


def mark_as_subfamily(value, general_handler):
    general_handler.queryset_manager.add_filter("entry", is_public=False)


def show_subset(value, general_handler):
    general_handler.queryset_manager.show_subset = True


def passing(x, y):
    pass


def get_deprecated_response(message):
    def deprecated(value, general_handler):
        raise DeprecatedModifier(message)

    return deprecated
