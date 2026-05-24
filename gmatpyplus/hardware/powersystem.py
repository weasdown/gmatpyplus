from __future__ import annotations

from typing import Union

import gmatpyplus as gp
from gmatpyplus import gmat
from gmatpyplus.hardware import Hardware


## TODO implement PowerSystem class
class PowerSystem(Hardware):
    pass


class NuclearPowerSystem(gp.GmatObject):
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
            return self.spacecraft.add_nps(self)
        else:
            return False

    @staticmethod
    def from_dict(nps_dict: dict[str, Union[str, int, float]]):
        try:
            name: str = str(nps_dict['Name'])
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


class SolarPowerSystem(gp.GmatObject):
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
            return self.spacecraft.add_sps(self)
        else:
            return False

    @staticmethod
    def from_dict(sps_dict: dict[str, Union[str, int, float]]):
        specs = sps_dict.copy()  # take a copy of the dictionary to avoid editing the original
        try:
            name: str = str(specs.get('Name', 'DefaultSolarPowerSystem'))
            specs.pop('Name')
        except KeyError:
            raise SyntaxError('SolarPowerSystem name required')

        sps = SolarPowerSystem(name)

        fields: list[str] = list(sps_dict.keys())
        fields.remove('Name')

        # TODO convert to sps.SetFields
        for field in fields:
            sps.SetField(field, sps_dict[field])
            setattr(sps, field, sps_dict[field])

        sps.Validate()

        return sps
