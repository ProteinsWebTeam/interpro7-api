# InterPro API documentation

This document aims to provide some guidance on how to use the InterPro API. The query syntax is very flexible and enables fetching and filtering of many different kinds of data from the InterPro databases. The documentation here defines some key concepts that should help with getting started.

In addition the to information given here, the [InterPro website](https://www.ebi.ac.uk/interpro/beta) is built upon the API and therefore provides many practical examples of how the API is used to fetch different types of data.  

## Getting started with some Examples
### 1. How many entries are there in the InterPro API?
This is a good starter query. InterPro integrates  data from all the member databases of the InterPro Consortium and contains both the original member database data and data for curated integrated entries. The following query returns a list of counts for all the different sources of entries in the InterPro dataset. In addition, there are also counts for the number of member database entries 'integrated' into InterPro and counts for those still 'unintegrated'.

[/api/entry](https://www.ebi.ac.uk/interpro/beta/api/entry)

### 2. How do I get a list of all CDD entries in the InterPro API?
This query will return a paginatable list of summary information about CDD entries included in our dataset. The response returns first 20 hits and contains a link to the next 20 hits. Due to a limitation our databases, this list cannot be sorted.

[/api/entry/cdd](https://www.ebi.ac.uk/interpro/beta/api/entry/cdd)

### 3. How many entries matching Human P53 protein in the different data sources (accession P04637)?
This query returns a list of counts of entries linked to P53 in all datasources in InterPro

[/api/entry/protein/uniprot/P04637](https://www.ebi.ac.uk/interpro/beta/api/entry/protein/uniprot/P04637)

### 4. How do I retrieve a list of all InterPro entries found in Human P53 protein (accession P04637)?
This query returns a list of InterPro entries which map to Human P53 protein.

[/api/entry/interpro/protein/uniprot/P04637](https://www.ebi.ac.uk/interpro/beta/api/entry/interpro/protein/uniprot/P04637)

### 5. How do I retrieve a list of UniProtKB reviewed proteins containing the entry IPR002117 domain?
This query returns a list of proteins with IPR002117 domains together with the location of the domain in the protein sequence.

[/api/protein/reviewed/entry/interpro/ipr002117](https://www.ebi.ac.uk/interpro/beta/api/protein/reviewed/entry/interpro/ipr002117)

### 6. How do I retrieve a list of organisms which possess RNA-directed RNA polymerase (IPR026381)?
This query returns a list of organisms which have a protein which contains a match to IPR026381.

[/api/taxonomy/uniprot/entry/interpro/IPR026381](https://www.ebi.ac.uk/interpro/beta/api/taxonomy/uniprot/entry/interpro/IPR026381)

## Key concepts

### Main data types
Currently there are six main types of data available through the API.
