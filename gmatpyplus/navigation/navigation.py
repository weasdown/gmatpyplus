import numpy as np

import gmatpyplus as gp


## TODO implement Antenna class
class Antenna(gp.Imager):
    def __init__(self, name: str, boresight: np.ndarray | list = np.array([1, 0, 0])):
        ## FIXME creates an Imager called "Antenna" rather than passing the type name and name.
        super().__init__('Antenna', name)

        self._boresight = np.array(boresight) if not isinstance(boresight, np.ndarray) else boresight

        # ## TODO implement Antenna.__init__()
        # raise NotImplementedError
