import logging
from datetime import date
from itertools import chain, islice
from random import randint
from threading import Thread

from tqdm import tqdm

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from release.models import iprel
from webfront.models import Entry, Protein, Structure, ProteinEntryFeature, ProteinStructureFeature, EntryStructureFeature

# global array
errors = []

# helpers
def chunks(iterable, max=1000):
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, max - 1))

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
    for input in qs:
        try:
            output = instantiator(input)
            yield output
        except Exception as err:
            errors.append((
                type_info,
                '-'.join(input) if type(input) is tuple else input.pk,
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
        id = method.method_ac_id
        if db in output:
            output[db].append(id)
        else:
            output[db] = [id]
    return output

def _extract_integration(member_db_entry):
    try:
        return Entry.objects.get(pk=member_db_entry.entry2method.entry_ac_id)
    except iprel.Entry2Method.DoesNotExist as err:
        pass

def _extract_go(joins):
    output = {
        "biological_process": [],
        "molecular_function": [],
        "cellular_component": [],
    }
    for join in joins:
        # TODO: check which kind of GO they are to assign to the right one
        output['biological_process'].append({
            "id": join.go_id,
            "name": "",# TODO
        })
    return output

def _get_tax_name_from_id(id):
    try:
        return iprel.TaxNameToId.objects.using("interpro_ro").get(pk=id).tax_name
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

def create_entry_from_member_db(input):
    return Entry(
        accession=input.method_ac,
        entry_id="",# TODO
        type=input.sig_type.abbrev,
        go_terms={},# TODO
        source_database=input.dbcode.dbshort,
        member_databases={},
        integrated=_extract_integration(input),
        name=input.description,
        short_name=input.name,
        other_names=[],# TODO
        description=[input.abstract] if input.abstract else [],
        literature=_extract_pubs(input.method2pub_set.all())
    )

def create_entry_from_interpro(input):
    # [members_dbs, member_db_accs] = _extract_member_db(input.entry_ac)
    return Entry(
        accession=input.entry_ac,
        entry_id="",# TODO
        type=input.entry_type.abbrev,
        go_terms=_extract_go(input.interpro2go_set.all()),# TODO
        source_database="InterPro",
        member_databases=_extract_member_db(input.entry_ac),
        integrated=None,
        name=input.name,
        short_name=input.short_name,
        other_names=[],# TODO
        description=[join.ann.text for join in input.entry2common_set.all()],
        literature=_extract_pubs(input.entry2pub_set.all())
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

def create_protein_from_protein(input):
    tax_name = _get_tax_name_from_id(input.tax_id)
    tax = {"taxid": input.tax_id}
    if tax_name:
        tax["name"] = tax_name
    return Protein(
        accession=input.protein_ac,
        identifier=input.name,
        organism=tax,
        name="",# TODO
        short_name="",# TODO
        other_names=[],# TODO
        description=[],# TODO
        sequence="",# TODO
        length=input.len,
        proteome="",# TODO
        gene="",# TODO
        go_terms={},# TODO
        evidence_code=0,# TODO
        feature={},# TODO
        # structure={},# TODO
        genomic_context={},# TODO
        source_database=input.dbcode.dbshort
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

def create_structure_from_uniprot_pdbe(id):
    qsi = queryset_from_model(iprel.UniprotPdbe).filter(entry_id=id).iterator()
    input = next(qsi)
    output = Structure(
        accession=input.entry_id,
        name=input.title,
        short_name="",
        other_names=[],
        experiment_type=input.method,
        release_date=date.today(),
        authors=[],
        chains=[input.chain],
        source_database='pdb'
    )
    for input in qsi:
        output.chains.append(input.chain)
    return output

# protein <-> entry
def get_n_protein_interpro_entry_features(n):
    qs = queryset_from_model(iprel.Supermatch).values_list(
        "protein_ac", "entry_ac"
    ).distinct()
    n = n_or_all(n, qs)
    set_protein_interpro_entry_feature_from_supermatch(
        subset_iterator_from_queryset(qs, n)
    )

def set_protein_interpro_entry_feature_from_supermatch(qs):
    for chunk in chunks(create_multiple_x(
        qs,
        create_protein_interpro_entry_feature_from_supermatch,
        'protein <-> interpro entry'
    )):
        bulk_insert(chunk, ProteinEntryFeature)

def create_protein_interpro_entry_feature_from_supermatch(composite):
    protein_id, entry_id = composite
    qsi = queryset_from_model(iprel.Supermatch).filter(
        protein_ac=protein_id,
        entry_ac=entry_id
    ).values("pos_from", "pos_to").iterator()
    protein = Protein.objects.get(pk=protein_id)
    entry = Entry.objects.get(pk=entry_id)
    input = next(qsi)
    output = ProteinEntryFeature(
        protein=protein,
        entry=entry,
        coordinates=[{
            'protein': [input["pos_from"], input["pos_to"]],
            'entry': [1, input["pos_to"] - input["pos_from"]]
        }]
    )
    for input in qsi:
        output.coordinates.append({
            'protein': [input["pos_from"], input["pos_to"]],
            'entry': [1, input["pos_to"] - input["pos_from"]]
        })
    return output

def get_n_protein_member_db_entry_features(n):
    qs = queryset_from_model(iprel.Match).values_list(
        "protein_ac", "method_ac"
    ).distinct()
    n = n_or_all(n, qs)
    set_protein_member_db_entry_feature_from_match(
        subset_iterator_from_queryset(qs, n)
    )

def set_protein_member_db_entry_feature_from_match(qs):
    for chunk in chunks(create_multiple_x(
        qs,
        create_protein_member_db_entry_feature_from_match,
        'protein <-> member db entry'
    )):
        bulk_insert(chunk, ProteinEntryFeature)

def create_protein_member_db_entry_feature_from_match(composite):
    protein_id, entry_id = composite
    qsi = queryset_from_model(iprel.Match).filter(
        protein_ac=protein_id,
        method_ac=entry_id
    ).values("pos_from", "pos_to").iterator()
    protein = Protein.objects.get(pk=protein_id)
    entry = Entry.objects.get(pk=entry_id)
    input = next(qsi)
    output = ProteinEntryFeature(
        protein=protein,
        entry=entry,
        coordinates=[{
            'protein': [input["pos_from"], input["pos_to"]],
            'entry': [1, input["pos_to"] - input["pos_from"]]
        }]
    )
    for input in qsi:
        output.coordinates.append({
            'protein': [input["pos_from"], input["pos_to"]],
            'entry': [1, input["pos_to"] - input["pos_from"]]
        })
    return output

# protein <-> structure
def get_n_protein_structure_features(n):
    qs = queryset_from_model(iprel.UniprotPdbe).values_list(
        "entry_id", "sptr_ac", "chain"
    ).distinct()
    n = n_or_all(n, qs)
    set_protein_structure_features(subset_iterator_from_queryset(qs, n))

def set_protein_structure_features(qs):
    for chunk in chunks(create_multiple_x(
        qs,
        create_protein_structure_feature_from_uniprot_pdbe,
        'protein <-> structure'
    )):
        bulk_insert(chunk, ProteinStructureFeature)

def create_protein_structure_feature_from_uniprot_pdbe(composite):
    structure_id, protein_id, chain = composite
    qsi = queryset_from_model(iprel.UniprotPdbe).filter(
        entry_id=structure_id,
        sptr_ac=protein_id,
        chain=chain
    ).iterator()
    protein = Protein.objects.get(pk=protein_id)
    structure = Structure.objects.get(pk=structure_id)
    input = next(qsi)
    output = ProteinStructureFeature(
        protein=protein,
        structure=structure,
        chain=input.chain,
        length=input.end_seq,# TODO: change this to correct value
        organism=protein.organism,
        coordinates=[{
            'protein': [1, protein.length],
            'structure': [input.beg_seq, input.end_seq],
        }]
    )
    for input in qsi:
        output.coordinates.append({
            'protein': [1, protein.length],
            'structure': [input.beg_seq, input.end_seq],
        })
        # TODO: *also* change this to correct value
        output.length = max(output.length, input.end_seq)
    return output









# def get_n_entry_structure_features(n):
#     qs = queryset_from_model(iprel.Match)
#     n = n_or_all(n, qs)
#     set_entry_structure_features(subset_iterator_from_queryset(qs, n))

# def set_entry_structure_features(qs):
#     for chunk in chunks(create_multiple_x(
#         qs,
#         create_entry_structure_features_from_match,
#         'entry-structure feature'
#     )):
#         bulk_insert(chunk, ProteinEntryFeature)

# def create_entry_structure_features_from_match(input):
#     pass







# def get_n_protein_entry_features(n):
#     qs = queryset_from_model(iprel.Match)
#     n = n_or_all(n, qs)
#     set_protein_entry_features(subset_iterator_from_queryset(qs, n))

# def set_protein_entry_features(qs):
#     for chunk in chunks(create_multiple_x(
#         qs,
#         create_protein_entry_features_from_match,
#         'protein-netry feature'
#     )):
#         bulk_insert(chunk, ProteinEntryFeature)

# def create_protein_entry_features_from_match(input):
#     protein = Protein.objects.get(pk=input.protein_ac_id)
#     entry = Entry.objects.get(pk=input.method_ac_id)





# def get_n_protein_entry_features(n):
#     for pef in iprel.Match.objects.using("interpro_ro").all()[:n]:
#         try:
#             coordinates = [{"protein": [pef.pos_from, pef.pos_to]}]
#             protein = Protein.objects.get(pk=pef.protein_ac_id)
#             entry = Entry.objects.get(pk=pef.method_ac_id)
#             output = ProteinEntryFeature(
#                 protein=protein,
#                 entry=entry,
#                 coordinates=coordinates
#             )
#             output.save()
#         except Entry.DoesNotExist:
#             pass
#         except Protein.DoesNotExist:
#             pass
#         except Exception as err:
#             errors.append((
#                 'protein <-> entry',
#                 '{} <-> {}'.format(pef.protein_ac_id, pef.method_ac_id),
#                 err
#             ))
#         yield "{} <-> {}, protein <-> entry".format(
#             pef.protein_ac_id, pef.method_ac_id
#         )
#         try:
#             interpro_entry = pef.method_ac.entry2method.entry_ac
#             entry = Entry.objects.get(pk=interpro_entry.entry_ac)
#             output = ProteinEntryFeature(
#                 protein=protein,
#                 entry=entry,
#                 coordinates=coordinates,
#             )
#             output.save()
#             yield "{} <-> {}, protein <-> entry".format(
#                 pef.protein_ac_id, interpro_entry.entry_ac
#             )
#         except iprel.Entry2Method.DoesNotExist:
#             pass
#         except Entry.DoesNotExist:
#             pass
#         except Exception as err:
#             errors.append((
#                 'protein <-> entry',
#                 '{} <-> {}'.format(pef.protein_ac_id, interpro_entry.entry_ac),
#                 err
#             ))

# def get_all_protein_structure_features(n):
#     s_qs = Structure.objects.all()
#     for p in Protein.objects.all():
#         for s in s_qs:
#             for psf in iprel.UniprotPdbe.objects.using(
#                 "interpro_ro"
#             ).filter(entry_id=s.pk, sptr_ac=p.pk).all():
#                 try:
#                     protein = Protein.objects.get(pk=psf.sptr_ac)
#                     structure = Structure.objects.get(pk=psf.entry_id)
#                     output = ProteinStructureFeature(
#                         protein=protein,
#                         structure=structure,
#                         chain=psf.chain,
#                         length=(psf.end_seq - psf.beg_seq),
#                         organism={},
#                         coordinates=[{
#                             'protein': [psf.beg_seq, psf.end_seq],
#                             'structure': [1, psf.end_seq - psf.beg_seq],
#                         }]
#                     )
#                     output.save()
#                     yield "{} <-> {}, protein <-> structure".format(
#                         psf.sptr_ac_id, psf.entry_id
#                     )
#                 except Protein.DoesNotExist:
#                     pass
#                 except Structure.DoesNotExist:
#                     pass
#                 except Exception as err:
#                     errors.append((
#                         'protein <-> structure',
#                         '{} <-> {}'.format(psf.sptr_ac_id, psf.entry_id),
#                         err
#                     ))

def get_n_entry_structure_features(n):
    pass

# def set_member_db_entry(input, integrated=None):
#     acc = input.method_ac
#     try:
#         output = Entry(
#             accession=acc,
#             entry_id="",# TODO
#             type=input.sig_type.abbrev,
#             go_terms={},# TODO
#             source_database=input.dbcode.dbshort,
#             member_databases={},
#             integrated=integrated,
#             name=input.description,
#             short_name=input.name,
#             other_names=[],# TODO
#             description=[input.abstract] if input.abstract else [],
#             literature=_extract_pubs(input.method2pub_set.all())
#         )
#         output.save()
#     except Exception as err:
#         errors.append(('entry', acc, err))
#     # already_added_proteins = dict()
#     # for match in input.match_set.all():
#     #     if len(already_added_proteins) > 0:
#     #         break
#     #     protein_id = match.protein_ac_id
#     #     protein = already_added_proteins.get(protein_id, None)
#     #     if not protein:
#     #         protein = set_protein(match.protein_ac)
#     #         yield "{}, protein".format(protein_id)
#     #         already_added_proteins[protein_id] = protein
#     #     pef = set_protein_entry_feature(protein, output, match)
#     #     yield "{}<->{}, protein/entry feature".format(
#     #         pef.protein.identifier, pef.entry.accession
#     #     )
#     # if integrated:
#     #     for protein in already_added_proteins.values():
#     #         pef = set_protein_entry_feature(protein, integrated)
#     #         yield "{}<->{}, protein/entry feature".format(
#     #             pef.protein.identifier, pef.entry.accession
#     #         )
#     yield acc

# def set_protein_entry_feature(protein, entry, feat = None):
#     pef = ProteinEntryFeature(
#         protein=protein,
#         entry=entry,
#         match_start=feat.pos_from if feat else None,
#         match_end=feat.pos_to if feat else None
#     )
#     pef.save()
#     return pef






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

def _fillProteinEntryFeatures(n):
    print('Step 1 and 2 of 2 running')
    # t1 = Thread(target=get_n_protein_interpro_entry_features, args=(n, 0))
    # t1.start()
    # t2 = Thread(target=get_n_protein_member_db_entry_features, args=(n, 1))
    # t2.start()
    # t1.join()
    # t2.join()

def _fillProteinInterproEntryFeatures(n):
    print('Step 1 of 1 running')
    get_n_protein_interpro_entry_features(n)

def _fillProteinMemberDBEntryFeatures(n):
    print('Step 1 of 1 running')
    get_n_protein_member_db_entry_features(n)

def _fillProteinStructureFeatures(n):
    print('Step 1 of 1 running')
    get_n_protein_structure_features(n)

def _fillEntryStructureFeatures(n):
    print('Step 1 of 1 running')
    get_n_entry_structure_features(n)

_modelFillers = {
    'Entry': _fillEntries,
    'Protein': _fillProteins,
    'Structure': _fillStructures,
    'ProteinEntry': _fillProteinEntryFeatures,
    'ProteinInterproEntry': _fillProteinInterproEntryFeatures,
    'ProteinMemberDBEntry': _fillProteinMemberDBEntryFeatures,
    'ProteinStructure': _fillProteinStructureFeatures,
    'EntryStructure': _fillEntryStructureFeatures,
}

def fillModelWith(model, n):
    print('Filling table for {}'.format(model))
    _modelFillers[model](n)

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
        for (type, accession, error) in errors:
            print(' - Error while adding the {} {} ({})'.format(type, accession, error))
