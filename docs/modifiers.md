# InterPro API documentation: modifiers

This document aims to provide some guidance on how to use the InterPro API modifiers for the different API end points blocks, together with examples. Modifiers allow to filter and/or order the data returned by the API call.

## Apply to any API call

| Modifier                         | Compatible with  other modifiers | Data returned                                     | Example                                                               |
|----------------------------------|----------------------------------|---------------------------------------------------|-----------------------------------------------------------------------|
| `page_size=< number up to 200 >` | &check;                          | Number of results returned at a time (default=20) | https://www.ebi.ac.uk:443/interpro/api/protein/reviewed?page_size=100 |
| `search=< text >`                | &check;                          | Entries matching the text search                  | https://www.ebi.ac.uk:443/interpro/api/taxonomy/uniprot/?search=9606  |

## /api/entry

| Modifier                                               | Compatible with  other modifiers         | Data returned                                                                                                                  | Example                                                                                        |
|--------------------------------------------------------|------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| `group_by=type`                                        | x                                        | Number of entries for each entry type (e.g. family, domain, site...)                                                           | https://www.ebi.ac.uk:443/interpro/api/entry?group_by=type                                     |
| `group_by=source_database`                             | x                                        | Number of entries for each member database (e.g. pfam, CDD...)                                                                 | https://www.ebi.ac.uk:443/interpro/api/entry?group_by=source_database                          |
| `group_by=tax_id`                                      | x                                        | Number of entries (InterPro+member database) for key species                                                                   | https://www.ebi.ac.uk:443/interpro/api/entry?group_by=tax_id                                   |
| `group_by=go_terms`                                    | x                                        | Number of entries (InterPro+member database) for each GO term                                                                  | https://www.ebi.ac.uk:443/interpro/api/entry?group_by=go_terms                                 |
| `type=< entry type >`                                  | &check;                                  | List of signatures with the entry type specified                                                                               | https://www.ebi.ac.uk:443/interpro/api/entry?type=family                                       |
| `go_category=[F, C, P]`                                | &check;                                  | List of GO terms for the category specified (P for Biological Process, F for Molecular Function, and C for Cellular Component) | https://www.ebi.ac.uk:443/interpro/api/entry?go_category=F                                     |
| `go_term=< GO identifier >`                            | &check;                                  | Count entries that have been annotated with the given GO term, group by member database                                        | http://www.ebi.ac.uk:443/interpro/api/entry?go_term=GO:0004298                                 |
| `ida_search`                                           | &check;                                  | List of InterPro domain architectures with protein count                                                                       | https://www.ebi.ac.uk:443/interpro/api/entry?ida_search                                        |
| `ida_search=< ipr1,pf2,ipr3 >`                         | &check;                                  | List of ida and protein count for the specified domain accessions                                                              | https://www.ebi.ac.uk:443/interpro/api/entry?ida_search=IPR003100,IPR003165                    |
| `ida_search=< ipr1,pf2,ipr3 >&ordered`                 | only works with `ida_search`             | List of ida and protein count for the specified domain accessions where the accession order matters                            | https://www.ebi.ac.uk:443/interpro/api/entry?ida_search=IPR003100,IPR003165&ordered            |
| `ida_search=< ipr1,pf2,ipr3 >&ordered&exact`           | only works with `ida_search` + `ordered` | Protein count for proteins containing specified domain accessions only                                                         | https://www.ebi.ac.uk:443/interpro/api/entry?ida_search=IPR003100,IPR003165&exact              |
| `ida_search=< ipr1,pf2,ipr3 >&ida-ignore=< ipr4,pf6 >` | only works with `ida_search`             | List of ida and protein count for the specified domain accessions where the last accessions specified shouldn't be in the ida  | https://www.ebi.ac.uk:443/interpro/api/entry?ida_search=IPR003100,IPR003165&ida_ignore=PF08699 |

## /api/entry/< _database name_ >

database name can be: interpro, pfam, cdd, panther, sfld, cathgene3d, ssf, hamap, pirsf, prints, prosite, profile, smart, ncbifam
Since interPro 94.0 `tigrfams` has been replaced by `ncbifam`. Temporary redirects are in place to avoid immediate issues, however users are highly recommended to start using `ncbifam` as the memberDB nam to avoid any problems. 

