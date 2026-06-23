from gmatpyplus.foundation import GmatObject


class PhysicalModel(GmatObject):
    def __init__(self, obj_type: str, name: str):
        super().__init__(obj_type, name)
        # self.Initialize()
