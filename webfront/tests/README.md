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
    
    contacts = "[[1,11,0.5], [2,30,0.8], [3,30,0.8]]"  
    contacts_gz = gzip.compress(bytes(contacts,'utf-8'))
    structure = """ATOM      1  N   VAL A   1      -0.701   1.770   1.392  1.00  4.92           N   
    ATOM      2  CA  VAL A   1       0.691   2.052   1.718  1.00  4.92           C   
    ATOM      3  C   VAL A   1       1.384   2.880   0.637  1.00  4.92           C   
    ATOM      4  O   VAL A   1       0.991   2.879  -0.532  1.00  4.92           O   
    """  
    structure_gz = gzip.compress(bytes(structure,'utf-8'))
    model = StructuralModel(model_id=1,accession='PF17176',contacts=contacts_gz,structure=structure_gz)
   
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
                "accession": "PF17176",
                "contacts": "H4sIAOAnHWAC/4uONtQxNNQx0DON1VGINtIxNgCyLUBsYxg7FgCIHLXIJAAAAA==",
                "structure": "H4sIAOcnHWAC/42QMQ7DMAhF95yCCxRhOy54RFnbZIly/6MEcBWpSi2V5X9s/Qe27tsbohLAanLoC7S3Xg9CJvcJmSm0tOxC1s3o/irLT3oB7WbRGxAIn819Rqq5g5MMgMsXsMTBDWgbyRxAEeoDCv8FtNQGvzZsnw2FW3xBLaMnW346Aa6DA5lEAQAA"
            }
        }
    ]

    ```
4. Now you can use the generated JSON to included in one of the fixture files in `webfront/tests/`. 

   In this example the generated fixture is included at the end of `webfront/tests/fixtures_structure.json`.
