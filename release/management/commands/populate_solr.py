import logging
from itertools import chain, islice

from django.core.management.base import BaseCommand

import cx_Oracle
import pysolr
from tqdm import tqdm

from interpro.settings import HAYSTACK_CONNECTIONS, DATABASES

import time

# global array
errors = []


def get_column_dict_from_cursor(cur):
    return {cur.description[i][0]: i for i in range(len(cur.description))}


def get_object_from_row(row, col):
    return {
        "text": row[col["PROTEIN_AC"]]+" "+row[col["METHOD_AC"]],
        "protein_ac": row[col["PROTEIN_AC"]],
        "method_ac": row[col["METHOD_AC"]],
        "pos_from": row[col["POS_FROM"]],
        "pos_to": row[col["POS_TO"]],
        "status": row[col["STATUS"]],
        "dbcode": row[col["DBCODE"]],
        "evidence": row[col["EVIDENCE"]],
        "seq_date": row[col["SEQ_DATE"]],
        "match_date": row[col["MATCH_DATE"]],
        "timestamp": row[col["TIMESTAMP"]],
        "userstamp": row[col["USERSTAMP"]],
        "score": row[col["SCORE"]]
    }


def chunks(iterable, max=1000):
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, max - 1))


def get_from_db(con, ends):
    cur = con.cursor()
    cur.execute('SELECT * FROM INTERPRO.MATCH WHERE ROWNUM <= {}'.format(ends))
    col = get_column_dict_from_cursor(cur)
    return tqdm(
        (get_object_from_row(row, col) for row in cur),
        initial=0,
        total=ends,
        mininterval=1,
        dynamic_ncols=True,
        position=0
    )


def upload_to_solr(n, bs):
    interpro_ro = DATABASES['interpro_ro']
    t = time.time()
    con = cx_Oracle.connect('{USER}/{PASSWORD}@{HOST}:{PORT}/{NAME}'.format(**interpro_ro))
    solr = pysolr.Solr(HAYSTACK_CONNECTIONS['default']['URL'], timeout=10)
    for chunk in chunks(get_from_db(con, n), bs):
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
        if not bs:
            bs = 1000
        upload_to_solr(n, bs)
