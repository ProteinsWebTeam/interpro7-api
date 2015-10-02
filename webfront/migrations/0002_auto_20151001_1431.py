# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webfront', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activesitealignments',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='alignmentandtree',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='architecture',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='clan',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='clanalignmentandrelationship',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='clanarchitecture',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='clandatabaselinks',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='clanlitref',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='clanmembership',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='clanwiki',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='completeproteomes',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='currentpfamversion',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='deadclan',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='deadfamily',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='edits',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='evidence',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='geneontology',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='interpro',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='ligand',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='literaturereference',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='lock',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='markupkey',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='ncbitaxonomy',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='nesteddomains',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='nestedlocations',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='otherreg',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pdb',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pdbimage',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pdbpfamareg',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pdbresiduedata',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfama',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfama2pfamahhsearch',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfama2pfamascoop',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamaarchitecture',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamadatabaselinks',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamafasta',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamahmm',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamainteractions',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamainternal',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamaligand',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamaliteraturereference',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamancbi',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamannseq',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamaregfullinsignificant',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamaregfullsignificant',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamaregseed',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamaspeciestree',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamataxdepth',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamawiki',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamseq',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamseqantifam',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamseqdisulphide',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamseqmarkup',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pfamseqncbi',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='proteomearchitecture',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='proteomepfamseq',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='proteomeregions',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='releasedclanversion',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='releasedpfamversion',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='secondarypfamseqacc',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='seqinfo',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='taxonomy',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='version',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='wikipedia',
            options={'managed': False},
        ),
    ]
