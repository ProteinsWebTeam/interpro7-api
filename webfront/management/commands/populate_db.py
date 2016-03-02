from django.core.management.base import BaseCommand

from unifam.release.iprel import get_entries
from webfront.models import Entry

class Command(BaseCommand):
    args = ""
    help = "populate db"


    def handle(self, *args, **kwargs):
        for data in get_entries(100):
            print("saving {}".format(data))
            accession = data["ENTRY_AC"]
            entry = Entry(
                accession=accession, type=data["ENTRY_TYPE"], name=data["NAME"],
                short_name=data["SHORT_NAME"], other_names=[],
                member_databases={}, go_terms={}, literature=data['literature']
            )
            entry.save()
