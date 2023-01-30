"""
This script generates the list of InterPro entries overlapping with a specified entry.

Requires python >= 3.6


The script requires to download the "match_complete.xml.gz" file for the release of interest from the InterPro ftp
$ wget https://ftp.ebi.ac.uk/pub/databases/interpro/releases/88.0/match_complete.xml.gz

Example of running command:
$ python overlapping-entries.py match_complete.xml.gz > overlapping.tsv

To extract entries overlapping with IPR035979, run:
$ awk -v FS='\t' -v OFS='\t' '($1=="IPR035979") {print $4,$5,$6}' overlapping-entries.tsv > overlapping-with-IPR035979.tsv
"""

import gzip
import re
import sys
from xml.etree import ElementTree


def parse_xml(file):
    regx = re.compile(r"<protein")

    with gzip.open(file, "rt") as fh:
        buffer = ""
        i = -1

        for line in fh:
            buffer += line

            for match in regx.finditer(buffer):
                j = match.start()

                if j > i >= 0:
                    yield ElementTree.fromstring(buffer[i:j])

                i = j

            if i >= 0:
                buffer = buffer[i:]
                i = 0

        j = re.search(r"</interpromatch>", buffer).start()
        yield ElementTree.fromstring(buffer[i:j])


def condense_locations(entries):
    for accession, locations in entries.items():
        condensed = []
        start = end = None

        for s, e in sorted(locations):
            if start is None:
                start = s
                end = e
                continue
            elif e <= end:
                continue
            elif s <= end:
                overlap = min(end, e) - max(start, s) + 1
                shortest = min(end - start, e - s) + 1

                if overlap >= shortest * 0.1:
                    end = e
                    continue

            condensed.append((start, end))
            start, end = s, e

        condensed.append((start, end))
        entries[accession] = condensed


def main():
    file = sys.argv[1]

    entries = {}
    for i, protein in enumerate(parse_xml(file)):
        protein_acc = protein.attrib["id"]
        
        protein_entries = {}
        for match in protein.findall("match"):
            match_acc = match.attrib["id"]
            ipr = match.find("ipr")

            if ipr is None:
                continue

            entry_acc = ipr.attrib["id"]
            if entry_acc not in entries:
                entries[entry_acc] = {
                    "name": ipr.attrib["name"],
                    "type": ipr.attrib["type"],
                    "proteins": 0,
                    "overlaps": {}
                }

            try:
                domains = protein_entries[entry_acc]
            except KeyError:
                domains = protein_entries[entry_acc] = []

            for lcn in match.findall("lcn"):
                domains.append((
                    int(lcn.attrib["start"]), 
                    int(lcn.attrib["end"])
                ))                    

        condense_locations(protein_entries)

        for entry_acc, locations in protein_entries.items():
            entries[entry_acc]["proteins"] += 1
            entry_overlaps = entries[entry_acc]["overlaps"]

            for other_acc, other_locations in protein_entries.items():
                if other_acc >= entry_acc:
                    continue

                try:
                    counts = entry_overlaps[other_acc]
                except KeyError:
                    counts = entry_overlaps[other_acc] = [0, 0]

                flag = 0
                for start1, end1 in locations:
                    length1 = end1 - start1 + 1

                    for start2, end2 in other_locations:
                        length2 = end2 - start2 + 1
                        overlap = min(end1, end2) - max(start1, start2) + 1

                        if not flag & 1 and overlap >= length1 * 0.5:
                            flag |= 1
                            counts[0] += 1

                        if not flag & 2 and overlap >= length2 * 0.5:
                            flag |= 2
                            counts[1] += 1

                    if flag == 3:
                        break

        if (i + 1) % 1e6 == 0:
            sys.stderr.write(f"{i+1:>20,}\n")

    sys.stderr.write(f"{i+1:>20,}\n")

    supfam = "homologous_superfamily"
    types = (supfam, "domain", "family", "repeat")

    for entry_acc, entry in entries.items():
        entry_cnt = entry["proteins"]

        for other_acc, (cnt1, cnt2) in entry["overlaps"].items():
            other_cnt = entries[other_acc]["proteins"]

            coef1 = cnt1 / (entry_cnt + other_cnt - cnt1)
            coef2 = cnt2 / (entry_cnt + other_cnt - cnt2)

            coef = (coef1 + coef2) * 0.5

            cont1 = cnt1 / entry_cnt
            cont2 = cnt2 / other_cnt

            if all(e < 0.75 for e in (coef, cont1, cont2)):
                continue

            type1 = entry["type"].lower()
            type2 = entries[other_acc]["type"].lower()
            if ((type1 == supfam and type2 in types)
                    or (type2 == supfam and type1 in types)):

                print("\t".join((
                    entry_acc,
                    entry["name"],
                    entry["type"],
                    other_acc,
                    entries[other_acc]["name"],
                    entries[other_acc]["type"]
                )))
                print("\t".join((
                    other_acc,
                    entries[other_acc]["name"],
                    entries[other_acc]["type"],                    
                    entry_acc,
                    entry["name"],
                    entry["type"]
                )))


if __name__ == "__main__":
    main()
