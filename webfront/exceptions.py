class DeletedEntryError(Exception):
    def __init__(self, accession, date, message):
        self.accession = accession
        self.message = message
        self.date = date


class EmptyQuerysetError(Exception):
    def __init__(self, message):
        self.message = message


class BadURLParameterError(Exception):
    def __init__(self, message):
        self.message = message
