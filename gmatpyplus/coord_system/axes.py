from foundation import GmatObject


# TODO align this class with the GMAT source code's AxisSystem class (including renaming here). This will then become the parent type of the InertialAxes and DynamicAxes types.
# TODO complete - will be able to create each type of Axes, for use in CoordinateSystem
class Axes(GmatObject):
    def __init__(self, axes_type: str, name: str):
        super().__init__(axes_type, name)
        self.Initialize()
