import logging
from datetime import date
from itertools import chain, islice

from tqdm import tqdm

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from release.models import iprel
from webfront.models import Entry, Protein, Structure
import json

# global array
errors = []


# helpers
def chunks(iterable, maximum=1000):
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, maximum - 1))


def queryset_from_model(m, db_name='interpro_ro'):
    return m.objects.using(db_name).all()


def subset_iterator_from_queryset(qs, n, n_skip=0, position=0):
    return tqdm(
        qs[n_skip:n].iterator(),
        initial=n_skip,
        total=n,
        mininterval=1,
        dynamic_ncols=True,
        position=position
    )


def bulk_insert(chunk, model):
    try:
        model.objects.bulk_create((e for e in chunk), batch_size=1000)
    except IntegrityError as err:
        # Might just be duplicate, so already there
        if 'Duplicate' not in str(err):
            # It is not a duplicate, so real problem, so re-raise
            raise


def create_multiple_x(qs, instantiator, type_info):
    for row in qs:
        try:
            output = instantiator(row)
            yield output
        except Exception as err:
            errors.append((
                type_info,
                '-'.join(row) if type(row) is tuple else row.pk,
                err,
            ))


def n_or_all(n, qs):
    count = qs.count()
    if n and n < count:
        return n
    return count


# TODO: put all these functions into their own file (could that be a view?)
def _extract_pubs(joins):
    return {
        p.pub_id: dict(
            PMID=int(p.pubmed_id), type=p.pub_type, ISBN=p.isbn,
            volume=p.volume, issue=p.issue, year=int(p.year), title=p.title,
            URL=p.url, raw_pages=p.rawpages, medline_journal=p.medline_journal,
            ISO_journal=p.iso_journal, authors=p.authors, DOI_URL=p.doi_url
        )
        for p in [j.pub for j in joins]
    }


def _extract_member_db(acc):
    output = {}
    methods = iprel.Entry2Method.objects.using("interpro_ro").filter(
        entry_ac=acc
    ).all()
    for method in methods:
        db = method.method_ac.dbcode.dbshort
        ac_id = method.method_ac_id
        if db in output:
            output[db].append(ac_id)
        else:
            output[db] = [ac_id]
    return output


def _extract_integration(member_db_entry):
    try:
        return Entry.objects.get(pk=member_db_entry.entry2method.entry_ac_id)
    except iprel.Entry2Method.DoesNotExist:
        pass


def _extract_go(joins):
    return [join.go_id for join in joins]


def _get_tax_name_from_id(acc):
    try:
        return iprel.TaxNameToId.objects.using("interpro_ro").get(pk=acc).tax_name
    except iprel.TaxNameToId.DoesNotExist:
        pass


def _get_protein_domain_architecture(acc):
    try:
        return iprel.ProteinIDA.objects.using("interpro_ro").get(pk=acc).ida
        # TODO: here is just getting an IDA id however this needs to get a IDA string
    except iprel.TaxNameToId.DoesNotExist:
        pass


# entries
def get_n_member_db_entries(n):
    qs = iprel.Method.objects.using("interpro_ro").all()
    n = n_or_all(n, qs)
    set_member_db_entries(subset_iterator_from_queryset(qs, n))


def set_member_db_entries(qs):
    for chunk in chunks(create_multiple_x(
        qs,
        create_entry_from_member_db,
        'memberDB entry'
    )):
        bulk_insert(chunk, Entry)

def get_n_interpro_entries(n):
    _preFillTrees()
    qs = queryset_from_model(iprel.Entry)
    n = n_or_all(n, qs)
    set_interpro_entries(subset_iterator_from_queryset(qs, n))


def set_interpro_entries(qs):
    for chunk in chunks(create_multiple_x(
        qs,
        create_entry_from_interpro,
        'interpro entry'
    )):
        bulk_insert(chunk, Entry)


def create_entry_from_member_db(row):
    return Entry(
        accession=row.method_ac,
        entry_id="",    # TODO
        type=row.sig_type.abbrev,
        go_terms={},    # TODO
        source_database=row.dbcode.dbshort,
        member_databases={},
        integrated=_extract_integration(row),
        name=row.description,
        short_name=row.name,
        other_names=[],    # TODO
        description=[row.abstract] if row.abstract else [],
        literature=_extract_pubs(row.method2pub_set.all()),
    )


def create_entry_from_interpro(row):
    # [members_dbs, member_db_accs] = _extract_member_db(input.entry_ac)
    return Entry(
        accession=row.entry_ac,
        entry_id="",  # TODO
        type=row.entry_type.abbrev,
        go_terms=_extract_go(row.interpro2go_set.all()),
        source_database="InterPro",
        member_databases=_extract_member_db(row.entry_ac),
        integrated=None,
        name=row.name,
        short_name=row.short_name,
        other_names=[],  # TODO
        description=[join.ann.text for join in row.entry2common_set.all()],
        literature=_extract_pubs(row.entry2pub_set.all()),
        hierarchy=json.dumps(nodes[roots[row.entry_ac]]) if row.entry_ac in roots and roots[row.entry_ac] is not None else None
    )


# proteins
def get_n_proteins(n):
    qs = queryset_from_model(iprel.Protein)
    n = n_or_all(n, qs)
    # This will be likely to break before completion, so enable resumable
    # Count n existing, skip n, then starts filling
    n_skip = Protein.objects.count()
    set_proteins(subset_iterator_from_queryset(qs, n, n_skip))


