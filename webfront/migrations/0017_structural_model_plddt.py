# Generated by Django 3.1.7 on 2021-08-28 10:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webfront', '0016_structural_model_algorithm'),
    ]

    operations = [
        migrations.RenameField(
            model_name='structuralmodel',
            old_name='lddt',
            new_name='plddt',
        ),
    ]