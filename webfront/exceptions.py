class DeletedEntryError(Exception):
    def __init__(self, accession, database, _type, name, short_name, history, date):
        self.accession = accession
        self.database = database
        self.type = _type
        self.name = name
        self.short_name = short_name
        self.history = history
        self.date = date


class EmptyQuerysetError(Exception):
    def __init__(self, message):
        self.message = message


class ExpectedUniqueError(Exception):
    def __init__(self, message):
        self.message = message


class HmmerWebError(Exception):
    def __init__(self, message):
        self.message = message


class BadURLParameterError(Exception):
    def __init__(self, message):
        self.message = message


class InvalidOperationRequest(Exception):
    def __init__(self, message):
        self.message = message

class DeprecatedModifier(Exception):
    def __init__(self, message):
        self.message = message
