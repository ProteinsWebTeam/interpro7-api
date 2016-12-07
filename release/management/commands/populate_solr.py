import logging
from itertools import chain, islice

from django.core.management.base import BaseCommand

import cx_Oracle
import pysolr
from tqdm import tqdm
from haystack.utils import get_model_ct
from django.utils.encoding import force_text
import json

from interpro.settings import HAYSTACK_CONNECTIONS, DATABASES

import time

# global array
from webfront.models import ProteinEntryFeature

errors = []


def get_column_dict_from_cursor(cur):
    return {cur.description[i][0]: i for i in range(len(cur.description))}


def get_id(*args):
    return "-".join([a for a in args if a is not None])


def attach_coordinates(con, obj, is_for_interpro_entries):
    cur = con.cursor()
    if is_for_interpro_entries:
        sql = """  SELECT *
                   FROM INTERPRO.SUPERMATCH
                   WHERE ENTRY_AC='{}' AND PROTEIN_AC='{}'"""
    else:
        sql = """ SELECT *
                  FROM INTERPRO.MATCH
                  WHERE METHOD_AC='{}' AND PROTEIN_AC='{}'"""

    cur.execute(sql.format(obj["entry_acc"], obj["protein_acc"]))
    col = get_column_dict_from_cursor(cur)
    obj["entry_protein_coordinates"] = json.dumps(
        [{"protein": [row[col["POS_FROM"]], row[col["POS_TO"]]]} for row in cur]
    )
    return attach_structure_coordinates(con, obj)


def attach_structure_coordinates(con, obj):
    if "structure_acc" in obj and obj["structure_acc"] is not None:
        cur = con.cursor()
        sql = """ SELECT *
                  FROM INTERPRO.UNIPROT_PDBE
                  WHERE ENTRY_ID='{}' AND SPTR_AC='{}' AND CHAIN='{}'"""\
            .format(obj["structure_acc"], obj["protein_acc"], obj["chain"])
        cur.execute(sql)
        col = get_column_dict_from_cursor(cur)
        obj["protein_structure_coordinates"] = json.dumps(
            [{"protein": [row[col["BEG_SEQ"]], row[col["END_SEQ"]]]} for row in cur]
        )

    return obj

def get_object_from_row(con, row, col, is_for_interpro_entries=True):
    return attach_coordinates(con, {
        "text": row[col["ENTRY_AC"]]+" "+row[col["PROTEIN_AC"]],
        "entry_acc": row[col["ENTRY_AC"]].lower(),
        "entry_type": row[col["ENTRY_TYPE"]].lower(),
        "entry_db": "interpro" if is_for_interpro_entries else row[col["ENTRY_DB"]].lower(),
        "integrated": None if is_for_interpro_entries else row[col["INTEGRATED"]].lower(),
        "protein_acc": row[col["PROTEIN_AC"]].lower(),
        "protein_db": row[col["PROTEIN_DB"]].lower(),
        "tax_id": row[col["TAX_ID"]],
        "structure_acc": row[col["STRUCTURE_AC"]].lower() if row[col["STRUCTURE_AC"]] is not None else None,
        "chain": row[col["CHAIN"]].lower() if row[col["CHAIN"]] is not None else None,

        # "django_ct": get_model_ct(ProteinEntryFeature),
        # "django_id": 0,
        "id": get_id(row[col["ENTRY_AC"]], row[col["PROTEIN_AC"]], row[col["STRUCTURE_AC"]], row[col["CHAIN"]])
    }, is_for_interpro_entries)


def chunks(iterable, max=1000):
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, max - 1))

query_for_interpro_entries = '''SELECT DISTINCT
    e.ENTRY_AC, e.ENTRY_TYPE,
    p.PROTEIN_AC, p.DBCODE as PROTEIN_DB, p.TAX_ID,
    ps.ENTRY_ID as STRUCTURE_AC, PS.CHAIN
  FROM INTERPRO.ENTRY e
    JOIN  INTERPRO.SUPERMATCH pe ON e.ENTRY_AC=pe.ENTRY_AC
    JOIN INTERPRO.PROTEIN p ON p.PROTEIN_AC=pe.PROTEIN_AC
    LEFT JOIN INTERPRO.UNIPROT_PDBE ps ON ps.SPTR_AC=p.PROTEIN_AC
  WHERE ROWNUM <= {} {}'''

query_for_memberdb_entries = '''SELECT
    e.METHOD_AC as ENTRY_AC, e.SIG_TYPE as ENTRY_TYPE, e.DBCODE as ENTRY_DB, em.ENTRY_AC as INTEGRATED,
    p.PROTEIN_AC, p.DBCODE as PROTEIN_DB, p.TAX_ID,
    ps.ENTRY_ID as STRUCTURE_AC, PS.CHAIN
  FROM INTERPRO.METHOD e
    JOIN INTERPRO.MATCH pe ON e.METHOD_AC=pe.METHOD_AC
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
        (get_object_from_row(con, row, col, is_for_interpro_entries) for row in cur),
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
    print(ipro)
    con = cx_Oracle.connect(ipro['USER'], ipro['PASSWORD'], cx_Oracle.makedsn(ipro['HOST'], ipro['PORT'], ipro['NAME']))

    solr = pysolr.Solr(HAYSTACK_CONNECTIONS['default']['URL'], timeout=10)
    where = ''
    if is_for_interpro_entries:
        where = conditions[subset]
    elif subset in dbcodes:
        where = "AND e.DBCODE='{}'".format(subset)
    for chunk in chunks(get_from_db(con, n, where, is_for_interpro_entries), bs):
        solr.add(chunk, commit=False)
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
