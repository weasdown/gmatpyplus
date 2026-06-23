from math import sqrt

from gmatpyplus import gmat


class Rvector3:
    def __init__(self, e1: float | None = None, e2: float | None = None, e3: float | None = None):
        """Provides linear algebra operations for 3-element float vectors."""
        self.gmat_obj: gmat.Rvector3 = gmat.Rvector3()

        for index, element in enumerate([e1, e2, e3]):
            if element is not None:
                self.gmat_obj[index] = element

    def __repr__(self):
        return str(self._values)

    @property
    def _e1(self) -> float:
        return self.gmat_obj[0]

    @_e1.setter
    def _e1(self, e1: float) -> None:
        self.gmat_obj[0] = e1

    @property
    def _e2(self) -> float:
        return self.gmat_obj[1]

    @_e2.setter
    def _e2(self, e1: float) -> None:
        self.gmat_obj[1] = e1

    @property
    def _e3(self) -> float:
        return self.gmat_obj[2]

    @_e3.setter
    def _e3(self, e1: float) -> None:
        self.gmat_obj[2] = e1

    def Get(self, index: int) -> float:
        return self._values[index]

    def GetMagnitude(self) -> float:
        return sqrt(self._e1 ** 2 + self._e2 ** 2 + self._e3 ** 2)

    def Set(self, e1: float, e2: float, e3: float) -> None:
        self._e1 = e1
        self._e2 = e2
        self._e3 = e3

    @property
    def _values(self) -> list[float]:
        return [self._e1, self._e2, self._e3]
