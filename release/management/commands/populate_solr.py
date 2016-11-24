import logging
from itertools import chain, islice

from django.core.management.base import BaseCommand

import cx_Oracle
import pysolr
from tqdm import tqdm
from haystack.utils import get_model_ct
from django.utils.encoding import force_text

from interpro.settings import HAYSTACK_CONNECTIONS, DATABASES

import time

# global array
from webfront.models import ProteinEntryFeature

errors = []


def get_column_dict_from_cursor(cur):
    return {cur.description[i][0]: i for i in range(len(cur.description))}


def get_id(*args):
    return "-".join([a for a in args if a is not None])


def get_object_from_row(row, col, is_for_interpro_entries=True):
    return {
        "text": row[col["ENTRY_AC"]]+" "+row[col["PROTEIN_AC"]],
        "entry_acc": row[col["ENTRY_AC"]],
        "entry_type": row[col["ENTRY_TYPE"]],
        "entry_db": "interpro" if is_for_interpro_entries else row[col["ENTRY_DB"]],
        "integrated": None if is_for_interpro_entries else row[col["INTEGRATED"]],
        "protein_acc": row[col["PROTEIN_AC"]],
        "protein_db": row[col["PROTEIN_DB"]],
        "tax_id": row[col["TAX_ID"]],
        "entry_protein_from": row[col["ENTRY_PROTEIN_FROM"]],
        "entry_protein_to": row[col["ENTRY_PROTEIN_TO"]],
        "structure_acc": row[col["STRUCTURE_AC"]],
        "chain": row[col["CHAIN"]],
        "protein_structure_from": row[col["PROTEIN_STRUCTURE_FROM"]],
        "protein_structure_to": row[col["PROTEIN_STRUCTURE_TO"]],

        "django_ct": get_model_ct(ProteinEntryFeature),
        "django_id": 0,
        "id": get_id(row[col["ENTRY_AC"]], row[col["PROTEIN_AC"]], row[col["STRUCTURE_AC"]], row[col["CHAIN"]])
    }


def chunks(iterable, max=1000):
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, max - 1))

query_for_interpro_entries = '''  SELECT
    e.ENTRY_AC, e.ENTRY_TYPE,
    p.PROTEIN_AC, p.DBCODE as PROTEIN_DB, p.TAX_ID,
    pe.POS_FROM as ENTRY_PROTEIN_FROM, pe.POS_TO as ENTRY_PROTEIN_TO,
    ps.ENTRY_ID as STRUCTURE_AC, PS.CHAIN,
    ps.BEG_SEQ as PROTEIN_STRUCTURE_FROM, ps.END_SEQ as PROTEIN_STRUCTURE_TO
  FROM INTERPRO.ENTRY e
    JOIN  INTERPRO.SUPERMATCH pe ON e.ENTRY_AC=pe.ENTRY_AC
    JOIN INTERPRO.PROTEIN p ON p.PROTEIN_AC=pe.PROTEIN_AC
    LEFT JOIN INTERPRO.UNIPROT_PDBE ps ON ps.SPTR_AC=p.PROTEIN_AC
  WHERE ROWNUM <= {} {}'''

query_for_memberdb_entries = '''SELECT
    e.METHOD_AC as ENTRY_AC, e.SIG_TYPE as ENTRY_TYPE, e.DBCODE as ENTRY_DB, em.ENTRY_AC as INTEGRATED,
    p.PROTEIN_AC, p.DBCODE as PROTEIN_DB, p.TAX_ID,
    pe.POS_FROM as ENTRY_PROTEIN_FROM, pe.POS_TO as ENTRY_PROTEIN_TO,
    ps.ENTRY_ID as STRUCTURE_AC, PS.CHAIN,
    ps.BEG_SEQ as PROTEIN_STRUCTURE_FROM, ps.END_SEQ as PROTEIN_STRUCTURE_TO
  FROM INTERPRO.METHOD e
    JOIN  INTERPRO.MATCH pe ON e.METHOD_AC=pe.METHOD_AC
    JOIN INTERPRO.PROTEIN p ON p.PROTEIN_AC=pe.PROTEIN_AC
    LEFT JOIN INTERPRO.ENTRY2METHOD em ON em.METHOD_AC=e.METHOD_AC
    LEFT JOIN INTERPRO.UNIPROT_PDBE ps ON ps.SPTR_AC=pe.PROTEIN_AC
  WHERE ROWNUM <= {} {}'''


