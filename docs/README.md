# InterPro API documentation

This document aims to provide some guidance on how to use the InterPro API. In addition the information given here, 
the [InterPro website](https://www.ebi.ac.uk/interpro/beta) is built upon the API and therefore provides many examples
of how the API is used to fetch different types of data.

## Key concepts

### Main data types
Currently there are six main types of data available through the API.

|Type| Description|Source|
|----|----|----|
|Entry| Predicted functional and structural domains on proteins| InterPro, CATH-Gene3D, CDD, HAMAP, PANTHER, Pfam, PIRSF, PRINTS, ProDom, PROSITE Patterns, PROSITE Profiles, SMART, SFLD, SUPERFAMILY, TIGRFAMs| 
|Protein| Protein sequence| UniProtKB (reviewed and unreviewed)|
|Structure| Macromolecular structures involving proteins| PDB|
|Set| Sets describing relationships between entries|Pfam, CDD|
|Taxonomy| Taxonomic information about proteins|UniProtKB|
|Proteome| Collections of proteins defined from whole genome sequencing of isolate organisms|UniProtKB|

### REST interface
Queries to the API are formatted as URL queries. As a general principle a short query to the API will return general 
data and a specific query will return detailed data. The following example shows the most basic query that can 
be made, '/'.  

https://www.ebi.ac.uk/interpro/beta/api/

The JSON response from the API, amongst other attributes, includes a list of all supported  "endpoints". The main data types 
defined above are the most important of these endpoints because they determine the type of data which will be returned.





### End point blocks



### Return types

### Examples

### On-going issues and future work

