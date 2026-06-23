from __future__ import annotations

import numpy as np

from gmatpyplus.foundation import GmatObject


class Hardware(GmatObject):
    def __init__(self, obj_type: str, name: str):
        """
        Base class used for spacecraft hardware.

        This class is the base class for spacecraft fuel tanks, thrusters, and other hardware elements that can be added to a spacecraft in GMAT.  It contains data structures that locate the center of the element in the spacecraft's body coordinate system (BCS) and that orient the elements in the same system.

        This class has been modified (May 2019) to allow modeling fields of view. FOV modeling includes determining whether a unit vector is in the FOV, and returning the field of view mask for graphics display.

        Notes: The current builds of GMAT do not model torques or moments of inertia, so the parameter access for those pieces is commented out.
        """
        super().__init__(obj_type, name)

    @property
    def direction(self) -> np.ndarray:
        """Principle direction for hardware element on the spacecraft."""
        internal = self.gmat_obj.GetDirection()  # gmat.Rvector3
        direction: np.ndarray = np.array([internal.Get(0), internal.Get(1), internal.Get(2)],
                                         dtype=float)
        return direction

    def GetDirection(self) -> np.ndarray:
        return self.direction

    def GetLocation(self) -> np.ndarray:
        return self.location

    def GetRotationMatrix(self) -> np.ndarray:
        return self.rotation_matrix

    def GetSecondDirection(self) -> np.ndarray:
        return self.second_direction

    # noinspection PyMethodMayBeStatic
    def HasFOV(self) -> bool:
        return False

    @property
    def location(self) -> np.ndarray:
        """Location of center of the hardware element on the spacecraft, in meters."""
        location_vec = self.gmat_obj.GetLocation()  # gmat.Rvector3
        location: np.ndarray = np.array([location_vec.Get(0), location_vec.Get(1), location_vec.Get(2)],
                                        dtype=float)
        return location

    @property
    def rotation_matrix(self) -> np.ndarray:
        """Rotation from body to hardware frame."""
        internal = self.gmat_obj.GetRotationMatrix()  # gmat.Rvector3
        rotation_matrix: np.ndarray = np.array(
            [[internal[0, 0], internal[0, 1], internal[0, 2]],
             [internal[1, 0], internal[1, 1], internal[1, 2]],
             [internal[2, 0], internal[2, 1], internal[2, 2]]])
        return rotation_matrix

    @property
    def second_direction(self) -> np.ndarray:
        """Secondary direction, to complete the orientation."""
        internal = self.gmat_obj.GetSecondDirection()  # gmat.Rvector3
        second_direction: np.ndarray = np.array([internal.Get(0), internal.Get(1), internal.Get(2)],
                                                dtype=float)
        return second_direction