def set_proteins(qs):
    for chunk in chunks(create_multiple_x(
        qs,
        create_protein_from_protein,
        'protein'
    )):
        bulk_insert(chunk, Protein)


def create_protein_from_protein(row):
    tax_name = _get_tax_name_from_id(row.tax_id)
    tax = {"taxid": row.tax_id}
    if tax_name:
        tax["name"] = tax_name
    return Protein(
        accession=row.protein_ac,
        identifier=row.name,
        organism=tax,
        name="",  # TODO
        short_name="",  # TODO
        other_names=[],  # TODO
        description=[],  # TODO
        sequence="",  # TODO
        length=row.len,
        proteome="",  # TODO
        gene="",  # TODO
        go_terms={},  # TODO
        evidence_code=0,  # TODO
        feature={},  # TODO
        # structure={},  # TODO
        genomic_context={},  # TODO
        source_database=row.dbcode.dbshort,
        domain_architectures = _get_protein_domain_architecture(row.protein_ac)
    )


# structures
def get_n_structures(n):
    qs = queryset_from_model(iprel.UniprotPdbe).values_list(
        "entry_id", flat=True
    ).distinct()
    n = n_or_all(n, qs)
    set_structures(subset_iterator_from_queryset(qs, n))


def set_structures(qs):
    for chunk in chunks(create_multiple_x(
        qs,
        create_structure_from_uniprot_pdbe,
        'structure'
    )):
        bulk_insert(chunk, Structure)


def create_structure_from_uniprot_pdbe(acc):
    qsi = queryset_from_model(iprel.UniprotPdbe).filter(entry_id=acc).iterator()
    row = next(qsi)
    output = Structure(
        accession=row.entry_id,
        name=row.title,
        short_name="",
        other_names=[],
        experiment_type=row.method,
        release_date=date.today(),
        authors=[],
        chains=[row.chain],
        source_database='pdb'
    )
    for row in qsi:
        output.chains.append(row.chain)
    return output


def _fillEntries(n):
    print('Step 1 of 2 running')
    # This needs to be done first
    get_n_interpro_entries(n)
    print('Step 2 of 2 running')
    # Because we reference InterPro entries inside member DB entries
    get_n_member_db_entries(n)


def _fillProteins(n):
    print('Step 1 of 1 running')
    get_n_proteins(n)


def _fillStructures(n):
    print('Step 1 of 1 running')
    get_n_structures(n)

_modelFillers = {
    'Entry': _fillEntries,
    'Protein': _fillProteins,
    'Structure': _fillStructures,
}


def fillModelWith(model, n):
    print('Filling table for {}'.format(model))
    _modelFillers[model](n)


nodes = {}
roots = {}


def _updateChildrenRootsOld(p, c):
    global nodes
    nodes[c]["root"] = p
    if nodes[p]["root"] is not None:
        nodes[c]["root"] = nodes[p]["root"]
    for gc in nodes[c]["children"]:
        _updateChildrenRoots(c, gc["ac"])

def _updateChildrenRoots(p, c):
    global nodes, roots
    roots[c] = roots[p]
    for gc in nodes[c]["children"]:
        _updateChildrenRoots(c, gc["accession"])

def _preFillTrees():
    print('Precalculating entry trees')
    global nodes, roots
    nodes = {}
    roots = {}
    for ee in tqdm(iprel.Entry2Entry.objects.using("interpro_ro").all()):
        p = ee.parent_ac.entry_ac
        c = ee.entry_ac.entry_ac
        if p not in nodes:
            nodes[p] = {
                "accession": p,
                "name": ee.parent_ac.name,
                "type": ee.parent_ac.entry_type.abbrev,
                "children": [],
            }
            roots[p] = p
        if c not in nodes:
            nodes[c] = {
                "accession": c,
                "name": ee.entry_ac.name,
                "type": ee.entry_ac.entry_type.abbrev,
                "children": [],
            }
            roots[c] = c
        nodes[p]["children"].append(nodes[c])
        _updateChildrenRoots(p, c)
    for k, v in nodes.items():
        if len(v["children"]) == 0:
            del v["children"]

class Command(BaseCommand):
    help = "populate db"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number", "-n",
            type=int,
            help=(
                "Number of elements of each kind to add to the DW. " +
                "If none specified, will add EVERYTHING to the model"
            )
        )
        parser.add_argument(
            "--model", "-m",
            type=str,
            required=True,
            choices=_modelFillers.keys(),
            help="Name of the model to add to"
        )
        parser.add_argument(
            "--logs", "-l",
            action='store_true',
            help="Activates Django logs"
        )

    def handle(self, *args, **options):
        n = options["number"]
        m = options["model"]
        if not n:
            print('Warning: adding everything in {}'.format(m))
        if not options["logs"]:
            logging.disable(logging.CRITICAL)
        fillModelWith(model=m, n=n)
        if len(errors) <= 1:
            print('There has been {} error:'.format(len(errors)))
        else:
            print('There have been {} errors:'.format(len(errors)))
        for (error_type, accession, error) in errors:
            print(' - Error while adding the {} {} ({})'.format(
                error_type, accession, error
            ))