def get_from_db(con, ends, where='', is_for_interpro_entries=True):
    cur = con.cursor()
    sql = query_for_interpro_entries if is_for_interpro_entries else query_for_memberdb_entries
    print(sql.format(ends, where))
    cur.execute(sql.format(ends, where))
    col = get_column_dict_from_cursor(cur)
    return tqdm(
        (get_object_from_row(row, col, is_for_interpro_entries) for row in cur),
        initial=0,
        total=ends,
        mininterval=1,
        dynamic_ncols=True,
        position=0
    )

conditions = [
    "",
    "AND e.ENTRY_TYPE='F' AND p.DBCODE='S'",
    "AND e.ENTRY_TYPE='F' AND p.DBCODE='T'",
    "AND e.ENTRY_TYPE!='F' AND p.DBCODE='S'",
    "AND e.ENTRY_TYPE!='F' AND p.DBCODE='T'",
]

dbcodes = ["H", "M", "R", "V", "g", "B", "P", "X", "N", "J", "Y", "U", "D", "Q", "F"]

def upload_to_solr(n, bs, subset=0, is_for_interpro_entries=True):
    t = time.time()
    ipro = DATABASES['interpro_ro']
    con = cx_Oracle.connect(ipro['USER'], ipro['PASSWORD'], cx_Oracle.makedsn(ipro['HOST'], ipro['PORT'], ipro['NAME']))

    solr = pysolr.Solr(HAYSTACK_CONNECTIONS['default']['URL'], timeout=10)
    where = ''
    if is_for_interpro_entries:
        where = conditions[subset]
    elif subset in dbcodes:
        where = "AND e.DBCODE='{}'".format(subset)
    for chunk in chunks(get_from_db(con, n, where, is_for_interpro_entries), bs):
        solr.add(chunk)
    con.close()
    t2 = time.time()
    print("TIME: :", t2-t)


class Command(BaseCommand):
    help = "populate solr"

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
            "--block_size", "-bs",
            type=int,
            help=(
                "Number of elements in a block, which is the number of docs send to solr per connection" +
                "If none specified, will use blocks of 1000"
            )
        )
        parser.add_argument(
            "--query_filter", "-qf",
            type=int,
            default=0,
            help=(
                "Usef the query needs to be partitioned" +
                "\n0: No partition (default)" +
                "\n1: Entry type is Family and proteins are swissprot" +
                "\n2: Entry type is Family and proteins are trembl" +
                "\n3: Entry type is NOT a Family and proteins are swissprot" +
                "\n4: Entry type is NOT a Family and proteins are trembl"
            )
        )
        parser.add_argument(
            "--dbcode", "-db",
            default='',
            help=(
                "When running the loader for member databases, you can partition the query by member DB" +
                " - H: Pfam" +
                " - M: Prosite profiles" +
                " - R: SMART" +
                " - V: PHANTER" +
                " - g: MobiDB" +
                " - B: SFLD" +
                " - P: Prosite patterns" +
                " - X: GENE 3D" +
                " - N: TIGRFAMs" +
                " - J: CDD" +
                " - Y: SUPERFAMILY" +
                " - U: PIRSF" +
                " - D: ProDom" +
                " - Q: HAMAP" +
                " - F: Prints"
        )
        )
        parser.add_argument(
            "--type_of_entry", "-t",
            type=int,
            default=0,
            help=(
                "This loading run in 2 different stages" +
                "\n0: for interpro entries" +
                "\n1: for member databases entries"
            )
        )
        parser.add_argument(
            "--logs", "-l",
            action='store_true',
            help="Activates Django logs"
        )

    def handle(self, *args, **options):
        n = options["number"]
        if not n:
            print('Warning: adding everything in the solr instance')
        if not options["logs"]:
            logging.disable(logging.CRITICAL)
        bs = options["block_size"]
        t = options["type_of_entry"]
        subset = options["query_filter"]
        if not bs:
            bs = 1000
        if options["dbcode"] != '':
            subset = options["dbcode"]
        upload_to_solr(n, bs, subset=subset, is_for_interpro_entries=(t == 0))
