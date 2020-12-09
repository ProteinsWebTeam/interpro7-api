from webfront.views.custom import is_single_endpoint


class ModifierManager:
    def __init__(self, general_handler=None):
        self.general_handler = general_handler
        self.modifiers = {}
        self.payload = None
        self.serializer = None
        self.many = None
        self.search_size = None
        self.after_key = None
        self.before_key = None

    def register(
        self,
        parameter,
        action,
        use_model_as_payload=False,
        serializer=None,
        many=None,
        works_in_single_endpoint=True,
        works_in_multiple_endpoint=True,
    ):
        self.modifiers[parameter] = {
            "action": action,
            "use_model_as_payload": use_model_as_payload,
            "serializer": serializer,
            "many": many,
            "works_in_single_endpoint": works_in_single_endpoint,
            "works_in_multiple_endpoint": works_in_multiple_endpoint,
        }

    def unregister(self, parameter):
        if parameter in self.modifiers:
            del self.modifiers[parameter]

    def _check_modifier(self, modifier):
        single = is_single_endpoint(self.general_handler)
        if single and not self.modifiers[modifier]["works_in_single_endpoint"]:
            raise Exception(
                "The modifier '{}' doen't work on URLs of a single endpoint".format(
                    modifier
                )
            )
        if not single and not self.modifiers[modifier]["works_in_multiple_endpoint"]:
            raise Exception(
                "The modifier '{}' doen't work on URLs of multiple endpoints".format(
                    modifier
                )
            )

    def execute(self, request):
        payload_modifiers = {}
        queryset_modifiers = {}
        for p, m in self.modifiers.items():

            if m["use_model_as_payload"]:
                payload_modifiers[p] = m
            else:
                queryset_modifiers[p] = m
        for modifier in queryset_modifiers:
            param = request.query_params.get(modifier)
            if param is not None:
                self._check_modifier(modifier)
                self.payload = self.modifiers[modifier]["action"](
                    param, self.general_handler
                )
                self.serializer = self.modifiers[modifier]["serializer"]
                if self.modifiers[modifier]["many"] is not None:
                    self.many = (self.many is not None and self.many) or self.modifiers[
                        modifier
                    ]["many"]
        use_model_as_payload = False
        for modifier in payload_modifiers:
            param = request.query_params.get(modifier)
            if param is not None:
                self._check_modifier(modifier)
                self.payload = self.modifiers[modifier]["action"](
                    param, self.general_handler
                )
                if self.modifiers[modifier]["many"] is not None:
                    self.many = (self.many is not None and self.many) or self.modifiers[
                        modifier
                    ]["many"]
                if self.serializer is None:
                    self.serializer = self.modifiers[modifier]["serializer"]
                else:
                    raise (
                        Exception,
                        "only one modifier can change the shape of the payload",
                    )
                use_model_as_payload = True
        return use_model_as_payload
