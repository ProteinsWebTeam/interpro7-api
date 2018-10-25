class DeletedEntryError(Exception):
    def __init__(self, accession, message):
        self.accession = accession
        self.message = message


class EmptyQuerysetError(Exception):
    def __init__(self, message):
        self.message = message
