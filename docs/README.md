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

[https://www.ebi.ac.uk/interpro/beta/api/](https://www.ebi.ac.uk/interpro/beta/api/)

The JSON response from the API, amongst other attributes, includes a list of all supported "endpoints". 


### The main endpoints 
The main data types (entry, protein, structure, set, proteome, taxonomy) are the most important of these endpoints because they determine the type of data which will be returned from a query. The URLs below request some general information about each of the main data types. The response is a list of source databases together with a count of how many entities of that type from that datasource are stored in InterPro.

* [/api/entry](https://www.ebi.ac.uk/interpro/beta/api/entry)
* [/api/protein](https://www.ebi.ac.uk/interpro/beta/api/protein)
* [/api/structure](https://www.ebi.ac.uk/interpro/beta/api/structure)
* [/api/set](https://www.ebi.ac.uk/interpro/beta/api/set)
* [/api/taxonomy](https://www.ebi.ac.uk/interpro/beta/api/taxonomy)
* [/api/proteome](https://www.ebi.ac.uk/interpro/beta/api/proteome)


### End point blocks
Endpoint blocks are the most important aspect of the query. An endpoint block can be composed of up to 3 parts: an endpoint data type (e.g., entry), a source database (e.g., InterPro) and a unique identifier (e.g., IPR00009). The endpoint type is mandatory, while the other two parts are optional.

The presence of the different parts of the main block define the filter and determine the type of response returned by the API. The following rules determine the type response:
• A query that only contains the endpoint type will return a list of aggregated values giving the total counts of all the unique entities, grouped by each data source of that type. For example, a query ‘/protein’ will return a JSON object with the number of proteins in UniProtKB, including the reviewed and unreviewed sections.
• When the query includes a data source, the response is a paginated list of the entities that belong to that source, including some basic information. For example, the entities returned by the query ‘/structure/pdb’ include the name, accession and experiment type for each PDB structure.
• If an accession block is part of the request, the response contains more detailed information about the requested entity. For example, the API response to the query ‘protein/UniProt/P50876’ will be a JSON object containing all the available information for that protein that has been imported into InterPro, including its sequence, description, etc.

The following table shows some examples of end point blocks and how the components determine the response type.

|Query|Response type|Description|
|------|-------|------|
|[/api/entry](https://www.ebi.ac.uk/interpro/beta/api/entry)|List of counts|List of counts of entries in InterPro and member databases|
|[/api/protein](https://www.ebi.ac.uk/interpro/beta/api/protein)|List of counts|List of counts of proteins in UniProtKB and the reviewed and unreviewed subsets|
|[/api/structure](https://www.ebi.ac.uk/interpro/beta/api/structure)|List of counts|List of counts of structures in PDB (PDB is the only source of stucture data)|
|[/api/entry/interpro](https://www.ebi.ac.uk/interpro/beta/api/entry/interpro)|List of entities|List of entries in InterPro|
|[/api/entry/cdd](https://www.ebi.ac.uk/interpro/beta/api/entry/cdd)|List of entities|List of entries in CDD|
|[/api/proteome/uniprot](https://www.ebi.ac.uk/interpro/beta/api/proteome/uniprot)|List of entities|List of proteomes (there is only 1 source of proteomes)|
|[/api/entry/interpro/ipr023411](https://www.ebi.ac.uk/interpro/beta/api/entry/interpro/ipr023411)|Detailed object|Data about InterPro entry IPR023411|
|[/api/entry/pfam/pf06235](https://www.ebi.ac.uk/interpro/beta/api/entry/pfam/pf06235)|Detailed object|Data about Pfam entry pf06235|
|[/api/entry/taxonomy/uniprot/9606](https://www.ebi.ac.uk/interpro/beta/api/taxonomy/uniprot/9606)|Detailed object|Data about Taxonomy ID 9606|

### Filtering data
The first end point block in a request defines the data type which will be returned. Additional end point blocks can be combined to filter the main dataset. This allows combinations of end points to be constructed to limit the data returned by the API.



### Examples

### On-going issues and future work