| Modifier                                                                                                                                                 | Compatible with other modifiers | Data returned                                                                                                | Example                                                                                           |
|----------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|--------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| `group_by=type`                                                                                                                                          | x                               | Number of signatures for each member database entry type (e.g. family, domain ...) for the database selected | https://www.ebi.ac.uk:443/interpro/api/entry/pfam?group_by=type                                   |
| `group_by=source_database`                                                                                                                               | x                               | Number of signatures for the database selected                                                               | https://www.ebi.ac.uk/interpro/api/entry/pfam?group_by=source_database                            |
| `group_by=go_categories`                                                                                                                                 | x                               | Number of signatures for each GO term category for the database selected                                     | https://www.ebi.ac.uk:443/interpro/api/entry/cathgene3d?group_by=go_categories                    |
| `group_by=tax_id`                                                                                                                                        | x                               | Number of signatures for key species for the database selected                                               | https://www.ebi.ac.uk:443/interpro/api/entry/cathgene3d?group_by=tax_id                           |
| `group_by=go_terms`                                                                                                                                      | x                               | Number of entries for each GO term for the database selected                                                 | https://www.ebi.ac.uk:443/interpro/api/entry/integrated?group_by=go_terms                         |
| `type=< entry_type >`                                                                                                                                    | &check;                         | List of signatures with the entry type specified for the database selected                                   | https://www.ebi.ac.uk:443/interpro/api/entry/smart?type=domain                                    |
| `sort_by=accession`                                                                                                                                      | &check;                         | List of signatures sorted by accession (low to high) for the database selected                               | https://www.ebi.ac.uk:443/interpro/api/entry/pfam?sort_by=accession                               |
| `sort_by=integrated`                                                                                                                                     | &check;                         | List of signatures sorted by integrated ones first for the database selected                                 | https://www.ebi.ac.uk:443/interpro/api/entry/pfam?sort_by=integrated                              |
| `extra_fields=[counters, entry_id, short_name, description, wikipedia, literature, hierarchy, cross_references, entry_date, is_featured, overlaps_with]` | x                               | Includes the value of the selected fields in the results                                                     | https://www.ebi.ac.uk:443/interpro/api/entry/InterPro?signature_in=hamap&extra_fields=description |
| `annotation=[hmm, alignment, logo]`                                                                                                                      | x                               | List of entries which have an annotation of the given type (hmm, alignment, logo)                            | https://www.ebi.ac.uk:443/interpro/api/entry/pfam?annotation=hmm                                  |

## /api/entry/< _integrated, unintegrated_ >

Information on member database signatures integrated/unintegrated in InterPro entries

| Modifier                                                                                                                                                 | Compatible with  other modifiers | Data returned                                                                                | Example                                                                                         |
|----------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------|----------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| `group_by=type`                                                                                                                                          | x                                | Number of integrated/unintegrated entries for each entry type (e.g. family, domain, site...) | https://www.ebi.ac.uk:443/interpro/api/entry/unintegrated?group_by=type                         |
| `group_by=source_database`                                                                                                                               | x                                | Number of integrated/unintegrated entries for each member database (e.g. pfam, CDD...)       | https://www.ebi.ac.uk:443/interpro/api/entry/unintegrated?group_by=source_database              |
| `group_by=tax_id`                                                                                                                                        | x                                | Number of integrated/unintegrated entries for key species                                    | https://www.ebi.ac.uk:443/interpro/api/entry/unintegrated?group_by=tax_id                       |
| `group_by=go_terms`                                                                                                                                      | x                                | Number of integrated/unintegrated entries for each GO term                                   | https://www.ebi.ac.uk:443/interpro/api/entry/integrated?group_by=go_terms                       |
| `extra_fields=[counters, entry_id, short_name, description, wikipedia, literature, hierarchy, cross_references, entry_date, is_featured, overlaps_with]` | x                                | Includes the value of the selected fields in the results                                     | https://www.ebi.ac.uk:443/interpro/api/entry/integrated?group_by=go_terms&extra_fields=counters |

## /api/entry/interpro

