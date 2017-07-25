import hashlib
import random


class RandomDocumentGenerator:

    entry_dbs = [
        "Pfam",
        "Prosite profiles",
        "SMART",
        "PHANTER",
        "MobiDB",
        "SFLD",
        "Prosite patterns",
        "GENE 3D",
        "TIGRFAMs",
        "CDD",
        "SUPERFAMILY",
        "PIRSF",
        "ProDom",
        "HAMAP",
        "Prints"
    ]
    protein_dbs = ["reviewed", "unreviewed"]
    entry_types = ["family", "domain", "site", "repeat"]

    def __init__(self,
                 number_of_proteins,
                 number_of_interpro_entries,
                 number_of_member_db_entries,
                 number_of_structures,
                 seed=0,
                 number_to_generate=0):
        self.number_of_interpro_entries = number_of_interpro_entries
        self.number_of_member_db_entries = number_of_member_db_entries
        self.number_of_proteins = number_of_proteins
        self.number_of_structures = number_of_structures
        self.seed = seed
        self.number_to_generate = number_to_generate

    def __iter__(self):
        return self

    def __next__(self):
        if self.seed > self.number_to_generate:
            raise StopIteration
        return self.get_document()

    def get_document(self):
        identifier = "document{}".format(self.seed)
        hashed = hashlib.md5(identifier.encode('utf-8')).hexdigest()

        is_interpro = int(hashed[0], 16) % 2 == 0
        entry_db = "interpro"
        integrated = None
        entry_type = self.entry_types[int(hashed[1], 16) % len(self.entry_types)]
        if is_interpro:
            entry_acc = "interpro_{}".format(int(hashed[1:6], 16) % self.number_of_interpro_entries)
        else:
            entry_acc = "entry_{}".format(int(hashed[1:6], 16) % self.number_of_member_db_entries)
            entry_db = self.entry_dbs[int(hashed[6], 16) % len(self.entry_dbs)]
            if int(hashed[7], 16) % 2 == 0:
                integrated = "interpro_{}".format(int(hashed[1:6], 16) % self.number_of_interpro_entries)

        protein_acc = "protein_{}".format(int(hashed[8:16], 16) % self.number_of_proteins)
        protein_db = "reviewed" if int(hashed[8], 16) % 10 > 6 else "unreviewed"
        start = random.randint(1, 100)

        structure_acc = "protein_{}".format(int(hashed[16:20], 16) % self.number_of_structures)
        chain = ["a", "b", "c", "d", "e"][int(hashed[16], 16) % 5]
        start_2 = random.randint(1, 100)
        start_3 = random.randint(1, 100)
        l = random.randint(10, 100)

        doc = {
            "id": identifier,
            "entry_acc": entry_acc,
            "entry_db": entry_db,
            "entry_type": entry_type,
            "integrated": integrated,
            "protein_acc": protein_acc,
            "protein_db": protein_db,
            "tax_id": str(int(hashed[9:12], 16)),
            "entry_protein_coordinates": [{"protein": [start, start + random.randint(10,100)]}],
            "structure_acc": structure_acc,
            "chain": chain,
            "structure_chain": structure_acc + " - " + chain,
            "protein_structure_coordinates": [{
                "structure": [start_2, start_2 + l],
                "protein": [start_3, start_3 + l]
            }],
            "text": entry_acc + " - " + protein_acc + " - " + structure_acc + " - " + chain,
        }
        self.seed += 1
        return doc
