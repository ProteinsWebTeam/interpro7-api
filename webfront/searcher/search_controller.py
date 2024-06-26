import abc
import re
from webfront.views.queryset_manager import escape


class SearchController(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_group_obj_of_field_by_query(
        self, query, fields, fq=None, rows=0, inner_field_to_count=None
    ):
        raise NotImplementedError(
            "users must define get_group_obj_of_field_by_query to use this base class"
        )

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
        if endpoint == "taxonomy":
            acc = "tax_lineage"
        elif endpoint == "structure":
            db = "structure_chain_acc"
        elif endpoint == "proteome":
            db = "proteome_acc"
            acc = "proteome_acc"
        ngroups = self.get_group_obj_of_field_by_query(
            "{} && {}:* && {}:{}".format(
                query, db, acc, escape(str(accession).lower())
            ),
            field,
            fq,
        )["ngroups"]
        if isinstance(ngroups, dict):
            ngroups = ngroups["value"]
        return ngroups

    @abc.abstractmethod
    def get_chain(self):
        raise NotImplementedError("users must define get_chain to use this base class")

    @abc.abstractmethod
    def get_counter_object(self, endpoint, query=None, extra_counters=[]):
        raise NotImplementedError(
            "users must define get_counter_object to use this base class"
        )

    @abc.abstractmethod
    def get_grouped_object(
        self, endpoint, field, query=None, extra_counters=[], size=10
    ):
        raise NotImplementedError(
            "users must define get_counter_object to use this base class"
        )

    @abc.abstractmethod
    def get_list_of_endpoint(self, endpoint, query=None, rows=1, start=0):
        raise NotImplementedError(
            "users must define get_list_of_endpoint to use this base class"
        )

    @abc.abstractmethod
    def execute_query(self, query, fq=None, rows=0, start=0):
        raise NotImplementedError(
            "users must define execute_query to use this base class"
        )

    @abc.abstractmethod
    def add(self, docs):
        raise NotImplementedError("users must define add to use this base class")

    @abc.abstractmethod
    def clear_all_docs(self):
        raise NotImplementedError(
            "users must define clear_all_docs to use this base class"
        )