| Modifier                    | Compatible with  other modifiers | Data returned                                                                                                                  | Example                                                                         |
|-----------------------------|----------------------------------|--------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| `group_by=member_databases` | x                                | Number of integrated signatures for each member database (e.g. pfam, CDD...)                                                   | https://www.ebi.ac.uk:443/interpro/api/entry/interpro?group_by=member_databases |
| `latest_entries`            | x                                | List of InterPro entries integrated in the last InterPro release                                                               | https://www.ebi.ac.uk:443/interpro/api/entry/interpro?latest_entries            |
| `signature_in=< memberdb >` | &check;                          | List of InterPro entries that have a match with the given memberDB                                                             | https://www.ebi.ac.uk:443/interpro/api/entry/InterPro?signature_in=hamap        |
| `go_category=[F, C, P]`     | &check;                          | List of GO terms for the category specified (P for Biological Process, F for Molecular Function, and C for Cellular Component) | https://www.ebi.ac.uk:443/interpro/api/entry/interpro?go_category=F             |
| `go_term=< GO identifier >` | x                                | List of InterPro entries that have been annotated with the given GO term                                                       | https://www.ebi.ac.uk:443/interpro/api/entry/interpro?go_term=GO:0004298        |

## /api/entry/interpro/< _InterPro entry accession_ >

| Modifier                                                                                                                                                 | Compatible with other modifiers | Data returned                                                                                               | Example                                                                                 |
|----------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|-------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| `interactions`                                                                                                                                           | x                               | List of interactions proteins matching the entry are involved in (obtained from Intact database)            | https://www.ebi.ac.uk:443/interpro/api/entry/InterPro/IPR000477?interactions            |
| `pathways`                                                                                                                                               | x                               | List of pathways proteins matching the entry are involved in (obtained from MetaCyc and Reactome databases) | https://www.ebi.ac.uk:443/interpro/api/entry/InterPro/IPR024156?pathways                |
| `annotation:info`                                                                                                                                        | x                               | Entry information                                                                                           | https://www.ebi.ac.uk:443/interpro/api/entry/InterPro/IPR025743?annotation:info         |
| `extra_fields=[counters, entry_id, short_name, description, wikipedia, literature, hierarchy, cross_references, entry_date, is_featured, overlaps_with]` | x                               | Includes the value of the selected fields in the results                                                    | https://www.ebi.ac.uk:443/interpro/api/entry/InterPro/IPR024156?extra_fields=short_name |

## /api/entry/< _member database_ >

! Not available for InterPro

| Modifier                            | Compatible with other modifiers | Data returned                                                                                         | Example                                                                |
|-------------------------------------|---------------------------------|-------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| `interpro_status`                   | &check;                         | Number of signatures integrated and unintegrated in InterPro entries for the member database selected | https://www.ebi.ac.uk:443/interpro/api/entry/panther?interpro_status   |
| `integrated=< interpro accession >` | &check;                         | List of signatures integrated in the specified InterPro entry                                         | https://www.ebi.ac.uk:443/interpro/api/entry/pfam?integrated=IPR003165 |

## /api/entry/< _member database_ >/< _accession_>

| Modifier                            | Compatible with other modifiers | Data returned                                       | Example                                                                  |
|-------------------------------------|---------------------------------|-----------------------------------------------------|--------------------------------------------------------------------------|
| `annotation=[hmm, alignment, logo]` | x                               | Download compressed signature hmm file if it exists | https://www.ebi.ac.uk:443/interpro/api/entry/pfam/pf02171?annotation=hmm |

## /api/entry/protein

| Modifier        | Compatible with  other modifiers | Data returned                                                         | Example                                                            |
|-----------------|----------------------------------|-----------------------------------------------------------------------|--------------------------------------------------------------------|
| `group_by=type` | x                                | Number of proteins for each entry type (e.g. family, domain, site...) | https://www.ebi.ac.uk:443/interpro/api/entry/protein?group_by=type |

## /api/protein

