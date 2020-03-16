Searcher Controller
===

The classes here are the ones in chage to execute queries in our search index.
Remember that although we are using a Search index, we are not using it exclusively for searching purposes. 
Instead, it is our join table of all the entities in MySQL.

It initally was split as `SearchController` and `ElasticController` because at that time, we weren't sure 
of what technology we were going to use. 
`SearchController` is basically an abstract class with thhe methods that need to be implemented by any particular 
technology contorller.We eventually choose elastic search and other controllers were removed  to avoid the overload of mantaining multiple systems that we werent actually using. So for the rest of the document we will be focusing on the ElasticSearch controller

ElasticSearch allows to submit a query by either the `q` URL parameter or in the body of the request. 
The general approach in this class is to use the `q` parameter for the filtering of the index and use the _body_ method for the aggregations and other complex operation. We actually combined this two methods; for example to get the number of interpro matches of a protein, we filtered the index using something like: `q=protein_acc:p99999 AND entry_type:interpro` and then in the body of the query we aggregate the results to get the count of *unique* matches. e.g.
```json
{
  "aggs": {
    "count": {"cardinality": {"field": "entry_acc"}},
  },
  "size": 0,
}
```

Most of the methods in this class are about to built generalizations to create the json to include in the query. For example the counter above is part of the `get_grouped_object()` method wich can be used in the different endpoints.

There are only 2 methods that actually deal with the HTTP transaction to elasticsearch `execute_query()` and `_elastic_json_query()` (*Note*: checking this now makes me think we could merge this 2 methods).
