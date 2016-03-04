from django.db import models
from jsonfield import JSONField


class Entry(models.Model):
    entry_id = models.CharField(max_length=10,null=True)
    accession = models.CharField(primary_key=True, max_length=10)
    type = models.CharField(max_length=10)
    name = models.TextField()
    short_name = models.CharField(max_length=12)
    other_names = JSONField()
    source_database = models.CharField(max_length=20)
    member_databases = JSONField()
    integrated = models.ForeignKey("Entry",null=True,blank=True)
    go_terms = JSONField()
    description = models.TextField()
    wikipedia = models.TextField(null=True)
    literature = JSONField()
