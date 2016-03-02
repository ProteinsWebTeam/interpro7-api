from functools import reduce


class Template:
    fields = ()
    user = None
    table = None

    def __init__(self):
        self.lut = {}
        for index, field in enumerate(self.fields):
            self.lut[field] = index

    def query_fields(self):
        return ", ".join(self.fields)

    def getValueForField(self, values, name):
        return values[lut[name]]

    def tupleToDict(self, values):
        d = {}
        for field, value in zip(self.fields, values):
            d[field] = value
        return d

    def build_select(self, conditions=None):
        query = "SELECT {} FROM ".format(", ".join(self.fields))
        if self.user:
            query += "{}.".format(self.user)
        query += "{} ".format(self.table)
        if conditions:
            query += "WHERE {}".format(" AND ".join(conditions))
        print(query)
        return query
