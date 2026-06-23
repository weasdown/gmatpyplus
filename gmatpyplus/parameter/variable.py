from gmatpyplus.parameter.parameter import Parameter


class Variable(Parameter):
    def __init__(self, name: str, value: int = None):
        super().__init__('Variable', name)

        self.value = value if value else 0
        self.SetStringParameter('Expression', str(self.value))

        self.Initialize()
