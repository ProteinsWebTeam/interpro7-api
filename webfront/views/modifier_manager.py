class ModifierManager:
    def __init__(self, general_handler=None):
        self.general_handler = general_handler
        self.modifiers = {}
        self.payload = None
        self.serializer = None
        self.many = False

    def register(self, parameter, action,
                 use_model_as_payload=False,
                 serializer=None,
                 many=False
                 ):
        self.modifiers[parameter] = {
            "action": action,
            "use_model_as_payload": use_model_as_payload,
            "serializer": serializer,
            "many": many,
        }

    def unregister(self, parameter):
        if parameter in self.modifiers:
            del self.modifiers[parameter]

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
                self.payload = self.modifiers[modifier]["action"](param, self.general_handler)
                self.serializer = self.modifiers[modifier]["serializer"]
                self.many = self.many or self.modifiers[modifier]["many"]
        use_model_as_payload = False
        for modifier in payload_modifiers:
            param = request.query_params.get(modifier)
            if param is not None:
                self.payload = self.modifiers[modifier]["action"](param, self.general_handler)
                self.many = self.many or self.modifiers[modifier]["many"]
                if self.serializer is None:
                    self.serializer = self.modifiers[modifier]["serializer"]
                else:
                    raise(Exception, "only one modifier can change the shape of the payload")
                use_model_as_payload = True
        return use_model_as_payload
