from subprocess import check_output
from webfront.models import PfamseqMarkup, PfamaRegFullSignificant

hmmer_path = "/Users/gsalazar/Downloads/hmmer-3.1b2-macosx-intel/binaries/"

class ActiveSites():
    def __init__(self, pfama_acc):
        self.pfama_acc = pfama_acc
        self.proteins = {}

    def load_from_DB(self):
        self.proteins = {}

        residues = PfamseqMarkup.objects.using('pfam_ro').raw("""
            SELECT m.*
            FROM pfamA_reg_full_significant r, pfamseq_markup m, pfamseq s
            WHERE m.pfamseq_acc=r.pfamseq_acc AND m.pfamseq_acc=s.pfamseq_acc AND r.pfamA_acc=%s AND r.in_full=1 AND auto_markup=1""", self.pfama_acc)

        for r in residues:
            if r.pfamseq_acc_id not in self.proteins:
                m = PfamaRegFullSignificant.objects.using('pfam_ro').filter(pfamseq_acc=r.pfamseq_acc,pfama_acc=self.pfama_acc,in_full=1).first()
                self.proteins[r.pfamseq_acc_id] = {
                    "seq_start": m.seq_start,
                    "seq_end": m.seq_end,
                    "ali_start": m.ali_start,
                    "ali_end": m.ali_end,
                    "model_start": m.model_start,
                    "model_end": m.model_end,
                    "residues": []
                }
            self.proteins[r.pfamseq_acc_id]["residues"].append(r.residue)
        print(self.proteins)
        return self.proteins

    def load_alignment(self):
        output = check_output([hmmer_path+ 'esl-sfetch', '-h'])
        print(output)
