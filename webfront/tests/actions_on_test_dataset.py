from webfront.serializers.content_serializers import ModelContentSerializer

plurals = ModelContentSerializer.plurals
singular = {v: k for k, v in plurals.items()}
for s in plurals.keys():
    singular[s + "_subset"] = s


# value: * all that have the field, None all that don't have the field
def filter_by_value(docs, field, value):
    if value is None:
        return [doc for doc in docs if field not in doc or doc[field] == value]
    return [
        doc
        for doc in docs
        if field in doc
        and ((value == "*" and doc[field] is not None) or doc[field] == value)
    ]


def exclude_by_value(docs, field, value):
    if value is None:
        return [doc for doc in docs if field in doc and doc[field] != value]
    return [doc for doc in docs if field not in doc or doc[field] != value]


def filter_by_contain_value(docs, field, value):
    return [doc for doc in docs if field in doc and value in doc[field]]


def select_fields(docs, fields):
    return [{k: v for k, v in doc.items() if k in fields} for doc in docs]


def unique(docs):
    u = []
    for doc in docs:
        if doc not in u:
            u.append(doc)
    return u


def identity(docs):
    return docs.copy()


def group_by_field_and_count(
    docs, field_to_group_by, field_to_count, force_unique=False
):
    with_field = filter_by_value(docs, field_to_group_by, "*")
    with_field = filter_by_value(with_field, field_to_count, "*")
    group_values = unique(select_fields(with_field, [field_to_group_by]))
    group_values = [d[field_to_group_by] for d in group_values]

    table = (
        unique(select_fields(with_field, [field_to_group_by, field_to_count]))
        if force_unique
        else with_field
    )

    return {
        value: len(filter_by_value(table, field_to_group_by, value))
        for value in group_values
    }


def count_unique(docs, fields):
    select = select_fields(docs, fields)
    u = unique(select)
    return len(u)


def get_field_to_check_for_endpoint(ep):
    if ep == "taxonomy":
        return "tax_id"
    return "{}_acc".format(ep)


def get_db_field(ep):
    if ep in ["structure", "taxonomy", "proteome"]:
        return None
    return "{}_db".format(ep)


def get_acc_field(ep, db=None):
    if ep == "taxonomy":
        return "tax_lineage"
    return "{}_acc".format(ep)


def count_integrated(docs):
    integrated = filter_by_value(docs, "entry_integrated", "*")
    select = select_fields(integrated, ["entry_acc"])
    u = unique(select)
    return len(u)


def count_unintegrated(docs):
    unintegrated = filter_by_value(docs, "entry_integrated", None)
    unintegrated = exclude_by_value(unintegrated, "entry_db", "interpro")
    select = select_fields(unintegrated, ["entry_acc"])
    u = unique(select)
    return len(u)


def count_all(docs):
    select = select_fields(docs, ["entry_acc"])
    u = unique(select)
    return len(u)


def filter_by_db_field(subset, db_field, db):
    if db_field is not None:
        if db_field != "protein_db" or db != "uniprot":
            subset = filter_by_value(subset, db_field, db)
    return subset


def spread_data_per_proteome(docs):
    data = []
    for doc in docs:
        for proteome in doc["proteomes"]:
            new_doc = doc.copy()
            new_doc["proteome_acc"] = proteome
            data.append(new_doc)
    return data


def filter_by_endpoint(docs, ep, db=None, acc=None):
    field = get_field_to_check_for_endpoint(ep)
    subset = docs
    # if ep == 'proteome':
    #     subset = spread_data_per_proteome(docs)
    subset = filter_by_value(subset, field, "*")
    if db is not None:
        subset = filter_by_db_field(subset, get_db_field(ep), db)
        if acc is not None:
            acc = acc if type(acc) != str else acc.lower()
            acc_field = get_acc_field(ep, db)
            if ep in ["taxonomy", "proteome"]:
                subset = filter_by_contain_value(subset, acc_field, acc)
            else:
                subset = filter_by_value(subset, acc_field, acc)
    return subset


def get_entry_counter(data):
    groups = group_by_field_and_count(data, "entry_db", "entry_acc", True)
    return {
        "interpro": groups["interpro"] if "interpro" in groups else 0,
        "integrated": count_integrated(data),
        "unintegrated": count_unintegrated(data),
        "all": count_all(data),
        "member_databases": {k: v for k, v in groups.items() if k != "interpro"},
    }


