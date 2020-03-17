Serializers
===

This is the last part of the API logic; after all the endpoints have been processed by their respective views; and the modifiers have been executed, the final Queryset is then serialized. We basically use DRF (_Django REST Framework_) strategy for [serialization](https://www.django-rest-framework.org/api-guide/serializers/). Below we describe how we adapted this.

The call to be serialized is done in [custom.py](../views/custom.py#L134), making sure to pass extra data for any processing required at serializing. In that sense, this aren't pure serializers, as there are certain data tasks that only get executed there, for instance, when using the modifier `with_names` (See [Modifiers docs](../views/MODIFIER_README.md)) the serializer requires to get the names out of the model [taxonomy.py#L323](./taxonomy.py#L323).

Besides those cases, the task of the serializer is to create a data structure using simple types plus dictionaries and lists. DRF will take care of actually writing a JSON (or other configured format) out of it.

We have defined a base serializer class [ModelContentSerializer](./content_serializers.py), that deals with the initiation and contains methods shared for the serializers inheriting from it.

When defining the view that is going to deal with an endpoint, there are 3 class attributes that are useful to define the serializing behaviour.
* `serializer_class` ( Default: `None`): Inherited from DRF, it is the class that will be used to serialize the instances.
* `serializer_detail` (Default: `SerializerDetail.ALL`): Indicates which serializer function use, if this view is in the main endpoint.
* `serializer_detail_filter` (Default: `SerializerDetail.ALL`): Indicates which serializer function use, if this view is in the filter endpoints.

These values get overwritten by the latest View when processing the URL. So for example, if the URL is `/api/entry/interpro/protein` this is how these values get changed:
0. `/api`: This is the root pathe so we start with the defaults:
  * `serializer_class = None`
  * `serializer_detail = SerializerDetail.ALL`
  * `serializer_detail_filter = SerializerDetail.ALL`
1. `/entry`: Main endpoint redifines the values for the main endpoint
  * `serializer_class = EntrySerializer`
  * `serializer_detail = SerializerDetail.ENTRY_OVERVIEW`
2. `/interpro`: Still part of the main endpoint so it changes the detail values:
  * `serializer_class = EntrySerializer`
  * `serializer_detail = SerializerDetail.ENTRY_HEADERS`
3. `/protein` It is a different endpoint so this should be use to define the filter values
  * `serializer_detail_filter = SerializerDetail.PROTEIN_OVERVIEW`
  
Actually [custom.py](../views/custom.py#L231) register multiple `serializer_detail_filter` in case there are several filter endpoints in the URL.

So at the end with the result serialzers of this example Django will go to the `EntrySerializer` class to process each instance of the queryset, and because `serializer_detail = SerializerDetail.ENTRY_OVERVIEW` it would only include the header information of each instance and not its whole metadata ([see interpro.py#L52](./interpro.py#L52)). And for each instance it would include the protein count representation because `serializer_detail_filter = SerializerDetail.PROTEIN_OVERVIEW` ([see interpro.py#L63](./interpro.py#L63)).

All the values for `serializer_detail` and `serializer_detail_filter` are defined in ([constants.py](../constants.py#L4)).
