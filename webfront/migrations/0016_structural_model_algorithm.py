# Generated by Django 3.1.7 on 2021-06-24 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webfront', '0015_structural_model_lddt'),
    ]

    operations = [
        migrations.AddField(
            model_name='structuralmodel',
            name='algorithm',
            field=models.CharField(default='trRosetta', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='structuralmodel',
            name='lddt',
            field=models.BinaryField(),
        ),
    ]