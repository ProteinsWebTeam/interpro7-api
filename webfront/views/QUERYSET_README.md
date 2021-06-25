# Queryset Manager

Django provides the tools to map the model into the selected database. 
This project has a hybrid of MySQL-Elasticsearch as its data source. 

Please notice we are not using elastic as a search index for the MySQL DB. 
Instead, we use an index in Elasticsearch as our denormalized table that works as a 
pre-calculated `join` of all the tables.

In MySQL we have tables that have all the details of the entities: 
`Entry`, `Protein`, `Structure`, `Taxonomy`, `Proteome` and `Set`.
And when we need anything that links two or more of these entities we should query 
the Elasticsearch index.

For example if we need the sequence of the proteins that have a match with an entry 
with accession `IPR000001`, we start by querying Elasticsearch, filtering the index where
`entry_acc:IPR000001` to get the list of protein accessions. 
And then, we query MySQL to get the sequence of all the proteins of the given accessions.

The `QuerysetManager` class (see section below) is in charge of collecting the filters over the entities and 
built the corresponding queries for elastic and MySQL.

When the API processes the URL ([Read more](./README.md)), it adds a filter to the 
`QuerysetManager` for each level in the URL. When all the levels are processed, the `get()` method 
of `CustomView` checks if all the filters belong to the same entity, in which case, a Django
queryset can be built in the traditional way, by passing the filters included in the manager.
Otherwise an Elasticsearch query is created with the method `get_searcher_query` of the
QuerysetManager. And the Django queryset is using this result.
  
In any case a Django Queryset is created and can be use to serialize a response.

## The `QuerysetManager` class

The class is in the [`queryset_manager.py` file](./queryset_manager.py). 
The main endpoint of the queryset needs to be defined when the `QuerysetManager` is initialised. e.g.

```python
queryset_manager.reset_filters("entry", endpoint_levels)
```

The `filters` attribute of this class is where the filters get stored. It is a dictionary where each key is an endpoint,
and their value is also a dictionary where each key:value is a filter:value.

For example to filter a queryset for the entry with accession `"IPR000001"`, you can use the following code:

```python
queryset_manager.add_filter(
  "entry", accession__iexact="IPR000001"
)
```

Then the value of  `queryset_manager.filters` will be something like:

```python
{
  "search": {},
  "searcher": {},
  "entry": {
    "accession__iexact": "IPR000001",
  },
  "structure": {},
  "protein": {},
  "taxonomy": {},
  "proteome": {},
  "set": {},
  "set_alignment": {},
}
```

A second structure similar to the one above is used to store the _filter by exclusion_, 
for example something that is different to the type `"family"`.

## From stored filters to data

When all the filters are applying to a single endpoint, the data will be taken from MySQL.
Tables in MySQL are mapped into the Django model, and given that we are using the same format 
to store filters, the Django Queryset can be created by starting with the model that corresponds 
to the one defined as `main_endpoint`, and adding all the filters that have been stored for it.
That is basically the logic in the method `get_queryset()`.

But when there are more multiple endpoints the query needs to be executed in our Elasticsearch index.
The method `get_searcher_query()` is in charge of translating the filter into a string that follows 
the Lucene Query Language, which is the format that Elasticsearch supports in it `q` parameter.

For example with the same filter than above for accession `IPR00001` the outcome of calling `queryset_manager.get_searcher_query()` should be something like `entry_acc:IPR00001`

This query is not executed yet, oly the string of the query is generated. the logic for elastic queries 
is explained [here](../searcher/README.md)
