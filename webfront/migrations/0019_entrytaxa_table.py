# Generated by Django 3.2.8 on 2022-03-18 08:03

from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [("webfront", "0018_taxa_modifier")]

    operations = [
        migrations.CreateModel(
            name="EntryTaxa",
            fields=[
                (
                    "accession",
                    models.OneToOneField(
                        db_column="accession",
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="webfront.entry",
                    ),
                ),
                ("tree", jsonfield.fields.JSONField(null=True)),
            ],
            options={"db_table": "webfront_entrytaxa"},
        ),
        migrations.RemoveField(model_name="entry", name="taxa"),
    ]
