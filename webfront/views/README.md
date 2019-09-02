# InterPro7 Views

This folder contains the Django views inplemented for the InterPro7 API. 

Our strategy was to have a hierarchical structure (OOP) for all our views with 
a single entry point.

```
                      |            | <- | GeneralHandler |
| GenericAPIView | <- | CustomView |
                      |            | <- | *BlockHandler |
```


The [`urls.py`](../../interpro/urls.py) file is rather simple and just points 
every path starting with `/api` to the common view: `GeneralHandler`. 

```python
urlpatterns = [url(r"^api/(?P<url>.*)$", common.GeneralHandler.as_view())]
```


## URL structure

As seen above a valid URL on the InterPro7 API should start with `/api`.
From then onward, we will split the URL on the parts separated by `/`, and each of those
parts will be called *block* in this document. (e.g. /api/[block1]/[block2]/...)

A set of *blocks* can create an *endpoint-block*. For example`/api/protein/reviewed` defines a 
single *endpoint-block* formed by 2 *blocks*: `/protein` indicating that we are using the 
*protein* endpoint and `/reviewed` indicating the database to be filtered by.

We have define a structure that allows to combine information from multiple endpoints.
The first *endpoint-block* will be called *main-endpoint-block*. Any following 
*endpoint-block* are considered filters. 
In this way, the *main-endpoint-block* defines the set to return, and the rest of the endpoints
filter the set. For example `/api/protein/reviewed/entry/interpro` is a list of reviewed proteins
that have matches with interpro entries; in contrast of `/api/entry/interpro/protein/reviewed`, 
which is a list of interproentris that can match reviwed proteins.


## GeneralHandler

This configuration ensures that all the API requests are first managed in a single place, 
including all the common logic:
* Defines the available endpoints
* For the current request
    * Initializes the QuerysetManager.
    * Initializes the SearchController.
    * Initializes the ModifierManager.
    * Splits a given URL into blocks.
    * If there are not blocks generates the response for the root query i.e. `/api/`.
    * Tries to get the response from the redis cache.
    * A recursion chain gets started: it invokes the `get()` method of its parent class `CustomView`
    and recursively finding a handler for each block.

### Cache Strategy
Besides using the cache for fast responses we  use it to avoid duplication of expensive queries.
When a query is executed it has 90 seconds (by default) to get a response. 
Otherwise the response will be a time put HTTP code `408`, which will be temporarily saved in the 
cache. 
This however won't interrupt the query, which will keep its execution in parallel.
if a duplicate request arrives before the original request finishes, it will automaticaly get the
`408` from the cache.
When the original request completes, it saves the response in the cache, replacing the `408` one. 
This way, any future duplicate request will get the value from the cache alomos instantly.  


## CustomView

All *block* handlers inherit from `CustomView` and have to implement their `get()` method.


#### main-endpoint-block
 
Basically the task of the `get()` method in `CustomView` is to find what is the most apropiate 
handler for the current block, and once it founds it invokes the `get()` method of such handler.
The usual tasks of a handler and in particular of the `get()` method are:

 *  To add more filters to the current queryset. For example in a URL `/api/entry/interpro` the 
    handler of the `/interpro` *block* adds a filter like `source_database="interpro"`. 
 *  To define modifiers. Which is our strategy to extend the API, for example the modifier 
    `go_term` allows to filter a set of entries, selecting those which are annotated with a given GO ID.
 *  To define a serializer linked to this *block*. The actual serializer that a response will use, 
    it is the one linked to the last *block* of the *main-endpoint-block*.
 *  Finally, the `get()` method will return the result of invoking the `get()` method of its parent class.
    This, of course is when the recursion occurs.  

Once all the *blocks* of the main endpoint have been exhausted, is is time to process the filters:
 
 #### filter-endpoint-blocks
 The logic is very similar, but now the method to call in all the handlers is `filter()`.
 The `filter()` method should be defined as _static_ and should return the filtered queryset.
 This is then repeated for the rest of the *endpoint-blocks*
 
After processing the filters the last call of the recursion occurs, and because there are not more blocks, 
we should finish the response, which implies the excution of any available modifiers, setting up 
the pagination in case of responses with many items, and finally serializing the built queryset.
 
