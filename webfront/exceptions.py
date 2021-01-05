class DeletedEntryError(Exception):
    def __init__(self, accession, date, message, history):
        self.accession = accession
        self.message = message
        self.date = date
        self.history = history


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
