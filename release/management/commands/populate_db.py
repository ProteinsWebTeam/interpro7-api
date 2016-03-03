from django.core.management.base import BaseCommand

from release.iprel import get_entries
from release.models import iprel
from webfront.models import Entry

def extractPubs(joins):
    return [
        dict(
            PMID=int(p.pubmed_id), type=p.pub_type, ISBN=p.isbn,
            volume=p.volume, issue=p.issue, year=int(p.year), title=p.title,
            URL=p.url, rawPages=p.rawpages, medlineJournal=p.medline_journal,
            ISOJournal=p.iso_journal, authors=p.authors, DOI_URL=p.doi_url
        )
        for p in [j.pub for j in joins]
    ]


class Command(BaseCommand):
    help = "populate db"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number", "-n",
            type=int,
            default=10,
            help="Number of elements to add to the DW"
        )

    def handle(self, *args, **options):
        n = options["number"]
        print("Putting {} element{} from IPREL into DW".format(
            n, "" if n <= 1 else "s"
        ))
        for input in iprel.Entry.objects.using("interpro_ro").all()[:n]:
            output = Entry(
                accession=input.entry_ac, type=input.entry_type_id,
                name=input.name, short_name=input.short_name, other_names=[],
                member_databases={}, go_terms={},
                literature=[extractPubs(input.entry2pub_set.all())]
            )
            output.save()
