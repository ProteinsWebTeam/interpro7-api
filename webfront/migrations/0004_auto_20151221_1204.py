# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webfront', '0003_auto_20151221_1200'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cabshadow',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='cathdom',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='citation',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='comments',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='commonannotation',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='commonannotationaudit',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='createjavalobtable',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='cvdatabase',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='cventrytype',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='cvevidence',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='cvifc',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='cvrank',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='cvrelation',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='cvstatus',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='cvsynonym',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='databasecount',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dbversion',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='dbversionaudit',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='ding',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='domain2family',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='entry',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='entry2common',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='entry2commonaudit',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='entry2comp',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='entry2compaudit',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='entry2entry',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='entry2entryaudit',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='entry2ifc',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='entry2method',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='entry2methodaudit',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='entry2pathway',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='entry2pub',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='entry2pubaudit',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='entryaccpair',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='entryaccpairaudit',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='entryaudit',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='entrycolour',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='entrydeleted',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='entryfriends',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='entryxref',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='entryxrefaudit',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='etaxi',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='example',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='examplearchive',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='exampleaudit',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='exampleauto',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='intactdata',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='intactdatastg',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='interpro2go',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='interpro2goaudit',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='iprscan2dbcode',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='javaclassmd5table',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='javaoptions',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='logdetail',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='logerror',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='logexecution',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='match',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='matchcountindexes',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='matchloadstatus',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='matchnew',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='matchnewstg',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='matchpanther',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='matchpirsf',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='matchstats',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='matchstruct',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='merops',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='meropsnew',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='method',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='method2abstract',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='method2pub',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='method2swissde',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='methodaudit',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='methodstg',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='methodstodeletetemptable',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='modbase',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='modbasetmp',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='mventry2protein',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='mventry2proteintrue',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='mventry2uniparctrue',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='mventrymatch',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='mvmethod2protein',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='mvmethodmatch',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='mvpdb2interpro2go',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='mvpdb2interpro2gobak',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='mvproteinmethodtax',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='mvproteomecount',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='mvsecondary',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='mvtaxentrycount',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='mvuniprot2interpro2go',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='onion2dbcode',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='organism',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pathway2ec',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pdb2pub',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pdbpubadditional',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamclan',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamclandata',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamnested',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='prefilematch',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='prefilemethod',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='profilearchive',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='protein',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='protein2genome',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='proteinaccpair',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='proteinaccpairaudit',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='proteinaccpairnew',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='proteinaccpairnewtmp',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='proteinchanges',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='proteinchangestmp',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='proteinida',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='proteinidaold',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='proteinnew',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='proteinnewtmp',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='proteintaxonomyhierarchydm',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='proteintmp',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='proteintoscan',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='proteintoscantmp',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='proteomerank',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='sanitycheck',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='sanityreport',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='schemaversionlog',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='scopdom',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='shortnamevocab',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='shortnamevocabaudit',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='sproexample',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='sptrunobs',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='structclass',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='supermatch',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='supermatchnew',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='swissmodel',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='taxexamplegroup',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='taxlineage',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='taxnametoid',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='taxonomyload',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='temptaxhierarchy',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='textindexentry',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='tmpdbinnsphobius',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='tmpida',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='tmppfamablackbox',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='tremblexample',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='uniparcprotein',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='uniparcxref',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='uniprotclass',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='uniprotovlap',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='uniprotpdbe',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='uniprotsblob',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='uniprotsdom',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='uniprotstruct',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='uniprotsxref',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='uniprottaxonomy',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='useraccountinfo',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='usersession',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='usersettings',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='varsplicmaster',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='varsplicmatch',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='varsplicnew',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='varsplicsupermatch',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='violatorsentryxref',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='webstatus',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='xrefsummary',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='zeusjobslogs',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='zeussegmentarchived',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='zeussegmentlogs',
            options={'managed': False},
        ),
    ]
