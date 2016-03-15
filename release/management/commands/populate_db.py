from django.core.management.base import BaseCommand

from release.models import iprel
from webfront.models import Entry

def log(kind, source="IPREL"):
    def wrapper1(fn):
        def wrapper2(n, *args, **kwargs):
            message = " -> Put {n} {kind}{plural} from {source}".format(
                n=n, kind=kind, plural=("s" if n <= 1 else ""), source=source
            )
            print("STARTING{}".format(message))
            output = fn(n, *args, **kwargs)
            if not hasattr(output, '__iter__'):
                output = [output]
            for [i, step] in enumerate(output, 1):
                print("{:9d}: processed {}".format(i, step))

            print("ENDED{}".format(message))
            return output
        return wrapper2
    return wrapper1

# TODO: put all these functions into their own file (could that be a view?)
def extract_pubs(joins):
    return [
        dict(
            PMID=int(p.pubmed_id), type=p.pub_type, ISBN=p.isbn,
            volume=p.volume, issue=p.issue, year=int(p.year), title=p.title,
            URL=p.url, rawPages=p.rawpages, medlineJournal=p.medline_journal,
            ISOJournal=p.iso_journal, authors=p.authors, DOI_URL=p.doi_url
        )
        for p in [j.pub for j in joins]
    ]

def extract_member_db(acc):
    output = {}
    ids = []
    methods = iprel.Entry2Method.objects.using("interpro_ro").filter(entry_ac=acc).all()
    for method in methods:
        db = method.method_ac.dbcode.dbshort
        id = method.method_ac_id
        ids.append(id)
        if db in output:
            output[db].append(id)
        else:
            output[db] = [id]
    return [output, ids]

def extract_go(joins):
    output = {
        "biologicalProcess": [],
        "molecularFunction": [],
        "cellularComponent": [],
    }
    for join in joins:
        # TODO: check which kind of GO they are to assign to the right one
        output['biologicalProcess'].append({
            "id": join.go_id,
            "name": "",# TODO
        })
    return output

@log("interpro entry objects (and their contributing signatures)")
def get_interpro_entries(n):
    for input in iprel.Entry.objects.using("interpro_ro").all()[:n]:
        acc = input.entry_ac
        [members_dbs, member_db_accs] = extract_member_db(input.entry_ac)
        output = Entry(
            accession=acc,
            entry_id="",# TODO
            type=input.entry_type.abbrev,
            go_terms=extract_go(input.interpro2go_set.all()),# TODO
            source_database="InterPro",
            member_databases=members_dbs,
            integrated=None,
            name=input.name,
            short_name=input.short_name,
            other_names=[],# TODO
            description=[join.ann.text for join in input.entry2common_set.all()],
            literature=extract_pubs(input.entry2pub_set.all())
        )
        output.save()
        yield acc
        for acc in member_db_accs:
            set_member_db_entry(
                iprel.Method.objects.using("interpro_ro").get(pk=acc),
                output
            )
            yield acc

def set_member_db_entry(input, integrated=None):
    acc = input.method_ac
    output = Entry(
        accession=acc,
        entry_id="",# TODO
        type=input.sig_type.abbrev,
        go_terms={},# TODO
        source_database=input.dbcode.dbshort,
        member_databases={},
        integrated=integrated,
        name=input.description,
        short_name=input.name,
        other_names=[],# TODO
        description=[input.abstract] if input.abstract else [],
        literature=[]# TODO
    )
    output.save()
    return acc

@log("unintegrated entry objects")
def get_n_unintegrated_member_db_entries(n):
    for input in iprel.Method.objects.using("interpro_ro").filter(entry2method__isnull=True).all()[:n]:
        yield set_member_db_entry(input)

class Command(BaseCommand):
    help = "populate db"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number", "-n",
            type=int,
            default=10,
            help="Number of elements of each kind to add to the DW"
        )

    def handle(self, *args, **options):
        n = options["number"]
        get_interpro_entries(n)
        get_n_unintegrated_member_db_entries(n)
