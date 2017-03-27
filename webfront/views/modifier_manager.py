class ModifierManager:
    def __init__(self, general_handler=None):
        self.general_handler = general_handler
        self.modifiers = {}
        self.payload = None
        self.serializer = None

    def register(self, parameter, action,
                 use_model_as_payload=False,
                 serializer=None
                 ):
        self.modifiers[parameter] = {
            "action": action,
            "use_model_as_payload": use_model_as_payload,
            "serializer":serializer
        }

    def execute(self, request):
        use_model_as_payload = False
        for modifier in self.modifiers:
            param = request.query_params.get(modifier)
            if param is not None:
                self.payload = self.modifiers[modifier]["action"](param, self.general_handler)
                self.serializer = self.modifiers[modifier]["serializer"]
                if self.modifiers[modifier]["use_model_as_payload"]:
                    use_model_as_payload = True
        return use_model_as_payload
