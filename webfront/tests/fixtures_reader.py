import json
import copy

from webfront.search_controller import SearchController
from webfront.views.custom import CustomView


def get_id(*args):
    return "-".join([a for a in args if a is not None])


class FixtureReader:
    entries = {}
    proteins = {}
    structures = {}
    entry_protein_list = []
    protein_structure_list = {}
    search = None

    def __init__(self, fixture_paths):
        for path in fixture_paths:
            with open(path) as data_file:
                data = json.load(data_file)
                self.load_from_json(data)

    def load_from_json(self, data):
        for fixture in data:
            if fixture['model'] == "webfront.Entry":
                self.entries[fixture['fields']["accession"]] = fixture['fields']
            elif fixture['model'] == "webfront.Protein":
                self.proteins[fixture['fields']["accession"]] = fixture['fields']
                self.protein_structure_list[fixture['fields']["accession"]] = []
            elif fixture['model'] == "webfront.Structure":
                self.structures[fixture['fields']["accession"]] = fixture['fields']
            elif fixture['model'] == "webfront.ProteinEntryFeature":
                self.entry_protein_list.append(fixture['fields'])
            elif fixture['model'] == "webfront.ProteinStructureFeature":
                self.protein_structure_list[fixture['fields']["protein"]].append(fixture['fields'])

    def get_fixtures(self):
        to_add = []
        for ep in self.entry_protein_list:
            e = ep["entry"]
            p = ep["protein"]
            obj = {
                "text": e + " " + p,
                "entry_acc": e,
                "entry_type": self.entries[e]["type"],
                "entry_db": SearchController.to_dbcodes(self.entries[e]["source_database"]),
                "integrated": self.entries[e]["integrated"],
                "protein_acc": p,
                "protein_db": SearchController.to_dbcodes(self.proteins[p]["source_database"]),
                "tax_id": self.proteins[p]["organism"]["taxid"],
                "entry_protein_coordinates": json.dumps(ep["coordinates"]),
                # "django_ct": get_model_ct(ProteinEntryFeature),
                # "django_id": 0,
                "id": get_id(e, p)

            }
            if p in self.protein_structure_list:
                for sp in self.protein_structure_list[p]:
                    c = copy.copy(obj)
                    c["structure_acc"] = sp["structure"]
                    c["structure_chain"] = sp["structure"] + " - " + sp["chain"]
                    c["chain"] = sp["chain"]
                    c["id"] = get_id(e, p, sp["structure"], sp["chain"])
                    c["protein_structure_coordinates"] = json.dumps(sp["coordinates"]),
                    to_add.append(c)
            else:
                to_add.append(obj)
        proteins = [p["protein"] for p in self.entry_protein_list]
        for p, chains in self.protein_structure_list.items():
            if p not in proteins:
                for sp in chains:
                    to_add.append({
                        "text": p + " " + sp["structure"],
                        "protein_acc": p,
                        "protein_db": SearchController.to_dbcodes(self.proteins[p]["source_database"]),
                        "tax_id": self.proteins[p]["organism"]["taxid"],
                        # "django_ct": get_model_ct(ProteinEntryFeature),
                        # "django_id": 0,
                        "id": get_id(None, p, sp["structure"], sp["chain"]),
                        "structure_acc": sp["structure"],
                        "structure_chain": sp["structure"] + " - " + sp["chain"],
                        "chain": sp["chain"],
                        "protein_structure_coordinates": json.dumps(sp["coordinates"]),
                    })

        lower = []
        for doc in to_add:
            lower.append({k: v.lower() if type(v) == str else v for k, v in doc.items()})
        return lower

    def add_to_search_engine(self, docs):
        self.search = CustomView.get_search_controller()
        self.search.add(docs)

    def clear_search_engine(self):
        self.search.clear_all_docs()
