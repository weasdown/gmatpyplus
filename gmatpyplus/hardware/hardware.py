from __future__ import annotations

from typing import Union

import numpy as np

import gmatpyplus as gp
from basics import GmatObject
from gmatpyplus import gmat


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


class NuclearPowerSystem(GmatObject):
    def __init__(self, name: str):
        super().__init__('NuclearPowerSystem', name)

        self.spacecraft = None

        # TODO add parsing of each field under Help()
        # self.Help()
        pass

    def __repr__(self):
        return f'A NuclearPowerSystem named "{self.GetName()}"'

    def attach_to_sat(self, sat: gp.Spacecraft | gmat.Spacecraft) -> bool:
        self.spacecraft = sat
        if sat.GetField('PowerSystem') == '':
            self.spacecraft.add_nps(self)
        else:
            return False

    @staticmethod
    def from_dict(nps_dict: dict[str, Union[str, int, float]]):
        try:
            name = nps_dict['Name']
        except KeyError:  # no name found - use default
            name = 'DefaultNuclearPowerSystem'
        nps = NuclearPowerSystem(name)

        fields: list[str] = list(nps_dict.keys())
        fields.remove('Name')

        # TODO convert to nps.SetFields
        for field in fields:
            nps.SetField(field, nps_dict[field])
            setattr(nps, field, nps_dict[field])

        nps.Validate()

        return nps


class SolarPowerSystem(GmatObject):
    def __init__(self, name: str):
        super().__init__('SolarPowerSystem', name)

        self.spacecraft = None

        # TODO add parsing of each field under Help()
        # self.Help()
        pass

    def __repr__(self):
        return f'A SolarPowerSystem named "{self.GetName()}"'

    def attach_to_sat(self, sat: gp.Spacecraft | gmat.Spacecraft):
        self.spacecraft = sat
        if sat.GetField('PowerSystem') == '':
            self.spacecraft.add_sps(self)
        else:
            return False
        pass

    @staticmethod
    def from_dict(sps_dict: dict[str, Union[str, int, float]]):
        if sps_dict == {}:
            return

        name = sps_dict.get('Name', 'DefaultSolarPowerSystem')
        sps = SolarPowerSystem(name)

        fields: list[str] = list(sps_dict.keys())
        fields.remove('Name')

        # TODO convert to sps.SetFields
        for field in fields:
            sps.SetField(field, sps_dict[field])
            setattr(sps, field, sps_dict[field])

        sps.Validate()

        return sps
