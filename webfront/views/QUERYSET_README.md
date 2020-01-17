Queryset Manager
===

Django provides the tools to map the model into the selected database. 
This project has a hybrid of MySQL-elasticsearch as its data source. 

Please notice we are not using elastic as a search index for the MySQL DB. 
Instead, we use an index in elasticsearch as our denormalized table that works as a 
precalculated `join` of all the tables.

In MySQL we have tables that have all the details of the entities: 
`Entry`, `Protein`, `Structure`, `Taxonomy`, `Proteome` and `Set`.
And when we need anything that links 2 or more of these entities we should query 
the elastic search index.

For example if we need the sequence of the proteins that have a match with an entry 
with accession IPR000001, we start by quering elastic search, filtering the index where
`entry_acc:IPR000001` to get get the list of protein accessions. 
And then, we query MySQL to get the sequence of all the proteins of the given accessions.

The `QuerysetManager` class is in charge of collecting the filters over the entities and 
built the corresponding queries for elastic and MySQL.

When the API processes the URL([Read more](./README.md)), it adds a filter to the 
`QuerysetManager` for each level in the URL. When all the levels are processed the `get()` method 
of `CustomView` check if all the filters belong to the same entity, in which case, A Django
queryset can be built in in the traditional way, by passing the filters included in the manager.
Otherwise an elastic search query is created with the method `get_searcher_query` of the
QuerysetManager. And the django queryset is using this result.
  
In any case a Django Queryset is created and can be use to serialize a response.
