from __future__ import annotations

import numpy as np

from gmatpyplus.foundation import GmatObject


## TODO implement Hardware class
class Hardware(GmatObject):
    def __init__(self, obj_type: str, name: str):
        super().__init__(obj_type, name)

        self._location: np.ndarray = self.location

    # TODO: implement Hardware.GetDirection() method
    def GetDirection(self) -> np.ndarray:
        raise NotImplementedError('Method on Hardware is not yet implemented.')

    # TODO: implement Hardware.GetLocation() method
    def GetLocation(self) -> np.ndarray:
        raise NotImplementedError('Method on Hardware is not yet implemented.')

    # TODO: implement Hardware.GetRotationMatrix() method
    def GetRotationMatrix(self) -> np.ndarray:
        raise NotImplementedError('Method on Hardware is not yet implemented.')

    # TODO: implement Hardware.GetSecondDirection() method
    def GetSecondDirection(self) -> np.ndarray:
        raise NotImplementedError('Method on Hardware is not yet implemented.')

    # TODO: implement Hardware.HasFOV() method
    def HasFOV(self) -> bool:
        raise NotImplementedError('Hardware.HasFOV() method is not yet implemented.')

    @property
    def location(self) -> np.ndarray:
        """Location of center of the hardware element on the spacecraft, in meters."""
        self._location = self.GetLocation()
        return self._location
