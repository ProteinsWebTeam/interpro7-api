from unifam.release import oracle, db
from django.conf import settings

_db_info = settings.DATABASES["interpro_ro"]

class Template(db.Template):
    user = "INTERPRO"

class Entry(Template):
    fields = ("ENTRY_AC", "ENTRY_TYPE", "NAME", "SHORT_NAME")
    table = "ENTRY"

class Entry2Pub(Template):
    fields = ("ENTRY_AC", "ORDER_IN", "PUB_ID")
    table = "ENTRY2PUB"

class Citation(Template):
    fields = (
        "PUB_ID", "PUB_TYPE", "PUBMED_ID", "ISBN", "VOLUME", "ISSUE", "YEAR",
        "TITLE", "URL", "RAWPAGES", "MEDLINE_JOURNAL", "ISO_JOURNAL", "AUTHORS",
        "DOI_URL"
    )
    table = "CITATION"


def get_cursor():
    return oracle.get_cursor(
        _db_info["HOST"], _db_info["PORT"], _db_info["NAME"],
        _db_info["USER"], _db_info["PASSWORD"]
    )

def get_entries(n=10):
    entry = Entry();
    cur = get_cursor()
    cur.execute(entry.build_select())
    for row in (entry.tupleToDict(r) for r in cur.fetchmany(n)):
        output = row
        accession = output["ENTRY_AC"]
        entry2pub = Entry2Pub()
        cur = get_cursor()
        cur.execute(
            entry2pub.build_select(["ENTRY_AC = '{}'".format(accession)])
        )
        output["literature"] = {}
        for row in (entry2pub.tupleToDict(r) for r in cur.fetchall()):
            pub_id = row["PUB_ID"]
            citation = Citation()
            cur = get_cursor()
            cur.execute(citation.build_select(["PUB_ID = '{}'".format(pub_id)]))
            for row in (citation.tupleToDict(r) for r in cur.fetchall()):
                output["literature"][pub_id] = dict(
                    PMID=int(row["PUBMED_ID"]), type=row["PUB_TYPE"],
                    ISBN=row["ISBN"], volume=row["VOLUME"], issue=row["ISSUE"],
                    year=int(row["YEAR"]), title=row["TITLE"], URL=row["URL"],
                    rawPages=row["RAWPAGES"],
                    medlineJournal=row["MEDLINE_JOURNAL"],
                    ISOJournal=row["ISO_JOURNAL"], authors=row["AUTHORS"],
                    DOI_URL=row["DOI_URL"]
                )
        yield output
