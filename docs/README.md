# InterPro API documentation

This document aims to provide some guidance on how to use the InterPro API. The query syntax is very flexible 
and enables fetching and filtering of many different kinds of data from the InterPro databases. 
The documentation here defines some key concepts that should help with getting started.

In addition, the to information given here, the [InterPro website](https://www.ebi.ac.uk/interpro/) is built upon the API and therefore provides 
many practical examples of how the API is used to fetch different types of data. 
The [dynamic code snippet generator](https://www.ebi.ac.uk/interpro/result/download/#/entry/InterPro/|accession) is a particularly useful resource for getting at examples of 
how to download InterPro data in Python 3, Perl and Javascript.

## Getting started with some Examples

### How many entries are there in the InterPro API?

This is a good starter query. InterPro integrates  data from all the member databases of the InterPro Consortium and 
contains both the original member database data and data for curated integrated entries. 
The following query returns a list of counts for all the different sources of entries in the InterPro dataset. 
In addition, there are also counts for the number of member database entries 'integrated' into InterPro and counts 
for those still 'unintegrated'.

[/api/entry](https://www.ebi.ac.uk/interpro/api/entry)

### How do I get a list of all CDD entries in the InterPro API?

This query will return a paginateable list of summary information about CDD entries included in our dataset. 
The response returns first 20 hits and contains a link to the next 20 hits. Due to a limitation our databases, 
this list cannot be sorted.

[/api/entry/cdd](https://www.ebi.ac.uk/interpro/api/entry/cdd)

### How many entries matching Human P53 protein in the different data sources (accession P04637)?

This query returns a list of counts of entries linked to P53 in all datasources in InterPro

[/api/entry/protein/uniprot/P04637](https://www.ebi.ac.uk/interpro/api/entry/protein/uniprot/P04637)

### How do I retrieve a list of all InterPro entries found in Human P53 protein (accession P04637)?

This query returns a list of InterPro entries which map to Human P53 protein.

[/api/entry/interpro/protein/uniprot/P04637](https://www.ebi.ac.uk/interpro/api/entry/interpro/protein/uniprot/P04637)

### How do I retrieve a list of UniProtKB reviewed proteins containing the entry IPR002117 domain?

This query returns a list of proteins with IPR002117 domains together with the location of the domain in the protein sequence.

[/api/protein/reviewed/entry/interpro/ipr002117](https://www.ebi.ac.uk/interpro/api/protein/reviewed/entry/interpro/ipr002117)

### How do I retrieve a list of organisms which possess RNA-directed RNA polymerase (IPR026381)?

This query returns a list of organisms which have a protein which contains a match to IPR026381.

[/api/taxonomy/uniprot/entry/interpro/IPR026381](https://www.ebi.ac.uk/interpro/api/taxonomy/uniprot/entry/interpro/IPR026381)

## Key concepts

### Main data types

Currently, there are six main types of data available through the API.

| Type      | Description                                                                       | Source                                                                                                                                 |
|-----------|-----------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| Entry     | Predicted functional and structural domains on proteins                           | InterPro, CATH-Gene3D, CDD, HAMAP, PANTHER, Pfam, PIRSF, PRINTS, PROSITE Patterns, PROSITE Profiles, SMART, SFLD, SUPERFAMILY, NCBIfam |
| Protein   | Protein sequence                                                                  | UniProtKB (reviewed and unreviewed)                                                                                                    |
| Structure | Macromolecular structures involving proteins                                      | PDB                                                                                                                                    |
| Set       | Sets describing relationships between entries                                     | Pfam, CDD, PIRSF                                                                                                                              |
| Taxonomy  | Taxonomic information about proteins                                              | UniProtKB                                                                                                                              |
| Proteome  | Collections of proteins defined from whole genome sequencing of isolate organisms | UniProtKB                                                                                                                              |

### REST interface

Queries to the API are formatted as URL queries. As a general principle a short query to the API will return general
data and a specific query will return detailed data. The following example shows the most basic query that can
be made, '/'.  

[https://www.ebi.ac.uk/interpro/api/](https://www.ebi.ac.uk/interpro/api/)

The JSON response from the API, amongst other attributes, includes a list of all supported "endpoints".


### The main endpoints

The main data types (entry, protein, structure, set, proteome, taxonomy) are the most important of these endpoints 
because they determine the type of data which will be returned from a query. The URLs below request some general 
information about each of the main data types. The response is a list of source databases together with a count of 
how many entities of that type from that datasource are stored in InterPro.

* [/api/entry](https://www.ebi.ac.uk/interpro/api/entry)
* [/api/protein](https://www.ebi.ac.uk/interpro/api/protein)
* [/api/structure](https://www.ebi.ac.uk/interpro/api/structure)
* [/api/set](https://www.ebi.ac.uk/interpro/api/set)
* [/api/taxonomy](https://www.ebi.ac.uk/interpro/api/taxonomy)
* [/api/proteome](https://www.ebi.ac.uk/interpro/api/proteome)


### End point blocks

Endpoint blocks are the most important aspect of the query. An endpoint block can be composed of up to 3 parts: 
an endpoint data type (e.g., entry), a source database (e.g., InterPro) and a unique identifier (e.g., IPR00009). 
The endpoint type is mandatory, while the other two parts are optional.

The presence of the different parts of the main block define the filter and determine the type of response returned by the API. 
The following rules define the type of the response:

* A query defining only an endpoint type returns a list of aggregated values giving the total counts of all the unique entities, 
grouped by each data source of that type. For example, a query ‘/protein’ will return a JSON object with the number 
of proteins in UniProtKB, including the reviewed and unreviewed sections.
* When a query includes a data source, the response is a paginated list of the entities from the source, 
including some basic information. For example, the entities returned by the query `/structure/pdb` include the name, 
accession and experiment type for each PDB structure.
* If an accession is included in the request, the response contains more detailed information about the requested entity. 
For example, the API response to the query `protein/UniProt/P50876` is a JSON object containing all the available information 
for that protein that has been imported into InterPro, including its sequence, description, etc.

The following table shows some examples of end point blocks and how the components determine the response type.

| Query                                                                                        | Response type    | Description                                                                     |
|----------------------------------------------------------------------------------------------|------------------|---------------------------------------------------------------------------------|
| [/api/entry](https://www.ebi.ac.uk/interpro/api/entry)                                       | List of counts   | List of counts of entries in InterPro and member databases                      |
| [/api/protein](https://www.ebi.ac.uk/interpro/api/protein)                                   | List of counts   | List of counts of proteins in UniProtKB and the reviewed and unreviewed subsets |
| [/api/structure](https://www.ebi.ac.uk/interpro/api/structure)                               | List of counts   | List of counts of structures in PDB (PDB is the only source of structure data)  |
| [/api/entry/interpro](https://www.ebi.ac.uk/interpro/api/entry/interpro)                     | List of entities | List of entries in InterPro                                                     |
| [/api/entry/cdd](https://www.ebi.ac.uk/interpro/api/entry/cdd)                               | List of entities | List of entries in CDD                                                          |
| [/api/proteome/uniprot](https://www.ebi.ac.uk/interpro/api/proteome/uniprot)                 | List of entities | List of proteomes (there is only 1 source of proteomes)                         |
| [/api/entry/interpro/ipr023411](https://www.ebi.ac.uk/interpro/api/entry/interpro/ipr023411) | Detailed object  | Data about InterPro entry IPR023411                                             |
| [/api/entry/pfam/pf06235](https://www.ebi.ac.uk/interpro/api/entry/pfam/pf06235)             | Detailed object  | Data about Pfam entry pf06235                                                   |
| [/api/taxonomy/uniprot/9606](https://www.ebi.ac.uk/interpro/api/taxonomy/uniprot/9606)       | Detailed object  | Data about Taxonomy ID 9606                                                     |

### Filtering data

The first end point block in a request defines the data type which will be returned. 
Additional end point blocks can be combined to filter the main dataset. 
This allows combinations of end points to be constructed to limit the data returned by the API.

| Query                                                                                                                                                                      | Main type | Main source | Main accession | Filter type(s)                           | Filter source(s)                           | Filter accession(s)              | Response type    | Description                                                                                                                                                                                                                                        |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|-------------|----------------|------------------------------------------|--------------------------------------------|----------------------------------|------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [/api/entry/](https://www.ebi.ac.uk/interpro/api/entry)                                                                                                                    | entry     | -           | -              | -                                        | -                                          | -                                | List of counts   | List of all entry sources and counts                                                                                                                                                                                                               |
| [/api/entry/protein/](https://www.ebi.ac.uk/interpro/api/entry/protein)                                                                                                    | entry     | -           | -              | protein                                  | -                                          | -                                | List of counts   | Matches only entries which map to a protein. List of all entry sources and counts + all protein sources and counts                                                                                                                                 |
| [/api/entry/protein/set/](https://www.ebi.ac.uk/interpro/api/entry/protein/set)                                                                                            | entry     | -           | -              | *protein *set                            | -                                          | -                                | List of counts   | Matches only entries which are members of a set and map to a protein. List of all entry sources and counts + all protein sources and counts + all set sources and counts                                                                           |
| [/api/entry/protein/set/structure](https://www.ebi.ac.uk/interpro/api/entry/protein/set/structure)                                                                         | entry     | -           | -              | *protein *set *structure                 | -                                          | -                                | List of counts   | Matches only those entries which are members of a set and map to a protein which has at lease one structure. List of all entry sources and counts + all protein sources and counts + all set sources and counts + all structure sources and counts |
| [/api/entry/interpro/](https://www.ebi.ac.uk/interpro/api/entry/interpro)                                                                                                  | entry     | interpro    | -              | -                                        | -                                          | -                                | List of entities | List of all entry InterPro entries                                                                                                                                                                                                                 |
| [/api/entry/interpro/structure](https://www.ebi.ac.uk/interpro/api/entry/interpro/structure)                                                                               | entry     | interpro    | -              | structure                                | -                                          | -                                | List of entities | Matches InterPro entries which map to a protein with a structure. List of all entry InterPro entries together with a structure count                                                                                                               |
| [/api/entry/interpro/structure/pdb](https://www.ebi.ac.uk/interpro/api/entry/interpro/structure/pdb)                                                                       | entry     | interpro    | -              | structure                                | pdb                                        | -                                | List of entities | Matches InterPro entries which map to a protein with a structure in PDB. List of all entry InterPro entries with each item containing a list of all PDB structure that it's linked with                                                            |
| [/api/protein/reviewed/entry/interpro/ipr002117/taxonomy/uniprot/9606](https://www.ebi.ac.uk/interpro/api/protein/reviewed/entry/interpro/ipr002117/taxonomy/uniprot/9606) | protein   | reviewed    | -              | <ul><li>entry</li><li>taxonomy</li></ul> | <ul><li>interpro</li><li>uniprot</li></ul> | <ul><li>ipr002117</li><li>9606</li></ul> | List of entities | Matches InterPro proteins with Taxonomy ID 9606 which contain the InterPro IPR002117 entry. List of proteins                                                                                                                                       |

### Ongoing issues and future work

Some care needs to be taken when combining filters in order to ensure the desired data is requested. 
Some queries return lists of results within lists. These 'inner' lists  are limited to a maximum of 20 hits and cannot be paginated. 
To avoid confusion, we aim to either remove these inner lists or mark them as subsets in the future.
