# Generated by Django 2.0.9 on 2018-10-31 09:46

from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Database",
            fields=[
                (
                    "name",
                    models.CharField(max_length=100, primary_key=True, serialize=False),
                ),
                ("name_long", models.CharField(max_length=100)),
                ("description", models.TextField(null=True)),
                ("version", models.CharField(max_length=100, null=True)),
                ("release_date", models.DateTimeField(null=True)),
                ("type", models.CharField(max_length=100)),
                ("prev_version", models.CharField(max_length=100, null=True)),
                ("prev_release_date", models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Entry",
            fields=[
                ("entry_id", models.CharField(max_length=10, null=True)),
                (
                    "accession",
                    models.CharField(max_length=25, primary_key=True, serialize=False),
                ),
                ("type", models.CharField(max_length=50)),
                ("name", models.TextField()),
                ("short_name", models.CharField(max_length=100)),
                ("source_database", models.CharField(db_index=True, max_length=100)),
                ("member_databases", jsonfield.fields.JSONField(null=True)),
                ("go_terms", jsonfield.fields.JSONField(null=True)),
                ("description", jsonfield.fields.JSONField(null=True)),
                ("wikipedia", models.TextField(null=True)),
                ("literature", jsonfield.fields.JSONField(null=True)),
                ("hierarchy", jsonfield.fields.JSONField(null=True)),
                ("cross_references", jsonfield.fields.JSONField(null=True)),
                ("entry_date", models.DateTimeField(null=True)),
                ("is_featured", models.BooleanField(default=False)),
                ("overlaps_with", jsonfield.fields.JSONField(default=[])),
                ("is_alive", models.BooleanField(default=False)),
                ("deletion_date", models.DateTimeField(null=True)),
                ("counts", jsonfield.fields.JSONField(null=True)),
                (
                    "integrated",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="webfront.Entry",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EntryAnnotation",
            fields=[
                (
                    "annotation_id",
                    models.CharField(max_length=40, primary_key=True, serialize=False),
                ),
                ("type", models.CharField(max_length=32)),
                ("value", models.BinaryField()),
                ("mime_type", models.CharField(max_length=32)),
                (
                    "accession",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="webfront.Entry",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Protein",
            fields=[
                (
                    "accession",
                    models.CharField(max_length=15, primary_key=True, serialize=False),
                ),
                ("identifier", models.CharField(max_length=16, unique=True)),
                ("organism", jsonfield.fields.JSONField(null=True)),
                ("name", models.CharField(max_length=20)),
                ("other_names", jsonfield.fields.JSONField(null=True)),
                ("description", jsonfield.fields.JSONField(null=True)),
                ("sequence", models.TextField()),
                ("length", models.IntegerField()),
                ("proteome", models.CharField(max_length=20, null=True)),
                ("gene", models.CharField(max_length=70, null=True)),
                ("go_terms", jsonfield.fields.JSONField(null=True)),
                ("evidence_code", models.IntegerField()),
                (
                    "source_database",
                    models.CharField(
                        db_index=True, default="unreviewed", max_length=20
                    ),
                ),
                ("residues", jsonfield.fields.JSONField(null=True)),
                ("extra_features", jsonfield.fields.JSONField(null=True)),
                ("structure", jsonfield.fields.JSONField(default={})),
                ("is_fragment", models.BooleanField(default=False)),
                ("tax_id", models.CharField(default="", max_length=20)),
                ("size", models.CharField(max_length=10, null=True)),
                ("counts", jsonfield.fields.JSONField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Proteome",
            fields=[
                (
                    "accession",
                    models.CharField(max_length=20, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=512)),
                ("is_reference", models.BooleanField(default=False)),
                ("strain", models.CharField(max_length=512)),
                ("assembly", models.CharField(max_length=512)),
                ("counts", jsonfield.fields.JSONField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Release_Note",
            fields=[
                (
                    "version",
                    models.CharField(max_length=20, primary_key=True, serialize=False),
                ),
                ("release_date", models.DateTimeField(null=True)),
                ("content", jsonfield.fields.JSONField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Set",
            fields=[
                (
                    "accession",
                    models.CharField(max_length=20, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=512)),
                ("description", models.TextField()),
                ("source_database", models.CharField(db_index=True, max_length=20)),
                ("integrated", jsonfield.fields.JSONField(null=True)),
                ("relationships", jsonfield.fields.JSONField(null=True)),
                ("is_set", models.BooleanField(default=True)),
                ("counts", jsonfield.fields.JSONField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Structure",
            fields=[
                (
                    "accession",
                    models.CharField(max_length=4, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=512)),
                ("short_name", models.CharField(max_length=20, null=True)),
                ("other_names", jsonfield.fields.JSONField(null=True)),
                ("experiment_type", models.CharField(max_length=16)),
                ("release_date", models.DateTimeField()),
                ("literature", jsonfield.fields.JSONField(null=True)),
                ("chains", jsonfield.fields.JSONField(null=True)),
                (
                    "source_database",
                    models.CharField(db_index=True, default="pdb", max_length=10),
                ),
                ("resolution", models.FloatField(null=True)),
                ("counts", jsonfield.fields.JSONField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Taxonomy",
            fields=[
                (
                    "accession",
                    models.CharField(max_length=20, primary_key=True, serialize=False),
                ),
                ("scientific_name", models.CharField(max_length=255)),
                ("full_name", models.CharField(max_length=512)),
                ("lineage", models.CharField(max_length=512)),
                ("rank", models.CharField(max_length=20)),
                ("children", jsonfield.fields.JSONField(null=True)),
                ("counts", jsonfield.fields.JSONField(null=True)),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="webfront.Taxonomy",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="proteome",
            name="taxonomy",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="webfront.Taxonomy",
            ),
        ),
    ]