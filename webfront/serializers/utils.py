def to_camel_case(snake_case_string):
    parts = snake_case_string.split('_')
    return parts[0] + ''.join(p[0].upper() + p[1:] for p in parts[1:])

def set_or_create_and_set(obj, path, value):
    key = path[0]
    if key in obj:
        if len(path) == 1:
            raise KeyError(
                'Overload of key "{}", please use the corresponding field in the other table'.format(key)
            )
        else:
            set_or_create_and_set(obj[key], path[1:], value)
    else:
        if len(path) == 1:
            obj[key] = value
        else:
            obj[key] = {}
            set_or_create_and_set(obj[key], path[1:], value)


def flat_to_nested(flat, convert_to_camel_case = True):
    nested = {}
    for key, value in flat.items():
        path = key.split('__')
        if convert_to_camel_case:
            path = [to_camel_case(part) for part in path]
        set_or_create_and_set(nested, path, value)
    return nested

def recategorise_go_terms(go_terms):
    for term in go_terms:
        if term['category'] == "F":
            term['category'] = "Molecular Function"
        elif term['category'] == "C":
            term['category'] = "Cellular Component"
        elif term['category'] == "P":
            term['category'] = "Biological Process"
        else:
            raise Exception("Unkown Go Term category '{0}'".format(term['category']))
