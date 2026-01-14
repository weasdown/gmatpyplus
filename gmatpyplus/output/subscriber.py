from gmatpyplus import GmatObject


class Subscriber(GmatObject):
    def __init__(self, obj_type: str, name: str):
        super().__init__(obj_type, name)
