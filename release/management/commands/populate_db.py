from django.core.management.base import BaseCommand

from release.models import iprel
from webfront.models import Entry


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

def get_interpro_entries(n):
    for input in iprel.Entry.objects.using("interpro_ro").all()[:n]:
        output = Entry(
            accession=input.entry_ac, type=input.entry_type_id, name=input.name,
            short_name=input.short_name, other_names=[], member_databases={},
            go_terms={}, literature=[extract_pubs(input.entry2pub_set.all())]
        )
        output.save()

def get_member_db_entries(n):
    for input in iprel.Method.objects.using("interpro_ro").all()[:n]:
        output = Entry(
            accession=input.method_ac, type=input.sig_type_id, name=input.name,
            short_name='', other_names=[], member_databases={},
            go_terms={}, literature=[]
        )
        output.save()

# turn this into a decorator? (not important (at all))
def log(n, kind, source='IPREL'):
    message = '  -> Putting {n} {kind}{plural} from {source}'.format(
        n=n, kind=kind, plural=('s' if n <= 1 else '', source=source)
    )
    print('STARTING')
    print(message)
    return def end():
        print('ENDED')
        print(message)


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
        end = log(n, 'interpro entry object')
        get_interpro_entries(n)
        end()
        end = log(n, 'member db entry object')
        get_member_db_entries(n)
        end()