| Modifier                      | Compatible with other modifiers | Data returned                                                               | Example                                                                 |
|-------------------------------|---------------------------------|-----------------------------------------------------------------------------|-------------------------------------------------------------------------|
| `group_by=tax_id`             | x                               | Number of proteins for each taxon                                           | https://www.ebi.ac.uk:443/interpro/api/protein?group_by=tax_id          |
| `group_by=go_terms`           | x                               | Number of proteins for each GO term                                         | https://www.ebi.ac.uk:443/interpro/api/protein?group_by=go_terms        |
| `group_by=match_presence`     | x                               | Number of proteins with/without an InterPro entry match                     | https://www.ebi.ac.uk:443/interpro/api/protein?group_by=match_presence  |
| `group_by=is_fragment`        | x                               | Number of full/fragmented proteins                                          | https://www.ebi.ac.uk:443/interpro/api/protein?group_by=is_fragment     |
| `group_by=source_database`    | x                               | Number of reviewed and unreviewed proteins                                  | https://www.ebi.ac.uk:443/interpro/api/protein?group_by=source_database |
| `match_presence=[true,false]` | &check;                         | Number of proteins with [true]/without [false] a match to an InterPro entry | https://www.ebi.ac.uk:443/interpro/api/protein?match_presence=false     |
| `tax_id=< accession >`        | &check;                         | Number of proteins that belong to this taxonomy id                          | https://www.ebi.ac.uk:443/interpro/api/protein?tax_id=2711              |
| `is_fragment=[true,false]`    | &check;                         | Number of proteins that are [true]/aren't [false] fragments                 | https://www.ebi.ac.uk:443/interpro/api/protein?is_fragment=true         |

## /api/protein/< _uniprot/reviewed/unreviewed_ >

| Modifier                                                                                                                                                                     | Compatible with other modifiers | Data returned                                                                                             | Example                                                                                         |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|-----------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| `group_by=go_terms`                                                                                                                                                          | x                               | List of proteins for each GO term for the protein source selected                                         | https://www.ebi.ac.uk:443/interpro/api/protein/reviewed?group_by=go_terms                       |
| `group_by=is_fragment`                                                                                                                                                       | x                               | Number of proteins that are and aren't fragments for the protein source selected                          | https://www.ebi.ac.uk:443/interpro/api/protein/reviewed?group_by=is_fragment                    |
| `group_by=match_presence`                                                                                                                                                    | x                               | Number of proteins that have and don't have matches to InterPro entries for the protein source selected   | https://www.ebi.ac.uk:443/interpro/api/protein/reviewed?group_by=match_presence                 |
| `group_by=tax_id`                                                                                                                                                            | x                               | Number of proteins for each taxon for the protein source selected                                         | https://www.ebi.ac.uk:443/interpro/api/protein/uniprot?group_by=tax_id                          |
| `group_by=source_database`                                                                                                                                                   | x                               | Number of proteins for the protein source selected                                                        | https://www.ebi.ac.uk:443/interpro/api/protein/unreviewed?group_by=source_database              |
| `go_term=<_ GO identifier_ >`                                                                                                                                                | &check;                         | List of proteins for the GO term and protein source selected                                              | https://www.ebi.ac.uk:443/interpro/api/protein/reviewed?go_term=GO:0004298                      |
| `id=< Uniprot identifier >`                                                                                                                                                  | &check;                         | Information about the protein with the specified UniProt identifier                                       | https://www.ebi.ac.uk:443/interpro/api/protein/reviewed?id=CYC_HUMAN                            |
| `tax_id=< accession >`                                                                                                                                                       | &check;                         | List of proteins corresponding to the tax_id specified for the protein resource selected                  | http://www.ebi.ac.uk/interpro/api/protein/uniprot?tax_id=2711                                   |
| `ida=< ida_accession >`                                                                                                                                                      | &check;                         | List of proteins with the specified domain architecture for the protein source selected                   | http://www.ebi.ac.uk/interpro/api/protein/reviewed?ida=6ad3f81f5ba41a43b4c938fb2018f519f64e0548 |
| `match_presence=[true,false]`                                                                                                                                                | &check;                         | List of proteins for the protein source selected with [true]/without [false] a match to an InterPro entry | https://www.ebi.ac.uk:443/interpro/api/protein/reviewed?match_presence=true                     |
| `is_fragment=[true,false]`                                                                                                                                                   | &check;                         | List of proteins for the protein source selected that are [true]/aren't [false] fragments                 | https://www.ebi.ac.uk:443/interpro/api/protein/reviewed?is_fragment=true                        |
| `extra_fields=[counters, identifier, description, sequence, gene, go_terms, evidence_code, residues, tax_id, proteome, extra_features, structure, is_fragment, ida_id, ida]` | x                               | Includes the value of the selected fields in the results                                                  | https://www.ebi.ac.uk:443/interpro/api/protein/reviewed?id=CYC_HUMAN&extra_fields=sequence      |

