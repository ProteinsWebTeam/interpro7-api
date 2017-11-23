from django.core.management.base import BaseCommand

import logging
from itertools import chain, islice
from os.path import isdir
from os import mkdir

from interpro.settings import DATABASES
import cx_Oracle
from tqdm import tqdm
import json

dbcode = {
    'interpro': 'I',
    'cdd': 'J',
    'gene_3d': 'X',
    'hamap': 'Q',
    'mobidb': 'g',
    'pfam': 'H',
    'phanter': 'V',
    'pirsf': 'U',
    'prints': 'F',
    'prodom': 'D',
    'prosite_patterns': 'P',
    'prosite_profiles': 'M',
    'sfld': 'B',
    'smart': 'R',
    'superfamily': 'Y',
    'tigrfams': 'N'
}
query_for_interpro_entries = '''SELECT DISTINCT
    e.ENTRY_AC, e.ENTRY_TYPE, e.NAME, e.SHORT_NAME, DBMS_LOB.substr(e.ANNOTATION, 3000) as DESCRIPTION,
    p.PROTEIN_AC, p.DBCODE as PROTEIN_DB, p.TAX_ID, p.LEN as LEN, p_dw.DESCRIPTION as PROTEIN_DESCRIPTION, 
    p_dw.PROTEIN_NAME, p_dw.TAXONOMY_SCIENTIFIC_NAME as TAX_NAME, p_dw.TAXONOMY_FULL_NAME as TAX_FULLNAME,
    ps.ENTRY_ID as STRUCTURE_AC, PS.CHAIN, PS.TITLE, PS.METHOD
  FROM INTERPRODW.DW_ENTRY e
    JOIN  INTERPRODW.UPI_SUPERMATCH_STG pe ON e.ENTRY_AC=pe.ENTRY_AC
    JOIN INTERPRO.PROTEIN p ON p.PROTEIN_AC=pe.PROTEIN_AC
    LEFT JOIN INTERPRODW.DW_PROTEIN_XREF p_dw ON p_dw.PROTEIN_AC=p.PROTEIN_AC
    LEFT JOIN INTERPRO.UNIPROT_PDBE ps ON ps.SPTR_AC=p.PROTEIN_AC
  WHERE ROWNUM <= {} AND {}'''

query_for_memberdb_entries = '''SELECT DISTINCT
    e.METHOD_AC as ENTRY_AC, e.SIG_TYPE as ENTRY_TYPE, e.DBCODE as ENTRY_DB,
    e.NAME, e.DESCRIPTION, e.ABSTRACT as SHORT_NAME,
    em.ENTRY_AC as INTEGRATED,
    p.PROTEIN_AC, p.DBCODE as PROTEIN_DB, p.TAX_ID, p.LEN as LEN, p_dw.DESCRIPTION as PROTEIN_DESCRIPTION,
    p_dw.PROTEIN_NAME, p_dw.TAXONOMY_SCIENTIFIC_NAME as TAX_NAME, p_dw.TAXONOMY_FULL_NAME as TAX_FULLNAME,
    ps.ENTRY_ID as STRUCTURE_AC, PS.CHAIN, PS.TITLE, PS.METHOD
  FROM INTERPRO.METHOD e
    JOIN INTERPRO.MATCH pe ON e.METHOD_AC=pe.METHOD_AC
    JOIN INTERPRO.PROTEIN p ON p.PROTEIN_AC=pe.PROTEIN_AC
    LEFT JOIN INTERPRODW.DW_PROTEIN_XREF p_dw ON p_dw.PROTEIN_AC=p.PROTEIN_AC
    LEFT JOIN INTERPRO.ENTRY2METHOD em ON em.METHOD_AC=e.METHOD_AC
    LEFT JOIN INTERPRO.UNIPROT_PDBE ps ON ps.SPTR_AC=pe.PROTEIN_AC
  WHERE pe.DBCODE=e.DBCODE AND ROWNUM <= {} AND {}'''

def get_id(*args):
    return "-".join([a for a in args if a is not None])

dbcodes = None
entry_types = None

def get_dbcodes(con):
    global dbcodes
    if dbcodes is not None:
        return dbcodes
    cur = con.cursor()
    sql = "SELECT * FROM INTERPRO.CV_DATABASE"
    cur.execute(sql)
    dbcodes = {row[0]: row[3] for row in cur}
    dbcodes["S"] = "reviewed"# Swiss-Prot
    dbcodes["T"] = "unreviewed"# TrEMBL
    return dbcodes


