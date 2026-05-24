from __future__ import annotations

from typing import Union

import gmatpyplus as gp
from gmatpyplus import gmat
from gmatpyplus import utils as u
from gmatpyplus.hardware import Hardware


class Thruster(Hardware):
    def __init__(self, fuel_type: str, name: str,
                 tanks: str | gp.FuelTank | gmat.FuelTank | list[gp.FuelTank] | list[gmat.FuelTank],
                 mix_ratio: int | float | list[int | float] = None):
        self.fuel_type = fuel_type
        self.thruster_type: str = f'{self.fuel_type}Thruster'  # 'ChemicalThruster' or 'ElectricThruster'
        super().__init__(self.thruster_type, name)

        self.spacecraft: gp.Spacecraft | None = None

        self.tanks: list[gp.ChemicalTank | gp.ElectricTank] | None = tanks
        self.mix_ratio: list[int | float] = [mix_ratio] if isinstance(mix_ratio, (int, float)) else mix_ratio
        if isinstance(self.tanks, str | gp.FuelTank | gmat.FuelTank):
            if mix_ratio is not None and self.mix_ratio != 1:
                raise AttributeError(f'Invalid mix_ratio {self.mix_ratio} given for a single tank')
            self.mix_ratio = [1]
            self.SetField('MixRatio', self.mix_ratio)
            if isinstance(self.tanks, str):
                self.SetField('Tank', self.tanks)
            elif isinstance(self.tanks, gp.FuelTank | gmat.Tank):
                self.SetField('Tank', self.tanks.GetName())
        elif isinstance(self.tanks, list):
            if mix_ratio is None:
                raise AttributeError('mix_ratio must be given if multiple tanks have been given')
            else:
                tank_names = [tank.GetName() for tank in self.tanks]
                self.SetField('Tank', tank_names)

        self._decrement_mass = self.decrement_mass

        self.Initialize()

    def __repr__(self):
        return f'A {self.thruster_type} with name {self.name}'

    @staticmethod
    def from_dict(fuel_type: str, thr_dict: dict[str, Union[str, int, float]]):
        name = thr_dict.get('Name')
        tanks = thr_dict.get('Tanks')
        if fuel_type == 'Chemical':
            thr = ChemicalThruster(name, tanks)
        elif fuel_type == 'Electric':
            thr = ElectricThruster(thr_dict['Name'], tanks)
        else:
            raise SyntaxError(f'Invalid fuel_type found in Thruster.from_dict: {fuel_type}.'
                              f"\nMust be 'Chemical' or 'Electric'")

        fields: list[str] = list(thr_dict.keys())
        fields.remove('Name')
        fields.remove('Tanks')

        # TODO convert to thr.SetFields
        for field in fields:
            if field == 'Tanks':
                thr.SetField('Tank', thr_dict[field])
            else:
                thr.SetField(field, thr_dict[field])
            setattr(thr, field, thr_dict[field])

        thr.Validate()

        return thr

    def attach_to_sat(self, sat: gp.Spacecraft):
        self.spacecraft = sat
        self.spacecraft.add_thrusters([self.gmat_obj])

    def attach_to_tanks(self, tanks: list[gp.ChemicalTank | gp.ElectricTank]):
        u.extract_gmat_obj(self).SetField('Tank', tanks)

    @property
    def decrement_mass(self):
        gmat_value = self.GetField('DecrementMass')
        if gmat_value == 'false':
            return False
        elif gmat_value == 'true':
            return True
        else:
            raise AttributeError(f'Could not get valid DecrementMass value from GMAT object. Value found: {gmat_value}')

    @decrement_mass.setter
    def decrement_mass(self, true_false: bool):
        if type(true_false) is not bool:
            raise SyntaxError('decrement_mass takes either True or False')

        self._decrement_mass = true_false
        self.SetField('DecrementMass', true_false)


class ChemicalThruster(Thruster):
    def __init__(self, name: str, tanks: str | gp.ChemicalTank | gp.gmat.ChemicalTank |
                                         list[gp.ChemicalTank] | list[gp.gmat.ChemicalTank]):
        super().__init__('Chemical', name, tanks)

        self.Validate()
        self.Initialize()

    @classmethod
    def from_dict(cls, cp_thr_dict: dict) -> gp.ChemicalThruster | None:
        if cp_thr_dict != {}:
            cp_thr: ChemicalThruster = Thruster.from_dict('Chemical', cp_thr_dict)
            cp_thr.Validate()
            return cp_thr
        else:
            return None


class ElectricThruster(Thruster):
    def __init__(self, name: str, tanks: str | gp.ElectricTank | gp.gmat.ElectricTank |
                                         list[gp.ElectricTank] | list[gp.gmat.ElectricTank]):
        super().__init__('Electric', name, tanks)
        self.Initialize()

    @classmethod
    def from_dict(cls, ep_thr_dict: dict) -> gp.ElectricThruster | None:
        if ep_thr_dict != {}:
            ep_thr = Thruster.from_dict('Electric', ep_thr_dict)
            ep_thr.Validate()
            return ep_thr
        else:
            return None

    # @property
    # def mix_ratio(self):
    #     return self._mix_ratio

    # @mix_ratio.setter
    # def mix_ratio(self, mix_ratio: list[int]):
    #     if all(isinstance(ratio, int) for ratio in mix_ratio):  # check that all mix_ratio elements are of type int
    #         # convert GMAT's Tanks field (with curly braces) to a Python list of strings
    #         tanks_list = [item.strip("'") for item in self.gmat_obj.GetField('Tank')[1:-1].split(', ')]
    #         if len(mix_ratio) != len(tanks_list):
    #             raise SyntaxError('Number of mix ratios provided does not equal existing number of tanks')
    #         else:
    #             if tanks_list and any(ratio == -1 for ratio in mix_ratio):  # tank(s) assigned but a -1 ratio given
    #                 raise SyntaxError('Cannot have -1 mix ratio if tank(s) assigned to thruster')
    #             else:
    #                 self._mix_ratio = mix_ratio
    #     else:
    #         raise SyntaxError('All elements of mix_ratio must be of type int')
