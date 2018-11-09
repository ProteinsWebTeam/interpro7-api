import json

import copy

from webfront.searcher.elastic_controller import ElasticsearchController


def get_id(*args):
    return "-".join([a for a in args if a is not None])


class FixtureReader:
    entries = {}
    proteins = {}
    structures = {}
    entry_protein_list = []
    protein_structure_list = {}
    tax2lineage = {}
    tax2rank = {}
    sets = {}
    proteomes = {}
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
            elif fixture['model'] == "webfront.Taxonomy":
                self.tax2lineage[fixture['fields']["accession"]] = fixture['fields']['lineage'].split()
                self.tax2rank[fixture['fields']["accession"]] = fixture['fields']['rank']
            elif fixture['model'] == "webfront.Proteome":
                self.proteomes[fixture['fields']["accession"]] = fixture['fields']
            elif fixture['model'] == "webfront.Set":
                self.sets[fixture['fields']["accession"]] = fixture['fields']

    def get_entry2set(self):
        e2s = {}
        for s in self.sets:
            for n in self.sets[s]["relationships"]["nodes"]:
                if n["type"] == "entry":
                    db = self.sets[s]["source_database"]
                    integrated = self.sets[s]["integrated"]
                    if integrated is not None:
                        integrated = [x.lower() for x in integrated]
                    # if db == "node":
                    #     db = "kegg"
                    if n["accession"] not in e2s:
                        e2s[n["accession"]] = []
                    e2s[n["accession"]].append({"accession": s,
                                                "source_database": db,
                                                "integrated": integrated})
                    if self.sets[s]["integrated"] is not None:
                        for i in self.sets[s]["integrated"]:
                            e2s[n["accession"]].append({
                                "accession": i,
                                "source_database": db,
                                "integrated": []
                            })
        return e2s

    def get_fixtures(self):
        to_add = []
        entry2set = self.get_entry2set()
        for ep in self.entry_protein_list:
            e = ep["entry"]
            p = ep["protein"]
            proteome = self.proteins[p]["proteome"]
            obj = {
                "entry_acc": e,
                "entry_type": self.entries[e]["type"],
                "entry_db": self.entries[e]["source_database"],
                "entry_integrated": self.entries[e]["integrated"],
                "entry_date": self.entries[e]["entry_date"],
                "text_entry": e + " " + self.entries[e]["type"] + " " + (" ".join(self.entries[e]["description"])),
                "protein_acc": p,
                "protein_db": self.proteins[p]["source_database"],
                "text_protein": p+" "+self.proteins[p]["source_database"]+" "+(" ".join(self.proteins[p]["description"])),
                "tax_id": self.proteins[p]["organism"]["taxId"],
                "tax_name": self.proteins[p]["organism"]["name"],
                "tax_lineage": self.tax2lineage[self.proteins[p]["organism"]["taxId"]],
                "tax_rank": self.tax2rank[self.proteins[p]["organism"]["taxId"]],
                "proteome_acc": proteome,
                "proteome_name": self.proteomes[proteome]["name"],
                "proteome_is_reference": self.proteomes[proteome]["is_reference"],
                "text_proteome": proteome + " " + self.proteomes[proteome]["name"],
                "entry_protein_locations": ep["coordinates"],
                "protein_length": self.proteins[p]["length"],
                "protein_size": self.proteins[p]["size"],
                "id": get_id(e, p)
            }
            obj["text_taxonomy"] = obj["tax_id"] + " " + (" ".join(obj["tax_lineage"]))

            if "ida" in ep:
                obj["ida"] = ep["ida"]
                obj["ida_id"] = ep["ida_id"]

            if p in self.protein_structure_list:
                for sp in self.protein_structure_list[p]:
                    c = copy.copy(obj)
                    c["structure_acc"] = sp["structure"]
                    c["structure_evidence"] = self.structures[sp["structure"]]["experiment_type"]
                    c["structure_resolution"] = self.structures[sp["structure"]]["resolution"]
                    c["structure_date"] = self.structures[sp["structure"]]["release_date"]
                    c["structure_chain"] = sp["structure"] + " - " + sp["chain"]
                    c["structure_chain_acc"] = sp["chain"]
                    c["text_structure"] = c["structure_acc"] + " " + sp["chain"]

                    c["protein_structure_locations"] = sp["coordinates"]
                    if e in entry2set:
                        for e2s in entry2set[e]:
                            c2 = copy.copy(c)
                            c2["set_acc"] = e2s["accession"]
                            c2["set_db"] = e2s["source_database"]
                            c2["set_integrated"] = e2s["integrated"]
                            c2["text_set"] = c2["set_acc"] + " " + c2["set_db"]
                            c2["id"] = get_id(e, p, sp["structure"], sp["chain"], e2s["accession"])
                            to_add.append(c2)
                    else:
                        c["id"] = get_id(e, p, sp["structure"], sp["chain"])
                        to_add.append(c)
            else:
                if e in entry2set:
                    for e2s in entry2set[e]:
                        c2 = copy.copy(obj)
                        c2["id"] = get_id(e, p, e2s["accession"])
                        c2["set_acc"] = e2s["accession"]
                        c2["set_db"] = e2s["source_database"]
                        c2["set_integrated"] = e2s["integrated"]
                        c2["text_set"] = c2["set_acc"] + " " + c2["set_db"]
                        to_add.append(c2)
                else:
                    to_add.append(obj)

        proteins = [p["protein"] for p in self.entry_protein_list]
        for p, chains in self.protein_structure_list.items():
            if p not in proteins:
                for sp in chains:
                    proteome = self.proteins[p]["proteome"]
                    to_add.append({
                        "text": p + " " + sp["structure"],
                        "protein_acc": p,
                        "protein_db": self.proteins[p]["source_database"],
                        "text_protein": p + " " + self.proteins[p]["source_database"] + " " + (" ".join(self.proteins[p]["description"])),
                        "tax_id": self.proteins[p]["organism"]["taxId"],
                        "tax_name": self.proteins[p]["organism"]["name"],
                        "tax_rank": self.tax2rank[self.proteins[p]["organism"]["taxId"]],
                        "tax_lineage": self.tax2lineage[self.proteins[p]["organism"]["taxId"]],
                        "proteome_acc": proteome,
                        "proteome_name": self.proteomes[proteome]["name"],
                        "proteome_is_reference": self.proteomes[proteome]["is_reference"],
                        "protein_length": self.proteins[p]["length"],
                        "protein_size": self.proteins[p]["size"],
                        "id": get_id(None, p, sp["structure"], sp["chain"]),
                        "structure_acc": sp["structure"],
                        "structure_evidence": self.structures[sp["structure"]]["experiment_type"],
                        "structure_resolution": self.structures[sp["structure"]]["resolution"],
                        "structure_date": self.structures[sp["structure"]]["release_date"],
                        "structure_chain": sp["structure"] + " - " + sp["chain"],
                        "structure_chain_acc": sp["chain"],
                        "text_structure": sp["structure"] + " " + sp["chain"],
                        "protein_structure_locations": sp["coordinates"],
                    })
        lower = []
        for doc in to_add:
            lower.append({k: v.lower() if type(v) == str else v for k, v in doc.items()})
        return lower

    def add_to_search_engine(self, docs):
        self.search = ElasticsearchController()
        self.search.add(docs)

    def clear_search_engine(self):
        self.search.clear_all_docs()
