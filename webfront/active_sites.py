import os
import subprocess
from django.db import connections
import random
from webfront.models import PfamaHmm
from unifam.settings import TMP_FOLDER,HMMER_PATH


class ActiveSites():
    def __init__(self, pfama_acc):
        self.pfama_acc = pfama_acc
        self.proteins = {}

    def load_from_db(self):
        self.proteins = {}
        cursor = connections['pfam_ro'].cursor()

        cursor.execute("""
            SELECT r.pfamseq_acc, residue, annotation, seq_start, seq_end, model_start, model_end, ali_start, ali_end, sequence
            FROM pfamA_reg_full_significant r, pfamseq_markup m, pfamseq s
            WHERE m.pfamseq_acc=r.pfamseq_acc AND
                  m.pfamseq_acc=s.pfamseq_acc AND
                  r.pfamA_acc=%s AND
                  r.in_full=1 AND
                  auto_markup=1""", [self.pfama_acc])

        for r in cursor:
            if r[0] not in self.proteins: #r[0] => pfamseq_acc
                self.proteins[r[0]] = {
                    "seq_start":   r[3],
                    "seq_end":     r[4],
                    "model_start": r[5],
                    "model_end":   r[6],
                    "ali_start":   r[7],
                    "ali_end":     r[8],
                    "sequence":    str(r[9])[2:-1

                                   ],
                    "residues": []
                }
            r_obj ={
                "residue": r[1], # residue,
                "annotation": r[2] # annotation
            }
            if r_obj not in self.proteins[r[0]]["residues"]:
                self.proteins[r[0]]["residues"].append(r_obj)

        return self.proteins

    def _create_fasta_file(self,path):
        d_file = open(path,"w")
        for acc, values in self.proteins.items():
            d_file.write("> "+acc+"\n")
            d_file.write(values["sequence"]+"\n\n")
        d_file.close()

    def _create_hmm_file(self,path):
        hmm = PfamaHmm.objects.using('pfam_ro').get(pfama_acc=self.pfama_acc)
        hmm_file = open(path,"w")
        hmm_file.write(hmm.hmm)
        hmm_file.close()

    def _reset_alignments(self):
        for acc in self.proteins:
            self.proteins[acc]["alignment"] = ""

    def _read_alignments(self,path):
        self._reset_alignments()
        a_file = open(path,"r")
        for line in a_file:
            if not line.startswith("#") and line.strip()!="":
                acc, aln = line.split()
                self.proteins[acc]["alignment"] += aln

    def load_alignment(self):
        rand = random.randint(1,10000)
        path_fasta = TMP_FOLDER+"fasta"+str(rand)+".txt"
        path_hmm = TMP_FOLDER+"hmm"+str(rand)+".txt"
        path_aln = TMP_FOLDER+"out"+str(rand)+".txt"

        self._create_fasta_file(path_fasta)
        self._create_hmm_file(path_hmm)

        subprocess.run([HMMER_PATH + 'hmmalign', "--outformat", "SELEX", "-o", path_aln, path_hmm, path_fasta])

        self._read_alignments(path_aln)

        os.remove(path_fasta)
        os.remove(path_hmm)
        os.remove(path_aln)
