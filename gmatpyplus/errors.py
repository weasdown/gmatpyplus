class HardwareException(Exception):
    def __init__(self, details: str) -> None:
        super().__init__()
        self._details: str = details

    @property
    def details(self):
        return self._details

    def __repr__(self):
        return 'Hardware Exception Thrown: $details'
