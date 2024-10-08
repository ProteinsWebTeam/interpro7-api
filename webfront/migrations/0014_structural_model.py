# Generated by Django 3.0.7 on 2021-02-05 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("webfront", "0013_protein_extra")]

    operations = [
        migrations.CreateModel(
            name="StructuralModel",
            fields=[
                ("model_id", models.IntegerField(primary_key=True, serialize=False)),
                ("accession", models.CharField(max_length=25)),
                ("contacts", models.BinaryField()),
                ("structure", models.BinaryField()),
            ],
            options={"db_table": "webfront_structuralmodel"},
        )
    ]
