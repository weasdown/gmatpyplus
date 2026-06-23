from math import sqrt


class Rvector3:
    def __init__(self, e1: float | None = None, e2: float | None = None, e3: float | None = None):
        """Provides linear algebra operations for 3-element float vectors."""
        self._e1: float = e1 if e1 is not None else 0
        self._e2: float = e2 if e2 is not None else 0
        self._e3: float = e3 if e3 is not None else 0

        self._values: list[float] = [self._e1, self._e2, self._e3]

    def __repr__(self):
        return str(self._values)

    def Get(self, index: int) -> float:
        return self._values[index]

    def GetMagnitude(self) -> float:
        return sqrt(self._e1 ** 2 + self._e2 ** 2 + self._e3 ** 2)

    def Set(self, e1: float, e2: float, e3: float) -> None:
        self._e1 = e1
        self._e2 = e2
        self._e3 = e3
