import abc
import re
from webfront.views.queryset_manager import escape


class SearchController(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_group_obj_of_field_by_query(self, query, fields, fq=None, rows=0, start=0, inner_field_to_count=None):
        raise NotImplementedError('users must define get_group_obj_of_field_by_query to use this base class')

    def get_number_of_field_by_endpoint(self, endpoint, field, accession, query="*:*"):
        db = field
        fq = None
        if field.startswith("entry"):
            db = "entry_db"
        elif field.startswith("protein"):
            db = "protein_db"
        elif field == "tax_id":
            db = "{}_db".format(endpoint)
        acc = "{}_acc".format(endpoint)
        if endpoint == "organism":
            acc = "lineage"
        if field == "set_acc":
            fq = "!set_integrated:* && !set_db:kegg"
        ngroups = self.get_group_obj_of_field_by_query(
             "{} && {}:* && {}:{}".format(query, db, acc, escape(accession)), field, fq
        )["ngroups"]
        if isinstance(ngroups, dict):
            ngroups = ngroups["value"]
        return ngroups

    @abc.abstractmethod
    def get_chain(self):
        raise NotImplementedError('users must define get_chain to use this base class')

    @abc.abstractmethod
    def get_counter_object(self, endpoint, solr_query=None, extra_counters=[]):
        raise NotImplementedError('users must define get_counter_object to use this base class')

    @abc.abstractmethod
    def get_grouped_object(self, endpoint, field, solr_query=None, extra_counters=[], size=10):
        raise NotImplementedError('users must define get_counter_object to use this base class')

    @abc.abstractmethod
    def get_list_of_endpoint(self, endpoint, solr_query=None, rows=1, start=0):
        raise NotImplementedError('users must define get_list_of_endpoint to use this base class')

    @abc.abstractmethod
    def execute_query(self, query, fq=None, rows=0, start=0):
        raise NotImplementedError('users must define execute_query to use this base class')

    @abc.abstractmethod
    def add(self, docs):
        raise NotImplementedError('users must define execute_query to use this base class')

    @abc.abstractmethod
    def clear_all_docs(self):
        raise NotImplementedError('users must define execute_query to use this base class')

    # TODO: check if we can do that only once when building the data instead, to remove it here
    @staticmethod
    def to_dbcodes(q):
        re.sub(r'pfam', "p", "some pFam ", flags=re.IGNORECASE)

        q = re.sub(r'Pfam', "h", q, flags=re.IGNORECASE)
        q = re.sub(r'Prosite?profiles', "m", q, flags=re.IGNORECASE)
        q = re.sub(r'SMART', "r", q, flags=re.IGNORECASE)
        q = re.sub(r'PHANTER', "v", q, flags=re.IGNORECASE)
        q = re.sub(r'MobiDB', "g", q, flags=re.IGNORECASE)
        q = re.sub(r'SFLD', "b", q, flags=re.IGNORECASE)
        q = re.sub(r'Prosite?patterns', "p", q, flags=re.IGNORECASE)
        q = re.sub(r'GENE 3D', "x", q, flags=re.IGNORECASE)
        q = re.sub(r'TIGRFAMs', "n", q, flags=re.IGNORECASE)
        q = re.sub(r'CDD', "j", q, flags=re.IGNORECASE)
        q = re.sub(r'SUPERFAMILY', "y", q, flags=re.IGNORECASE)
        q = re.sub(r'PIRSF', "u", q, flags=re.IGNORECASE)
        q = re.sub(r'ProDom', "d", q, flags=re.IGNORECASE)
        q = re.sub(r'HAMAP', "q", q, flags=re.IGNORECASE)
        q = re.sub(r'Prints', "f", q, flags=re.IGNORECASE)
        q = re.sub(r'reviewed', "s", q, flags=re.IGNORECASE)
        q = re.sub(r'unreviewed', "t", q, flags=re.IGNORECASE)
        return q
