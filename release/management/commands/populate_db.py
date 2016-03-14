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
    methods = iprel.Entry2Method.objects.using("interpro_ro").filter(entry_ac=acc).all()
    for method in methods:
        db = method.method_ac.dbcode.dbshort
        id = method.method_ac_id
        if db in output:
            output[db].append(id)
        else:
            output[db] = [id]
    return output

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

@log("interpro entry object")
def get_interpro_entries(n):
    for input in iprel.Entry.objects.using("interpro_ro").all()[:n]:
        output = Entry(
            accession=input.entry_ac,
            type=input.entry_type_id,
            name=input.name,
            short_name=input.short_name,
            other_names=[],# TODO
            source_database="InterPro",
            member_databases=extract_member_db(input.entry_ac),
            go_terms=extract_go(input.interpro2go_set.all()),# TODO
            literature=extract_pubs(input.entry2pub_set.all())
        )
        output.save()

@log("member db entry object")
def get_member_db_entries(n):
    for input in iprel.Method.objects.using("interpro_ro").all()[:n]:
        output = Entry(
            accession=input.method_ac,
            type=input.sig_type_id,
            name=input.name,
            short_name="",# TODO
            other_names=[],# TODO
            source_database=input.dbcode.dbshort,
            member_databases={},
            go_terms={},# TODO
            literature=[]# TODO
        )
        output.save()


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
        get_member_db_entries(n)
