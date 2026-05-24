from __future__ import annotations

from typing import Union

import numpy as np

import gmatpyplus as gp
from basics import GmatObject
from gmatpyplus import gmat


## TODO implement Hardware class
class Hardware(gp.GmatObject):
    pass


class Antenna(GmatObject):
    def __init__(self, name: str, boresight: np.ndarray | list = np.array([1, 0, 0])):
        super().__init__('Antenna', name)

        self._boresight = np.array(boresight) if not isinstance(boresight, np.ndarray) else boresight

        raise NotImplementedError

# class Direction:
#     # TODO move to a more appropriate file
#     def __init__(self, x: int | float = 0, y: int | float = 0, z: int | float = 1):
#         self.x = x
#         self.y = y
#         self.z = z