def get_entry_types(con):
    global entry_types
    if entry_types is not None:
        return entry_types
    cur = con.cursor()
    sql = "SELECT * FROM INTERPRO.CV_ENTRY_TYPE"
    cur.execute(sql)
    entry_types = {row[0]: row[1] for row in cur}
    return entry_types


def attach_coordinates(con, obj, protein_length, is_for_interpro_entries):
    cur = con.cursor()
    if is_for_interpro_entries:
        sql = """  SELECT *
                   FROM INTERPRODW.UPI_SUPERMATCH_STG
                   WHERE ENTRY_AC='{}' AND PROTEIN_AC='{}'"""
    else:
        sql = """ SELECT *
                  FROM INTERPRO.MATCH
                  WHERE METHOD_AC='{}' AND PROTEIN_AC='{}'"""

    cur.execute(sql.format(obj["entry_acc"], obj["protein_acc"]))
    col = get_column_dict_from_cursor(cur)
    obj["entry_protein_locations"] = [
        {
            "fragments": [{
                "start": row[col["POS_FROM"]],
                "end":row[col["POS_TO"]]
            }]
        }
        for row in cur
    ]

    # Included in a second array to support discontinuous domains in the future
    # see  https://www.ebi.ac.uk/seqdb/confluence/pages/viewpage.action?pageId=34998332

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
        obj["protein_structure_locations"] = [
            {
                "fragments": [{
                    "start": row[col["BEG_SEQ"]],
                    "end": row[col["END_SEQ"]]
                }]
            }
            for row in cur
        ]
    return attach_ida_data(con, obj)


def attach_ida_data(con, obj):
    cur = con.cursor()
    sql = """  SELECT ida.IDA, ida.IDA_FK
               FROM PROTEIN_IDA_NEW ida
               WHERE PROTEIN_AC='{}'"""\
        .format(obj["protein_acc"])
    try:
        cur.execute(sql)
        col = get_column_dict_from_cursor(cur)
        if cur.rowcount > 0:
            row = cur.fetchone()
            obj["IDA"] = row[col["IDA"]]
            obj["IDA_FK"] = row[col["IDA_FK"]]
    except:
        print(sql)
    return obj


def get_object_from_row(con, row, col, is_for_interpro_entries=True):
    codes = get_dbcodes(con)
    ep = get_entry_types(con)
    entry_db = "interpro" if is_for_interpro_entries else codes[row[col["ENTRY_DB"]]]
    integrated = None if is_for_interpro_entries else row[col["INTEGRATED"]]
    protein_db = codes[row[col["PROTEIN_DB"]]]
    structure = {
        "acc": row[col["STRUCTURE_AC"]] if row[col["STRUCTURE_AC"]] is not None else None,
        "chain": row[col["CHAIN"]] if row[col["CHAIN"]] is not None else None,
        "method": row[col["METHOD"]] if row[col["METHOD"]] is not None else None,
        "title": row[col["TITLE"]] if row[col["TITLE"]] is not None else None,
    }
    obj = attach_coordinates(con, {
        "text_entry":
            str(row[col["ENTRY_AC"]]) + " " +
            str(row[col["ENTRY_TYPE"]]) + " " +
            str(row[col["SHORT_NAME"]]) + " " +
            str(integrated) + " " +
            str(row[col["NAME"]]) + " " +
            str(row[col["TAX_ID"]]) + " " +
            str(row[col["DESCRIPTION"]]) + " " +
            entry_db,
        "text_protein":
            str(row[col["PROTEIN_AC"]]) + " " +
            str(row[col["PROTEIN_DESCRIPTION"]]) + " " +
            str(row[col["PROTEIN_NAME"]]) + " " +
            str(protein_db),
        "text_structure":
            str(structure["acc"]) + " " +
            str(structure["chain"]) + " " +
            str(structure["method"]) + " " +
            str(structure["title"]),
        "text_organism":
            str(row[col["TAX_ID"]]) + " " +
            str(row[col["TAX_NAME"]]) + " " +
            str(row[col["TAX_FULLNAME"]]),
        "entry_acc": row[col["ENTRY_AC"]],
        "entry_type": ep[row[col["ENTRY_TYPE"]]],
        "entry_db": entry_db,
        "integrated": integrated,
        "protein_acc": row[col["PROTEIN_AC"]],
        "protein_db": protein_db,
        "protein_length": row[col["LEN"]],
        "tax_id": row[col["TAX_ID"]],
        "structure_acc": structure["acc"],
        "chain": structure["chain"],
        "structure_chain": structure["acc"] + " - " + structure["chain"] if structure["acc"] is not None else None,
        "id": get_id(row[col["ENTRY_AC"]], row[col["PROTEIN_AC"]], row[col["STRUCTURE_AC"]], row[col["CHAIN"]])
    }, row[col["LEN"]], is_for_interpro_entries)
    return {k: v.lower() if type(v) == str and k not in ['chain', 'id'] else v for k, v in obj.items()}