def extend_entry_counter(counter, data, ep, db):
    extend_entry_db_counter(counter, data, "interpro", ep, db)
    extend_entry_db_counter(counter, data, "integrated", ep, db)
    extend_entry_db_counter(counter, data, "unintegrated", ep, db)
    extend_entry_db_counter(counter, data, "all", ep, db)
    for m in counter["member_databases"]:
        extend_entry_db_counter(counter["member_databases"], data, m, ep, db)


def extend_entry_db_counter(counter, data, member, ep, db):
    if type(counter[member]) == int:
        counter[member] = {"entries": counter[member]}
    field_db = get_db_field(ep)
    field_acc = get_acc_field(ep)
    if member == "integrated":
        just_member = filter_by_value(data, "entry_integrated", "*")
    elif member == "unintegrated":
        just_member = filter_by_value(data, "entry_integrated", None)
        just_member = exclude_by_value(just_member, "entry_db", "interpro")
    elif member == "all":
        just_member = data
    else:
        just_member = filter_by_value(data, "entry_db", member)
    counter[member][plurals[ep]] = count_unique(
        filter_by_db_field(just_member, field_db, db), [field_acc]
    )


def get_protein_counter(data):
    groups = group_by_field_and_count(data, "protein_db", "protein_acc", True)
    groups["uniprot"] = sum(groups.values())
    return groups


def extend_protein_counter(counter, data, ep, db):
    for member in counter:
        if type(counter[member]) == int:
            counter[member] = {"proteins": counter[member]}
        just_member = filter_by_db_field(data, "protein_db", member)
        field_db = get_db_field(ep)
        field_acc = get_acc_field(ep)
        counter[member][plurals[ep]] = count_unique(
            filter_by_db_field(just_member, field_db, db), [field_acc]
        )


def get_structure_counter(data):
    return {"pdb": count_unique(data, ["structure_acc"])}


def extend_structure_counter(counter, data, ep, db):
    if type(counter["pdb"]) == int:
        counter["pdb"] = {"structures": counter["pdb"]}
    field_db = get_db_field(ep)
    field_acc = get_acc_field(ep)
    counter["pdb"][plurals[ep]] = count_unique(
        filter_by_db_field(data, field_db, db), [field_acc]
    )


def get_taxonomy_counter(data):
    return {"uniprot": count_unique(data, ["tax_id"])}


def get_proteome_counter(data):
    return {"uniprot": count_unique(data, ["proteome_acc"])}


def extend_taxonomy_counter(counter, data, ep, db):
    for member in counter:
        if type(counter[member]) == int:
            counter[member] = {"taxa": counter[member]}
        field_db = get_db_field(ep)
        field_acc = get_acc_field(ep)
        counter[member][plurals[ep]] = count_unique(
            filter_by_db_field(data, field_db, db), [field_acc]
        )


def extend_proteome_counter(counter, data, ep, db):
    for member in counter:
        if type(counter[member]) == int:
            counter[member] = {"proteomes": counter[member]}
        field_db = get_db_field(ep)
        field_acc = get_acc_field(ep)
        counter[member][plurals[ep]] = count_unique(
            filter_by_db_field(data, field_db, db), [field_acc]
        )


def get_set_counter(data):
    without_nodes = group_by_field_and_count(data, "set_db", "set_acc", True)
    without_nodes["all"] = sum(without_nodes.values())
    return without_nodes


def extend_set_counter(counter, data, ep, db):
    for member in counter:
        if type(counter[member]) == int:
            counter[member] = {"sets": counter[member]}
        just_member = (
            data if member == "all" else filter_by_db_field(data, "set_db", member)
        )
        field_db = get_db_field(ep)
        field_acc = get_acc_field(ep)
        counter[member][plurals[ep]] = count_unique(
            filter_by_db_field(just_member, field_db, db), [field_acc]
        )


get_endpoint_counter = {
    "entry": get_entry_counter,
    "protein": get_protein_counter,
    "structure": get_structure_counter,
    "taxonomy": get_taxonomy_counter,
    "proteome": get_proteome_counter,
    "set": get_set_counter,
}

extend_counter_with_db = {
    "entry": extend_entry_counter,
    "protein": extend_protein_counter,
    "structure": extend_structure_counter,
    "taxonomy": extend_taxonomy_counter,
    "proteome": extend_proteome_counter,
    "set": extend_set_counter,
}


