"""
This script allows to downloads the AlphaFold predictions 
(PDB format) of all UniProt proteins matched by a given 
InterPro entry or member database signature.

Requires python >= 3.6

Example of running command:
$ mkdir outdir
$ python af-entry-dl.py PF05306 outdir
"""

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlencode
from urllib.request import urlopen


def get_uniprot_accessions(source_db, query):
    api_url = "https://www.ebi.ac.uk/interpro/api"
    url = f"{api_url}/protein/UniProt/entry/{source_db}/{query}/?"
    url += urlencode({"with": "alphafold", "page_size": 100})
    accessions = []

    while True:
        with urlopen(url) as res:
            payload = res.read().decode("utf-8")
            obj = json.loads(payload)

            accessions += [r["metadata"]["accession"] for r in obj["results"]]
            
            url = obj.get("next")
            if not url:
                break

    return accessions


def download_af_pdb(accession, outdir):
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{accession}"
    with urlopen(url) as res:
        payload = res.read().decode("utf-8")
        obj = json.loads(payload)
        pdb_url = obj[0]["pdbUrl"]
        
    filename = os.path.basename(pdb_url)
    filepath = os.path.join(outdir, filename)

    with open(filepath, "wb") as fh, urlopen(pdb_url) as res:
        for chunk in res:
            fh.write(chunk)


def main():
    source_db = sys.argv[1]
    query = sys.argv[2]
    outdir = sys.argv[3]

    proteins = get_uniprot_accessions(source_db, query)

    with ThreadPoolExecutor(max_workers=8) as executor:
        fs = {}
        done = 0
        milestone = step = 10
        total = len(proteins)

        while True:
            for accession in proteins:
                f = executor.submit(download_af_pdb, accession, outdir)
                fs[f] = accession

            failed = []
            for f in as_completed(fs):
                accession = fs[f]

                try:
                    f.result()
                except Exception as exc:
                    failed.append(accession)
                    sys.stderr.write(f"error: {exc}\n")
                else:
                    done += 1
                    progress = done / total * 100
                    if progress >= milestone:
                        sys.stderr.write(f"progress: {progress:.0f}%\n")
                        milestone += step

            proteins = failed
            if not proteins:
                break


if __name__ == "__main__":
    main()