def get_column_dict_from_cursor(cur):
    return {cur.description[i][0]: i for i in range(len(cur.description))}

def get_from_db(con, ends, where='', is_for_interpro_entries=True):
    cur = con.cursor()
    sql = query_for_interpro_entries if is_for_interpro_entries else query_for_memberdb_entries
    sql = sql.format(ends, where)
    print(sql)
    cur.execute(sql)
    print("-- EXECUTED --")
    col = get_column_dict_from_cursor(cur)
    return tqdm(
        (get_object_from_row(con, row, col, is_for_interpro_entries) for row in cur),
        initial=0,
        total=ends,
        mininterval=1,
        dynamic_ncols=True,
        position=0
    )

def chunks(iterable, max=1000):
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, max - 1))

def oracle2json(interpro_db, protein_db, block_size, match_pos, compare_sym, end):
    ipro = DATABASES['interpro_ro']
    print('connecting to ', ipro['HOST'], ipro['PORT'], ipro['NAME'])
    con = cx_Oracle.connect(
        ipro['USER'], ipro['PASSWORD'],
        cx_Oracle.makedsn(ipro['HOST'], ipro['PORT'], ipro['NAME']) if ipro['PORT'] else ipro['NAME']
    )
    is_for_interpro_entries = interpro_db == "interpro"
    where = []
    if protein_db == "reviewed":
        where.append("p.DBCODE='S'")
    elif protein_db == "unreviewed":
        where.append("p.DBCODE='T'")
    if not is_for_interpro_entries:
        where.append("pe.DBCODE='{}'".format(dbcode[interpro_db]))
    if match_pos is not None:
        where.append("pe.POS_FROM {} {}".format(compare_sym, match_pos))

    try:
        mkdir(interpro_db)
    except FileExistsError:
        if not isdir(interpro_db):
            raise

    part = 0
    for chunk in chunks(get_from_db(con, end, " AND ".join(where), is_for_interpro_entries), block_size):
        f = open("{}/ipro_tst_{}_{}_{:06}{}.json".format(
            interpro_db,  # to save in folder
            interpro_db,
            protein_db,
            part,
            '' if match_pos is None else '_' + str(match_pos)
        ), "w")
        f.write(json.dumps(list(chunk)))
        f.close()
        part += 1


class Command(BaseCommand):
    help = "ippro 2 json"

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
            default=10000,
            help=(
                "Number of elements in a block, which is the number of docs to include in a file" +
                "If none specified, will use blocks of 1000"
            )
        )
        parser.add_argument(
            "--db_code", "-db",
            default='interpro',
            choices=dbcode.keys(),
            help="Database to be process (default to interpro)."

        )
        parser.add_argument(
            "--protein_db", "-pr",
            choices=['reviewed', 'unreviewed', 'uniprot'],
            help="Database to be process (default to uniprot)." +
                 "If none specified, the query will not be filter by POS_FROM"

        )
        parser.add_argument(
            "--match_pos", "-p",
            type=int,
            help=(
                "Filtering the query by an specific start position of the match" +
                "If none specified, the query will not be filter by POS_FROM"
            )
        )
        parser.add_argument(
            "--match_pos_compare", "-c",
            default='=',
            choices=['>', '<', '='],
            help="Database to be process (default to uniprot)." +
                 "If none specified, the query will not be filter by POS_FROM"

        )
        parser.add_argument(
            "--logs", "-l",
            action='store_true',
            help="Activates Django logs"
        )

    def handle(self, *args, **options):
        if not options["logs"]:
            logging.disable(logging.CRITICAL)
        oracle2json(
            end=options["number"],
            interpro_db=options["db_code"],
            protein_db=options["protein_db"],
            block_size=options["block_size"],
            match_pos=options["match_pos"],
            compare_sym=options["match_pos_compare"],
        )