## /api/protein/< _uniprot/reviewed/unreviewed_ >/< _protein accession_ >

| Modifier                                                                                                                                                                     | Compatible with other modifiers | Data returned                                                                 | Example                                                                              |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|-------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| `residues`                                                                                                                                                                   | x                               | Residues annotations for the protein selected                                 | https://www.ebi.ac.uk:443/interpro/api/protein/uniprot/A0A000?residues               |
| `structureinfo`                                                                                                                                                              | x                               | cath/scop domains matching the protein selected                               | https://www.ebi.ac.uk:443/interpro/api/protein/uniprot/P02185?structureinfo          |
| `ida`                                                                                                                                                                        | x                               | Information about the protein domains arrangement based on Pfam domains       | https://www.ebi.ac.uk:443/interpro/api/protein/reviewed/D4A7N1?ida                   |
| `extra_features`                                                                                                                                                             | x                               | Matches from the extra feature section (e.g. Mobidb-lite, Coil)               | https://www.ebi.ac.uk:443/interpro/api/protein/reviewed/D4A7N1?extra_features        |
| `isoforms`                                                                                                                                                                   | x                               | Different isoforms of the protein                                             | https://www.ebi.ac.uk:443/interpro/api/protein/reviewed/Q6ZNL6?isoforms              |
| `isoforms=< isoform_id >`                                                                                                                                                    | x                               | Information about the isoform selected                                        | https://www.ebi.ac.uk:443/interpro/api/protein/reviewed/Q6ZNL6?isoforms=Q6ZNL6-1     |
| `extra_fields=[counters, identifier, description, sequence, gene, go_terms, evidence_code, residues, tax_id, proteome, extra_features, structure, is_fragment, ida_id, ida]` | x                               | Includes the value of the selected fields in the results                      | https://www.ebi.ac.uk:443/interpro/api/protein/reviewed/Q6ZNL6?extra_fields=sequence |
| `conservation=< member database >`                                                                                                                                           | x                               | Residue conservation calculated using HMMER for the member database specified | https://www.ebi.ac.uk:443/interpro/api/protein/reviewed/D4A7N1?conservation=panther  |

## /api/proteome/uniprot

| Modifier                                    | Compatible with other modifiers | Data returned                                                                   | Example                                                                                |
|---------------------------------------------|---------------------------------|---------------------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| `group_by=proteome_is_reference`            | x                               | Number of UniProt proteomes that are/aren't from the UniProt reference proteome | https://www.ebi.ac.uk:443/interpro/api/proteome/uniprot?group_by=proteome_is_reference |
| `extra_fields=[counters, strain, assembly]` | x                               | Includes the value of the selected fields in the results                        | https://www.ebi.ac.uk:443/interpro/api/proteome/uniprot?extra_fields=counters          |

## /api/set/< _all, cdd, pfam_ >

| Modifier                                              | Compatible with other modifiers | Data returned                                            | Example                                                              |
|-------------------------------------------------------|---------------------------------|----------------------------------------------------------|----------------------------------------------------------------------|
| `extra_fields=[counters, description, relationships]` | x                               | Includes the value of the selected fields in the results | https://www.ebi.ac.uk:443/interpro/api/set/cdd?extra_fields=counters |

## /api/set/< _all, cdd, pfam_ >/< _accession_ >

| Modifier     | Compatible with other modifiers | Data returned                                            | Example                                                             |
|--------------|---------------------------------|----------------------------------------------------------|---------------------------------------------------------------------|
| `alignments` | x                               | Alignment information for the database and set specified | https://www.ebi.ac.uk:443/interpro/api/set/cdd/cl00014/?alignments= |

## /api/structure

| Modifier                         | Compatible with other modifiers | Data returned                                         | Example                                                                   |
|----------------------------------|---------------------------------|-------------------------------------------------------|---------------------------------------------------------------------------|
| `experiment_type=[x_ray,nmr,em]` | x                               | Number of structures for the experiment type selected | https://www.ebi.ac.uk:443/interpro/api/structure?experiment_type=nmr      |
| `group_by=experiment type`       | x                               | Number of structures for each experiment type         | https://www.ebi.ac.uk:443/interpro/api/structure?group_by=experiment_type |

## /api/structure/pdb

