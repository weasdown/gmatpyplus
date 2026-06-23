from gmatpyplus.force_model.physical_model import PhysicalModel


class FiniteThrust(PhysicalModel):
    def __init__(self, name: str = 'FiniteThrust'):
        super().__init__('FiniteThrust', name)
        raise NotImplementedError
