__author__ = "gsalazar"
from django.db.backends.signals import connection_created
from django.db import connection
from django.conf import settings

def case_insensitive(a, b):
    return (a.lower() > b.lower()) - (a.lower() < b.lower())

def register_sqlite_collation(sender, connection, **kwargs):
    # Only for SQLite testing
    if connection.vendor == "sqlite":
        connection.connection.create_collation("case_insensitive", case_insensitive)

connection_created.connect(register_sqlite_collation)