Modifier Manager
===

Modifiers are the technique defined to extend the functionality of the API. Modifiers are expose to the user as URL parameters, so they can modify the current queriset by filtering it further, aggregated or change the serializer of it.

As is described [here](./README.md), the API executes a view for each level in the URL. The main purpose of the view execution is to filter the queryset. But additionally, modifiers are registered in during this process. For example, the modifier `with_names` was registered at the level of the [TaxonomyAccessionHandler](./taxonomy.py#L35). This modifier is used by user that wants to include in the response, the names of children and parents of a given taxon id.

After all the levels of the URL have been processed by the views, the custom manager checks if there are any modifier registered, and if thhe associated URL parameter is present, and executes the modifier if that's the case.

This are the parameters of the method to register a modifier:
* `parameter`: The associated URL parameter of the mofifier.
* `action`: The modifier function. It should returns a queryset or None. And its parameters are:
  * `value`: The value given as a URL parameter.
  * `general_handler`: The handler that is in charge of the current request.
* `use_model_as_payload`: (default: `False`) If the modifier needs to replace the queryset to be serialized.
* `serializer`: (default: `None`) In case the modification requires to be serialized in an specific way.
* `many`: (default: `False`) This is to explicitely indicate when the modifier queryset has *many* results and needs to be iterated. This is useful to indicate the pagination logic needs to be included. Note that this only makes sense if `use_model_as_payload == True`. 
* `works_in_single_endpoint`: (default: `True`) It indicates that a given modifier works for single endpoints URLs. If is false it will raise an exception when a single endpoint URL has this modifier
* `works_in_multiple_endpoint`: (default: `True`) It indicates that a given modifier works for multiple endpoints URLs. If is false it will raise an exception when a multiple endpoint URL has this modifier.

Examples:
* `with_names`: Doesn't actually needs to execute an action so it uses the `passing` one defined in [modifiers.py#L684](./modifiers.py#L684) and registered in [taxonomy.py#L35](./taxonomy.py#L35). The actual change of this modifier is to use a different seializer (`SerializerDetail.TAXONOMY_DETAIL_NAMES`)
* `filter_by_key_species`: Defined in [modifiers.py#L249](./modifiers.py#L249) and registered in [taxonomy.py#L96](./taxonomy.py#L96). It doesn't require to replace the current queryset, but adds a new filter to it. 
* `filter_by_entry`: Defined in [modifiers.py#L255](./modifiers.py#L249) and registered in [taxonomy.py#L38](./taxonomy.py#L96). It replaces the current queryset, because it uses the model TaxonomyPerEntry, which doesn't correspond to any of the main endpoints. It is registered using its own serializer (`SerializerDetail.TAXONOMY_PER_ENTRY`) 
* 
