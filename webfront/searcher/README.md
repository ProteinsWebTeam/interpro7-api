Searcher Controller
===

The classes here are responsible of executing queries in our search index.
Although we are using a Search index, we don't just use if for search purposes, it is also effectively the join table of all the entities in MySQL.

Initially it was split into `SearchController` and `ElasticController` because at that time, we hadn't decided upon the technology we were going to use. 
`SearchController` is basically an abstract class with methods that need to be implemented by any particular 
technology controller. We eventually chose Elasticsearch, so the other controllers were removed to avoid the redundancy of maintaining multiple systems that we weren't being used. Therefore for the rest of the document we will be focus on the Elasticsearch controller

Elasticsearch allows a query to be submitted by either the `q` URL parameter or in the body of the request. 
The general approach in this class is to use the `q` parameter for the filtering of the index and use the _body_ method for the aggregations and other complex operation. We combined these two methods; for example to get the number of InterPro matches of a protein, we filter the index using something like: `q=protein_acc:p99999 AND entry_type:interpro` and then in the body of the query, we aggregate the results to get the count of *unique* matches. e.g.
```json
{
  "aggs": {
    "count": {"cardinality": {"field": "entry_acc"}}
  },
  "size": 0
}
```

Most of the methods in this class are about building generalisations to create the JSON to include in the query. For example the counter above is part of the `get_grouped_object()` method wich can be used in the different endpoints.

There are only 2 methods that actually deal with the HTTP transaction to Elasticsearch `execute_query()` and `_elastic_json_query()` (*Note*: checking this now makes me think we could merge this 2 methods).
