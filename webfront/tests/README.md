Testing
===

Generating fixtures for gzip BinaryFields
---
This in an example of how to generate the fixtures file for `StructuralModel`. The same approach was used for the sequence in the `Protein` table.

1. Go the djano shell. Make sure you are using the test DB by setting `use_test_db: true` in `interpro.local.yml`. 
   ```shell
   python3 manage.py shell
   ```

2. Manually create the fixture, using `gzip` and `bytes` for the binary fields
    ```python
    import gzip 
    from webfront.models import StructuralModel  
    
    contacts = "[[1,1,1,1,1.0], [1,2,1,2,30,0.5], [1,3,1,4,0.8], [2,2,2,2,1.0], [2,3,2,4,0.9], [3,3,4,4,1.0]]"  
    contacts_gz = gzip.compress(bytes(contacts,'utf-8'))
   
    plddt = '[0.7807835340499878, 0.8842586278915405, 0.8649855852127075]'
    plddt_gz = gzip.compress(bytes(plddt,'utf-8'))
   
    structure = """ATOM      1  N   VAL A   1      -0.701   1.770   1.392  1.00  4.92           N   
    ATOM      1  N   ARG A   1      -0.099   0.648  -0.392  1.00  0.00           N  
    ATOM      2  CA  ARG A   1       1.339   0.488  -0.541  1.00  0.00           C  
    ATOM      3  C   ARG A   1       2.039   1.845  -0.536  1.00  0.00           C  
    ATOM      4  O   ARG A   1       1.712   2.743  -1.333  1.00  0.00           O  
    ATOM      5  CB  ARG A   1       1.666  -0.244  -1.831  1.00  0.00           C  
    ATOM      6  CG  ARG A   1       3.140  -0.516  -2.039  1.00  0.00           C  
    ATOM      7  CD  ARG A   1       3.410  -1.196  -3.331  1.00  0.00           C  
    ATOM      8  NE  ARG A   1       4.824  -1.452  -3.502  1.00  0.00           N  
    ATOM      9  CZ  ARG A   1       5.425  -1.747  -4.668  1.00  0.00           C
    """  
    structure_gz = gzip.compress(bytes(structure,'utf-8'))

    model = StructuralModel(model_id=1, accession='PF18859', algorithm='RoseTTAFold', contacts=contacts_gz,
                            plddt=plddt_gz, structure=structure_gz)
    model.save()
    ```

3. Generate the fixture using the `dumpdata` tool in django:
    ```shell
    python manage.py dumpdata webfront --indent 4
    ```

    ```json
    [
        {
            "model": "webfront.structuralmodel",
            "pk": 1,
            "fields": {
                "accession": "PF18859",
                "algorithm": "RoseTTAFold",
                "contacts": "H4sIAKMfQmEC/4uONtSBQj2DWB0FINdIB4SNDXQM9EwhIsZAERMg1wLENdKBQKh6oEogByRrCeIaA7kmQAiSjQUAU15YL10AAAA=",
                "plddt": "H4sIAKMfQmEC/x3IwQ3AIAwDwFU6AEIm2NiZBXX/NSr1nncxHThbm2B3nPFgJizllNNLhP477EhRrTKs9wMKEasjPAAAAA==",
                "structure": "H4sIAKMfQmEC/43SS27EIAwG4P2cggvEssE8sqR0NJvpRKqqLnr/g9Q2VZUZEgkW4aHw8Zukfm0fzho595Duu95d7VNtC0JGHRPkjNaH1WuHMmPQ8X/T/Zf6KtbP24uI6yoDhMTF5jsR7bkXd6C81eoAaqTQQS4djEwnYHsCgy0MoAc0kKBw7GBIUyA7t7mjhJm8wZnlzEUThxNwewLl+PZ2BKaULJlnNrCEuZJlV7uNYABi7KWSwn9XMAFmWXg/ApnQktGqYJCS5xLKJ3xcR5Ch+F4qR29gxLnfRupoPyMYgX00MLMUsbDcaTlLePkFk6MiNykDAAA="
            }
        }
    ]
    ```

4. Now you can use the generated JSON to included in one of the fixture files in `webfront/tests/`. 

   In this example the generated fixture is included at the end of `webfront/tests/fixtures_structure.json`.