| Modifier                                                                          | Compatible with other modifiers | Data returned                                                | Example                                                                                                  |
|-----------------------------------------------------------------------------------|---------------------------------|--------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| `experiment_type=[x_ray,nmr,em]`                                                  | &check;                         | List of PDB structures for the experiment type selected      | https://www.ebi.ac.uk:443/interpro/api/structure/PDB/?experiment_type=x-ray                              |
| `resolution=< start-end >`                                                        | &check;                         | List of PDB structures between the resolution range selected | https://www.ebi.ac.uk:443/interpro/api/structure/pdb?resolution=1.0-2.5                                  |
| `group_by=experiment type`                                                        | x                               | Number of PDB structures for each experiment type            | https://www.ebi.ac.uk:443/interpro/api/structure/pdb?group_by=experiment_type                            |
| `extra_fields=[release_date, literature, chains, secondary_structures, counters]` | &check;                         | Includes the value of the selected fields in the results     | https://www.ebi.ac.uk:443/interpro/api/structure/pdb?resolution=1.0-2.5&extra_field=secondary_structures |

## /api/structure/pdb/< _pdb accession_ >

| Modifier                                                                          | Compatible with other modifiers | Data returned                                            | Example                                                                            |
|-----------------------------------------------------------------------------------|---------------------------------|----------------------------------------------------------|------------------------------------------------------------------------------------|
| `extra_fields=[release_date, literature, chains, secondary_structures, counters]` | x                               | Includes the value of the selected fields in the results | https://www.ebi.ac.uk:443/interpro/api/structure/pdb/101m?extra_field=release_date |

## /api/taxonomy/uniprot

| Modifier                                                             | Compatible with other modifiers | Data returned                                            | Example                                                                          |
|----------------------------------------------------------------------|---------------------------------|----------------------------------------------------------|----------------------------------------------------------------------------------|
| `scientific_name=< name >`                                           | x                               | Taxon hierachy and counters                              | https://www.ebi.ac.uk:443/interpro/api/taxonomy/uniprot?scientific_name=Bacteria |
| `key_species`                                                        | x                               | Taxonomy info for key species                            | https://www.ebi.ac.uk:443/interpro/api/taxonomy/uniprot?key_species              |
| `extra_fields=[counters, scientific_name, full_name, lineage, rank]` | &check;                         | Includes the value of the selected fields in the results | https://www.ebi.ac.uk:443/interpro/api/taxonomy/uniprot?extra_fields=full_name   |

## /api/taxonomy/uniprot/< _taxonomy accession_ >

| Modifier                                 | Compatible with other modifiers | Data returned                                                                                         | Example                                                                               |
|------------------------------------------|---------------------------------|-------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| `with_names`                             | x                               | Selected taxon hierarchy and names                                                                    | https://www.ebi.ac.uk:443/interpro/api/taxonomy/uniprot/1?with_names                  |
| `filter_by_entry=< InterPro accession >` | x                               | Selected taxon hierarchy and counters for the InterPro entry accession specified                      | https://www.ebi.ac.uk:443/interpro/api/taxonomy/uniprot/1?filter_by_entry=IPR001165   |
| `filter_by_entry_db=< db name >`         | x                               | Selected taxon hierarchy and counters for the database name specified (e.g. interpro, pfam, smart...) | https://www.ebi.ac.uk:443/interpro/api/taxonomy/uniprot/1?filter_by_entry_db=interpro |

## /api/protein/uniprot/entry/< _source database_ >/< _interpro accession_ >

Proteins with an AlphaFold model.

| Modifier                 | Compatible with other modifiers | Data returned                                                                         | Example                                                                                         |
|--------------------------|---------------------------------|---------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| `has_model=[true,false]` | x                               | List of proteins with/without an AlphaFold prediction for the <_ source database _> entry selected | https://www.ebi.ac.uk:443/interpro/api/protein/uniprot/entry/InterPro/IPR000001/?has_model=true |


Proteins with an AlphaFold or BFVD model.

| Modifier                 | Compatible with other modifiers | Data returned                                                                         | Example                                                                                         |
|--------------------------|---------------------------------|---------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| `with=[alphafold,bfvd]` | x                               | List of proteins with an AlphaFold prediction or a BFVD prediction for the <_ source database _> entry selected | https://www.ebi.ac.uk:443/interpro/api/protein/uniprot/entry/InterPro/IPR000001/?with=alphafold|