def get_counter_payload(data, endpoints, dbs=None, accs=None):
    payload = {plurals[ep]: get_endpoint_counter[ep](data) for ep in endpoints}
    # the endpoints that include a db should extend the current counters
    if dbs is not None:
        for i in range(len(dbs)):
            if dbs[i] is None:
                current_ep = endpoints[i]
                for j in range(len(dbs)):
                    if dbs[j] is not None and (accs is None or accs[j] is None):
                        extend_counter_with_db[current_ep](
                            payload[plurals[current_ep]], data, endpoints[j], dbs[j]
                        )
        # remove the unnedded counters
        for j in range(len(dbs)):
            if dbs[j] is not None:
                del payload[plurals[endpoints[j]]]
    return payload


endpoint_attributes = {
    "entry": ["entry_acc", "entry_db", "entry_type", "entry_integrated"],
    "protein": ["protein_acc", "protein_db", "protein_length"],
    "structure": ["structure_acc"],
    "taxonomy": ["tax_id"],
    "proteome": ["proteome_acc"],
    "set": ["set_acc", "set_db"],
}
payload_attributes = {
    "entry": ["accession", "source_database", "type", "integrated"],
    "protein": ["accession", "source_database", "length"],
    "structure": ["accession"],
    "taxonomy": ["accession"],
    "proteome": ["accession"],
    "set": ["accession", "source_database"],
}
sublist_attributes = {
    "entry": ["accession", "source_database", "entry_type", "entry_integrated"],
    "protein": ["accession", "source_database", "protein_length"],
    "structure": ["accession"],
    "taxonomy": ["accession"],
    "proteome": ["accession"],
    "set": ["accession", "source_database"],
}


def get_endpoint_payload(obj, endpoint, db, acc=None, replace_proteome_accession=True):
    attrs = payload_attributes if replace_proteome_accession else sublist_attributes
    payload = {
        attrs[endpoint][i]: obj[endpoint_attributes[endpoint][i]]
        for i in range(len(attrs[endpoint]))
    }
    if acc is not None:
        payload["accession"] = acc
    # if replace_proteome_accession and endpoint == "organism" and db == "proteome":
    #     payload["accession"] = obj["proteomes"][0]
    #     payload["taxonomy"] = obj["tax_id"]
    return payload


def get_payload_list(data, endpoint, db, embed_as_metadata=True, include_chains=False):
    attrs = endpoint_attributes[endpoint].copy()
    if include_chains:
        attrs.append("structure_chain_acc")
    group_values = unique(select_fields(data, attrs))
    payload = [
        get_endpoint_payload(instance, endpoint, db, None, embed_as_metadata)
        for instance in group_values
    ]
    if embed_as_metadata:
        payload = [{"metadata": p} for p in payload]
    return payload


def extend_obj_with_other_endpoints(data, endpoints, dbs, accs, instance, ep):
    for i in range(1, len(endpoints)):
        current_ep = endpoints[i]
        current_db = dbs[i]
        current_acc = None if accs is None else accs[i]
        if current_db is None:
            instance[plurals[current_ep]] = get_endpoint_counter[current_ep](data)
            for j in range(1, len(endpoints)):
                if dbs[j] is not None and (accs is None or accs[j] is None):
                    extend_counter_with_db[current_ep](
                        instance[plurals[current_ep]], data, endpoints[j], dbs[j]
                    )
        else:
            key = plurals[current_ep]
            if current_acc is None:
                key = current_ep + "_subset"
            instance[key] = get_payload_list(
                data,
                current_ep,
                current_db,
                False,
                ep == "structure"
                or current_ep == "structure",  # and current_acc is None
            )[
                :20
            ]  # the API only returns up to 20 items in a sublist
            if current_ep == "entry" and current_acc is None:
                del instance[key]
                key = "entries_url"
                instance[key] = "URL TO BE DEFINED"


def get_db_payload(data, endpoints, dbs, accs=None):
    ep = endpoints[0]
    db = dbs[0]
    payload = get_payload_list(data, ep, db)
    for instance in payload:
        filtered = filter_by_value(
            data, endpoint_attributes[ep][0], instance["metadata"]["accession"]
        )
        extend_obj_with_other_endpoints(filtered, endpoints, dbs, accs, instance, ep)
    return payload


def get_acc_payload(data, endpoints, dbs, accs):
    payload = {
        "metadata": get_endpoint_payload(data[0], endpoints[0], dbs[0], accs[0], True),
        # plurals[endpoints[1]]: get_payload_list(data, endpoints[1], dbs[1], False),
        # plurals[endpoints[2]]: get_payload_list(data, endpoints[2], dbs[2], False),
    }
    extend_obj_with_other_endpoints(data, endpoints, dbs, accs, payload, endpoints[0])
    return payload
