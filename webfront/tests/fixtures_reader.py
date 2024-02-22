import json

import copy

from webfront.searcher.elastic_controller import ElasticsearchController

from webfront.models import Entry, Taxonomy, TaxonomyPerEntry, TaxonomyPerEntryDB


def get_id(*args):
    return "-".join([a for a in args if a is not None])


class FixtureReader:

    def __init__(self, fixture_paths):
        self.ida_to_add = {}
        self.entries = {}
        self.proteins = {}
        self.structures = {}
        self.entry_protein_list = []
        self.protein_structure_list = {}
        self.tax2lineage = {}
        self.tax2rank = {}
        self.sets = {}
        self.proteomes = {}
        self.entry_annotations = {}
        self.search = None
        for path in fixture_paths:
            with open(path) as data_file:
                data = json.load(data_file)
                self.load_from_json(data)

    def load_from_json(self, data):
        for fixture in data:
            if fixture["model"] == "webfront.Entry":
                self.entries[fixture["fields"]["accession"].lower()] = fixture["fields"]
            elif fixture["model"] == "webfront.Protein":
                self.proteins[fixture["fields"]["accession"].lower()] = fixture[
                    "fields"
                ]
                self.protein_structure_list[fixture["fields"]["accession"].lower()] = []
                if "ida_id" in fixture["fields"]:
                    ida_id = fixture["fields"]["ida_id"]
                    if ida_id not in self.ida_to_add:
                        self.ida_to_add[ida_id] = {
                            "id": ida_id,
                            "ida_id": ida_id,
                            "ida": fixture["fields"]["ida"],
                            "representative": {
                                "accession": fixture["fields"]["accession"].lower(),
                                "length": fixture["fields"]["length"],
                                "domains": [],
                            },
                            "counts": 0,
                        }
                    self.ida_to_add[ida_id]["counts"] += 1

            elif fixture["model"] == "webfront.Structure":
                self.structures[fixture["fields"]["accession"].lower()] = fixture[
                    "fields"
                ]
            elif fixture["model"] == "webfront.ProteinEntryFeature":
                self.entry_protein_list.append(fixture["fields"])
                # complete representative info

            elif fixture["model"] == "webfront.ProteinStructureFeature":
                self.protein_structure_list[
                    fixture["fields"]["protein"].lower()
                ].append(fixture["fields"])
            elif fixture["model"] == "webfront.Taxonomy":
                self.tax2lineage[fixture["fields"]["accession"].lower()] = fixture[
                    "fields"
                ]["lineage"].split()
                self.tax2rank[fixture["fields"]["accession"].lower()] = fixture[
                    "fields"
                ]["rank"]
            elif fixture["model"] == "webfront.Proteome":
                self.proteomes[fixture["fields"]["accession"].lower()] = fixture[
                    "fields"
                ]
            elif fixture["model"] == "webfront.Set":
                self.sets[fixture["fields"]["accession"].lower()] = fixture["fields"]
            elif fixture["model"] == "webfront.EntryAnnotation":
                self.entry_annotations[fixture["fields"]["accession"].lower()] = (
                    fixture["fields"]
                )

    def get_entry2set(self):
        e2s = {}
        for s in self.sets:
            for n in self.sets[s]["relationships"]["nodes"]:
                if n["type"] == "entry":
                    db = self.sets[s]["source_database"]
                    # if db == "node":
                    #     db = "kegg"
                    if n["accession"].lower() not in e2s:
                        e2s[n["accession"].lower()] = []
                    e2s[n["accession"].lower()].append(
                        {"accession": s, "source_database": db}
                    )
        return e2s

    def get_fixtures(self):
        to_add = []
        entry2set = self.get_entry2set()

        # Creating obj to add for proteins with entries
        for ep in self.entry_protein_list:
            e = ep["entry"]
            p = ep["protein"]
            proteome = self.proteins[p]["proteome"].lower()
            obj = {
                "entry_acc": e,
                "entry_type": self.entries[e]["type"],
                "entry_db": self.entries[e]["source_database"],
                "entry_integrated": self.entries[e]["integrated"],
                "entry_date": self.entries[e]["entry_date"],
                "text_entry": e
                + " "
                + self.entries[e]["type"]
                + " "
                + (" ".join(self.entries[e]["description"])),
                "protein_acc": p,
                "protein_db": self.proteins[p]["source_database"],
                "protein_af_score": 0.5 if self.proteins[p]["in_alphafold"] else -1,
                "text_protein": p
                + " "
                + self.proteins[p]["source_database"]
                + " "
                + (" ".join(self.proteins[p]["description"])),
                "ida_id": self.proteins[p]["ida_id"],
                "ida": self.proteins[p]["ida"],
                "tax_id": self.proteins[p]["organism"]["taxId"],
                "tax_name": self.proteins[p]["organism"]["name"],
                "tax_lineage": self.tax2lineage[self.proteins[p]["organism"]["taxId"]],
                "tax_rank": self.tax2rank[self.proteins[p]["organism"]["taxId"]],
                "proteome_acc": self.proteomes[proteome]["accession"],
                "proteome_name": self.proteomes[proteome]["name"],
                "proteome_is_reference": self.proteomes[proteome]["is_reference"],
                "text_proteome": proteome + " " + self.proteomes[proteome]["name"],
                "entry_protein_locations": ep["coordinates"],
                "protein_length": self.proteins[p]["length"],
                "protein_is_fragment": self.proteins[p]["is_fragment"],
                "id": get_id(e, p),
            }
            obj["text_taxonomy"] = obj["tax_id"] + " " + (" ".join(obj["tax_lineage"]))

            # In case that protein also has a structure
            if p in self.protein_structure_list:
                for sp in self.protein_structure_list[p]:
                    c = copy.copy(obj)
                    c["structure_acc"] = sp["structure"]
                    c["structure_evidence"] = self.structures[sp["structure"]][
                        "experiment_type"
                    ]
                    c["structure_resolution"] = self.structures[sp["structure"]][
                        "resolution"
                    ]
                    c["structure_date"] = self.structures[sp["structure"]][
                        "release_date"
                    ]
                    c["structure_chain"] = sp["structure"] + " - " + sp["chain"]
                    c["structure_chain_acc"] = sp["chain"]
                    c["text_structure"] = c["structure_acc"] + " " + sp["chain"]

                    c["entry_structure_locations"] = ep["coordinates"]
                    c["structure_protein_locations"] = sp["coordinates"]
                    c["structure_protein_acc"] = p
                    # c["protein_structure"] = sp["mapping"]
                    if e in entry2set:
                        for e2s in entry2set[e]:
                            c2 = copy.copy(c)
                            c2["set_acc"] = e2s["accession"]
                            c2["set_db"] = e2s["source_database"]
                            c2["text_set"] = c2["set_acc"] + " " + c2["set_db"]
                            c2["id"] = get_id(
                                e, p, sp["structure"], sp["chain"], e2s["accession"]
                            )
                            to_add.append(c2)
                    else:
                        c["id"] = get_id(e, p, sp["structure"], sp["chain"])
                        to_add.append(c)
            else:
                if e in entry2set:
                    for e2s in entry2set[e]:
                        c2 = copy.copy(obj)
                        c2["id"] = get_id(e, p, e2s["accession"])
                        c2["set_acc"] = e2s["accession"]
                        c2["set_db"] = e2s["source_database"]
                        c2["text_set"] = c2["set_acc"] + " " + c2["set_db"]
                        to_add.append(c2)
                else:
                    to_add.append(obj)

        # Creating obj to add for proteins without entries but with structures
        proteins = [p["protein"] for p in self.entry_protein_list]
        for p, chains in self.protein_structure_list.items():
            if p not in proteins:
                for sp in chains:
                    proteome = self.proteins[p]["proteome"].lower()
                    to_add.append(
                        {
                            "text": p + " " + sp["structure"],
                            "protein_acc": p,
                            "protein_db": self.proteins[p]["source_database"],
                            "protein_af_score": (
                                0.5 if self.proteins[p]["in_alphafold"] else -1
                            ),
                            "text_protein": p
                            + " "
                            + self.proteins[p]["source_database"]
                            + " "
                            + (" ".join(self.proteins[p]["description"])),
                            "tax_id": self.proteins[p]["organism"]["taxId"],
                            "tax_name": self.proteins[p]["organism"]["name"],
                            "tax_rank": self.tax2rank[
                                self.proteins[p]["organism"]["taxId"]
                            ],
                            "tax_lineage": self.tax2lineage[
                                self.proteins[p]["organism"]["taxId"]
                            ],
                            "proteome_acc": self.proteomes[proteome]["accession"],
                            "proteome_name": self.proteomes[proteome]["name"],
                            "proteome_is_reference": self.proteomes[proteome][
                                "is_reference"
                            ],
                            "protein_length": self.proteins[p]["length"],
                            "id": get_id(None, p, sp["structure"], sp["chain"]),
                            "structure_acc": sp["structure"],
                            "structure_evidence": self.structures[sp["structure"]][
                                "experiment_type"
                            ],
                            "structure_resolution": self.structures[sp["structure"]][
                                "resolution"
                            ],
                            "structure_date": self.structures[sp["structure"]][
                                "release_date"
                            ],
                            "structure_chain": sp["structure"] + " - " + sp["chain"],
                            "structure_chain_acc": sp["chain"],
                            "text_structure": sp["structure"] + " " + sp["chain"],
                            "structure_protein_locations": sp["coordinates"],
                            "structure_protein_acc": p,
                            # "protein_structure": sp["mapping"],
                        }
                    )

        # getting representative coordinates for IDA
        for ep in self.entry_protein_list:
            e = ep["entry"]
            p = ep["protein"]
            if e.startswith("pf") or e.startswith("ipr"):
                for ida in self.ida_to_add.values():
                    if p == ida["representative"]["accession"]:
                        ida["representative"]["domains"].append(
                            {"entry": e, "coordinates": ep["coordinates"]}
                        )

        # Creating obj to add for proteins without entry or structure
        for p in self.proteins:
            p_ocurrences = len([t for t in to_add if t["protein_acc"] == p])
            if p_ocurrences == 0:
                to_add.append(
                    {
                        "text": p,
                        "protein_acc": p,
                        "protein_db": self.proteins[p]["source_database"],
                        "protein_af_score": (
                            0.5 if self.proteins[p]["in_alphafold"] else -1
                        ),
                        "text_protein": p + " " + self.proteins[p]["source_database"],
                        "tax_id": self.proteins[p]["organism"]["taxId"],
                        "tax_name": self.proteins[p]["organism"]["name"],
                        "tax_rank": self.tax2rank[
                            self.proteins[p]["organism"]["taxId"]
                        ],
                        "tax_lineage": self.tax2lineage[
                            self.proteins[p]["organism"]["taxId"]
                        ],
                        "proteome_acc": self.proteomes[proteome]["accession"],
                        "proteome_name": self.proteomes[proteome]["name"],
                        "proteome_is_reference": self.proteomes[proteome][
                            "is_reference"
                        ],
                        "protein_length": self.proteins[p]["length"],
                        "id": get_id(None, p),
                    }
                )

        lower = []
        for doc in to_add:
            lower.append(
                {
                    k: (
                        v.lower()
                        if type(v) == str
                        and k != "ida"
                        and "date" not in k
                        and "chain" not in k
                        else v
                    )
                    for k, v in doc.items()
                }
            )
        return lower

    def add_to_search_engine(self, docs):
        search = ElasticsearchController()
        search.add(docs)
        # apparently you can't reuse the connection, so I create a second one
        search2 = ElasticsearchController()
        search2.add(self.ida_to_add.values(), True)

    def generate_tax_per_entry_fixtures(self, docs):
        counters = {}
        counters_db = {}
        for doc in docs:
            if "entry_acc" not in doc or "tax_lineage" not in doc:
                continue
            entry = doc["entry_acc"]
            entry_db = doc["entry_db"]
            lineage = doc["tax_lineage"]
            if entry not in counters:
                counters[entry] = {}
            if entry_db not in counters_db:
                counters_db[entry_db] = {}
            for tax in lineage:
                if tax not in counters[entry]:
                    counters[entry][tax] = {
                        "structures": 0,
                        "proteins": 0,
                        "proteomes": 0,
                    }
                if tax not in counters_db[entry_db]:
                    counters_db[entry_db][tax] = {
                        "entries": 0,
                        "proteomes": 0,
                        "proteins": 0,
                        "structures": 0,
                    }
                counters_db[entry_db][tax]["entries"] += 1
                if doc["structure_acc"] is not None:
                    counters[entry][tax]["structures"] += 1
                    counters_db[entry_db][tax]["structures"] += 1
                if doc["protein_acc"] is not None:
                    counters[entry][tax]["proteins"] += 1
                    counters_db[entry_db][tax]["proteins"] += 1
                if doc["proteome_acc"] is not None:
                    counters[entry][tax]["proteins"] += 1
                    counters_db[entry_db][tax]["proteins"] += 1
        for entry in counters:
            for tax in counters[entry]:
                txe = TaxonomyPerEntry(
                    entry_acc=Entry.objects.get(accession=entry.upper()),
                    taxonomy=Taxonomy.objects.get(accession=tax),
                    counts=counters[entry][tax],
                )
                txe.save()
        for db in counters_db:
            for tax in counters_db[db]:
                txe = TaxonomyPerEntryDB(
                    source_database=db,
                    taxonomy=Taxonomy.objects.get(accession=tax),
                    counts=counters_db[db][tax],
                )
                txe.save()

    def clear_search_engine(self):
        search = ElasticsearchController()
        search.clear_all_docs()
