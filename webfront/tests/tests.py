from pathlib import Path
import unittest
import os
from django.test import TestCase
from webfront.active_sites import ActiveSites
from webfront.models.pfam import Clan, Pfama, Pfamseq, MarkupKey, PfamseqMarkup, PfamaRegFullSignificant, PfamaHmm
from django.utils import timezone
from django.core.urlresolvers import resolve
from unifam.settings import TMP_FOLDER, HMMER_PATH, DB_MEMBERS
from webfront.views.member_databases.pfam import home_page


class ImportedModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.c1 = Clan.objects.using('pfam_ro').create(
            clan_acc="CL0587",
            clan_id="CL0587",
            updated=timezone.now())
        cls.c2 = Clan.objects.using('pfam_ro').create(
            clan_acc="CL0588",
            clan_id="CL0588",
            updated=timezone.now())

    @classmethod
    def tearDownClass(cls):
        cls.c1.delete()
        cls.c2.delete()
        super(ImportedModelTest, cls).tearDownClass()

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_saving_clan_in_test_server(self):
        all_clans = Clan.objects.using('pfam_ro').all()
        self.assertEqual(all_clans.count(), 2)
        self.assertEqual(all_clans[0], self.c1)

    def test_home_page_returns_correct_html(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_clans_returns_correct_html(self):
        response = self.client.get('/entry/interpro/all/pfam/clans/')
        self.assertTemplateUsed(response, 'clans.html')

    def test_read_the_unifam_settings_file(self):
        self.assertEqual(TMP_FOLDER, "/tmp/")
        self.assertGreater(len(DB_MEMBERS.items()), 0)


class ActiveSitesTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        pfam1 = Pfama.objects.using('pfam_ro').create(
            pfama_acc="TEST_PFAM_ACC",
            pfama_id="TEST_PFAM_ID",
            updated="2011-09-01T13:20:30+03:00",
            num_full=95
        )
        seq1 = Pfamseq.objects.using('pfam_ro').create(
            pfamseq_acc="TEST_SEQ_ACC_1",
            pfamseq_id="TEST_SEQ_ID_1",
            description="seq1",
            sequence="TTATCT"
        )
        seq2 = Pfamseq.objects.using('pfam_ro').create(
            pfamseq_acc="TEST_SEQ_ACC_2",
            pfamseq_id="TEST_SEQ_ID_2",
            description="seq2",
            sequence="TTATCTAA"
        )
        m1 = MarkupKey.objects.using('pfam_ro').create(label="Active site", auto_markup=1)
        PfamseqMarkup.objects.using('pfam_ro').create(
            pfamseq_acc=seq1,
            auto_markup=m1,
            residue=136,
            annotation="ANNOTATION_1"
        )
        PfamseqMarkup.objects.using('pfam_ro').create(
            pfamseq_acc=seq1,
            auto_markup=m1,
            residue=204,
            annotation="ANNOTATION_2"
        )
        PfamaRegFullSignificant.objects.using('pfam_ro').create(
            pfama_acc=pfam1,
            pfamseq_acc=seq1,
            seq_start=312,
            seq_end=376,
            ali_start=312,
            ali_end=341,
            model_start=1,
            model_end=33,
            in_full=1
        )
        PfamaRegFullSignificant.objects.using('pfam_ro').create(
            pfama_acc=pfam1,
            pfamseq_acc=seq2,
            seq_start=32,
            seq_end=36,
            ali_start=32,
            ali_end=34,
            model_start=1,
            model_end=33,
            in_full=1
        )
        PfamaHmm.objects.using('pfam_ro').create(
            pfama_acc=pfam1,
            hmm="| HMMER3/f [3.1b2 | February 2015]\nNAME  TEST_PFAM_NAME\nACC   TEST_PFAM_ACC"
        )

    def test_load_unknown_id_from_db(self):
        active_sites = ActiveSites("unknownID")
        proteins = active_sites.load_from_db()
        self.assertEqual(0, len(proteins.items()))

    def test_load_from_db(self):
        active_sites = ActiveSites("TEST_PFAM_ACC")
        proteins = active_sites.load_from_db()
        self.assertEqual(1, len(proteins.items()))
        self.assertEqual(312, proteins["TEST_SEQ_ACC_1"]["seq_start"])
        self.assertIn(136, [e["residue"] for e in proteins["TEST_SEQ_ACC_1"]["residues"]])
        self.assertIn(204, [e["residue"] for e in proteins["TEST_SEQ_ACC_1"]["residues"]])

    def test_fasta_creation(self):
        active_sites = ActiveSites("TEST_PFAM_ACC")
        proteins = active_sites.load_from_db()
        file_path = TMP_FOLDER+"tmp.fa"
        active_sites._create_fasta_file(file_path)
        fasta_f = open(file_path, "r")
        fasta = fasta_f.read()
        self.assertIn("TEST_SEQ_ACC_1", fasta)
        self.assertIn(proteins["TEST_SEQ_ACC_1"]["sequence"], fasta)
        fasta_f.close()
        os.remove(file_path)

    def test_hmm_creation(self):
        active_sites = ActiveSites("TEST_PFAM_ACC")
        file_path = TMP_FOLDER+"tmp.hmm"
        active_sites._create_hmm_file(file_path)
        hmm_f = open(file_path, "r")
        hmm = hmm_f.read()
        self.assertIn("TEST_PFAM_ACC", hmm)
        self.assertIn("HMMER", hmm)
        hmm_f.close()
        os.remove(file_path)

    @unittest.skipIf("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true", "Skipping this test on Travis CI.")
    def test_native_execution(self):
        self.assertTrue(Path(HMMER_PATH).exists())
        self.assertTrue(Path(HMMER_PATH+"/hmmalign").is_file())
