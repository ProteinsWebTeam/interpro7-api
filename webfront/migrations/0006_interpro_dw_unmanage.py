# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webfront', '0005_interpro_dw_managed'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dwentry',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dwentrycitation',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dwentrydomainorg',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dwentrygo',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dwentryhierarchy',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dwentryinteraction',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dwentrymethod',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dwentrypathway',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dwentryproteinsmatched',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dwentryrelatedresource',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dwentrysequence',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dwentrysignature',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dwentrystructure',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dwproteinxref',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dwseqstructpred',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dwsequence',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dwsignaturematches',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dwsignatureproteinsmatched',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dwsupermatch',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dwtaxentrycount',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dwxrefpdbe',
            options={'managed': False},
        ),
    ]
