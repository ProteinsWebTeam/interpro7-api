"""
Download matches and other features from InterPro for a given UniProt accession

Requires python >= 3.6

Example of running command:
$ python fetch-protein-matches.py UNIPROT-ACCESSION
"""

import json
import sys
from urllib.error import HTTPError
from urllib.request import urlopen


def main():
    query = sys.argv[1]

    api_url = "https://www.ebi.ac.uk/interpro/api"
    url = f"{api_url}/entry/all/protein/UniProt/{query}/"
    url += "?page_size=200&extra_fields=hierarchy,short_name"

    with urlopen(url) as res:
        data = json.loads(res.read().decode("utf-8"))

    protein_accession = ""
    protein_length = ""
    for i, m in enumerate(data["results"]):
        meta = m["metadata"]
        protein = m["proteins"][0]
        
        if meta["member_databases"]:
            dbs = meta["member_databases"].values()
            signatures = ",".join([sig for db in dbs for sig in db.keys()])
        else:
            signatures = "-"

        if meta["go_terms"]:
            go_terms = ",".join([t["identifier"] for t in meta["go_terms"]])
        else:
            go_terms = "-"

        locations = []
        for l in protein["entry_protein_locations"]:
            for f in l["fragments"]:
                locations.append(f"{f['start']}..{f['end']}")

        if i == 0:
            protein_accession = protein["accession"].upper()
            protein_length = str(protein["protein_length"])

        length = protein["protein_length"]
        print("\t".join([
            meta["accession"],
            meta["name"] or "-",
            meta["source_database"],
            meta["type"],
            meta["integrated"] or "-",
            signatures,
            go_terms,
            protein_accession,
            protein_length,
            ",".join(locations)
        ]))

    url = f"{api_url}/protein/UniProt/{query}/?extra_features=true"
    with urlopen(url) as res:
        features = json.loads(res.read().decode("utf-8"))
        for feature in features.values():

            locations = []
            for l in feature["locations"]:
                for f in l["fragments"]:
                    locations.append(f"{f['start']}..{f['end']}")

            print("\t".join([
                feature["accession"],
                "-",
                feature["source_database"],
                "-",
                "-",
                "-",
                "-",
                protein_accession,
                protein_length,
                ",".join(locations)
            ]))
    

if __name__ == "__main__":
    main()
