from __future__ import annotations

from typing import TypeVar, Generic
import logging
from enum import Enum
from typing import Union

import numpy as np

import gmatpyplus as gp
from gmatpyplus import gmat
from gmatpyplus.basics import GmatObject
from gmatpyplus.hardware import Imager, HardwareException, NuclearPowerSystem, SolarPowerSystem
from gmatpyplus.orbit import OrbitState
from gmatpyplus.utils import (gmat_str_to_py_str, gmat_field_string_to_list,
                              list_to_gmat_field_string, rvector6_to_list)

T = TypeVar('T')


class Spacecraft(GmatObject):
    """A spacecraft object."""

    class SpacecraftHardware:
        """
        Container for a Spacecraft's hardware objects.
        """

        class PropList:
            def __init__(self, name: str):
                self.name = name
                self.chemical = []
                self.electric = []

            def __repr__(self):
                return (f'A set of Spacecraft {self.name}:'
                        f'\n\t- chemical:     {self.chemical},'
                        f'\n\t- Electrical:   {self.electric}')

        def __init__(self,
                     chem_tanks: list[gp.ChemicalTank] = None,
                     elec_tanks: list[gp.ElectricTank] = None,
                     chem_thrusters: list[gp.ChemicalThruster] = None,
                     elec_thrusters: list[gp.ElectricThruster] = None,
                     solar_power_system: gp.SolarPowerSystem = None,
                     nuclear_power_system: gp.NuclearPowerSystem = None,
                     imagers: list[gp.Imager] = None):
            self.chem_tanks: list[gp.ChemicalTank] = chem_tanks if chem_tanks is not None else []
            self.elec_tanks: list[gp.ElectricTank] = elec_tanks if elec_tanks is not None else []

            self.chem_thrusters: list[gp.ChemicalThruster] = chem_thrusters if chem_thrusters is not None else []
            self.elec_thrusters: list[gp.ElectricThruster] = elec_thrusters if elec_thrusters is not None else []

            self.solar_power_system: gp.SolarPowerSystem | None = None if solar_power_system is None\
                else solar_power_system
            self.nuclear_power_system: gp.NuclearPowerSystem | None = None if nuclear_power_system is None\
                else nuclear_power_system

            self.imagers: list[Imager] = imagers if imagers is not None else []

        def __repr__(self):
            return (f'{type(self).__name__} object with the following parameters:'
                    # f'\n- Spacecraft: {self.Spacecraft.GetName()},'
                    f'\n- ChemicalTanks: {self.chem_tanks},'
                    f'\n- ElectricTanks: {self.elec_tanks},'
                    f'\n- ChemicalThrusters: {self.chem_thrusters},'
                    f'\n- ElectricThrusters: {self.elec_thrusters},'
                    f'\n- SolarPowerSystem: {self.solar_power_system},'
                    f'\n- NuclearPowerSystem: {self.nuclear_power_system},'
                    f'\n- Imagers: {self.imagers}')

        @classmethod
        def from_dict(cls, hw: dict) -> Spacecraft.SpacecraftHardware:
            sc_hardware = cls()

            # parse ChemicalTanks
            cp_tanks_list: list[dict] = hw.get('ChemicalTanks', [{}])
            cp_tanks_objs = []
            for index, cp_tank in enumerate(cp_tanks_list):
                cp_tanks_objs.append(ChemicalTank.from_dict(cp_tank))
            sc_hardware.chem_tanks = cp_tanks_objs if cp_tanks_objs != [None] else None

            # parse ElectricTanks
            ep_tanks_list: list[dict] = hw.get('ElectricTanks', [{}])
            ep_tanks_objs = []
            for index, ep_tank in enumerate(ep_tanks_list):
                ep_tanks_objs.append(ElectricTank.from_dict(ep_tank))
            sc_hardware.elec_tanks = ep_tanks_objs if ep_tanks_objs != [None] else None

            # parse ChemicalThrusters
            cp_thrusters_list: list[dict] = hw.get('ChemicalThrusters', [{}])
            cp_thruster_objs = []
            for index, cp_thruster in enumerate(cp_thrusters_list):
                cp_thruster_objs.append(ChemicalThruster.from_dict(cp_thruster))
            sc_hardware.chem_thrusters = cp_thruster_objs if cp_thruster_objs != [None] else None

            # parse ElectricThrusters
            ep_thrusters_list: list[dict] = hw.get('ElectricThrusters', [{}])
            ep_thruster_objs = []
            for index, ep_thruster in enumerate(ep_thrusters_list):
                ep_thruster_objs.append(ElectricThruster.from_dict(ep_thruster))
            sc_hardware.elec_thrusters = ep_thruster_objs if ep_thruster_objs != [None] else None

            # parse solar power systems
            solar_power_systems: dict = hw.get('SolarPowerSystem', {})
            sc_hardware.solar_power_system = gp.SolarPowerSystem.from_dict(solar_power_systems)

            # TODO: parse nuclear_power_system, imager

            return sc_hardware

        @property
        def ChemicalTanks(self):
            return self.chem_tanks

        @property
        def ElectricTanks(self):
            return self.elec_tanks

        @property
        def ChemicalThrusters(self):
            return self.chem_thrusters

        @property
        def ElectricThrusters(self):
            return self.elec_thrusters

    def __init__(self, name, hardware: SpacecraftHardware = None):
        super().__init__('Spacecraft', name)
        self.was_propagated = False  # determines whether to use GetObject() or GetRuntimeObject()

        # TODO: add elements for non-Cartesian orbit states (e.g. 'SMA', 'ECC' for Kep) - get OrbitState allowed fields
        _allowed_fields = set()
        _gmat_allowed_fields = ['NAIFId', 'NAIFIdReferenceFrame', 'SpiceFrameId', 'OrbitSpiceKernelName',
                                'AttitudeSpiceKernelName',
                                'SCClockSpiceKernelName', 'FrameSpiceKernelName', 'OrbitColor', 'TargetColor',
                                'Epoch', 'X', 'Y', 'Z', 'VX',
                                'VY', 'VZ', 'StateType', 'DisplayStateType', 'AnomalyType', 'CoordinateSystem',
                                'DryMass', 'DateFormat',
                                'OrbitErrorCovariance', 'ProcessNoiseModel', 'Cd', 'Cr', 'CdSigma', 'CrSigma',
                                'DragArea', 'SRPArea', 'Tanks',
                                'Thrusters', 'PowerSystem', 'ExtendedMassPropertiesModel', 'Id', 'SPADSRPFile',
                                'SPADSRPScaleFactor',
                                'SPADSRPInterpolationMethod', 'SPADSRPScaleFactorSigma', 'SPADDragFile',
                                'SPADDragScaleFactor',
                                'SPADDragInterpolationMethod', 'SPADDragScaleFactorSigma',
                                'AtmosDensityScaleFactor',
                                'AtmosDensityScaleFactorSigma', 'AddPlates', 'AddHardware', 'SolveFors',
                                'NPlateSRPEquateAreaCoefficients',
                                'ModelFile', 'ModelOffsetX', 'ModelOffsetY', 'ModelOffsetZ', 'ModelRotationX',
                                'ModelRotationY',
                                'ModelRotationZ', 'ModelScale', 'Attitude']

        # TODO: get string attr names for non-GMAT attrs
        _allowed_fields.update(_gmat_allowed_fields,
                               ['Name', 'Orbit', 'Hardware'])

        self.hardware: Spacecraft.SpacecraftHardware = self.SpacecraftHardware() if hardware is None else hardware

        # TODO confirm fixed - FIXME - not being updated by from_dict()
        # Setup tanks
        self.chem_tanks: list[ChemicalTank] = []
        if self.hardware.chem_tanks:
            if isinstance(self.hardware.chem_tanks, list):
                for tank in self.hardware.chem_tanks:
                    self.chem_tanks.append(tank)
                    tank.attach_to_sat(self)
            else:
                # self.hardware.chem_tanks is of an inappropriate type.
                raise TypeError(f'self.hardware.chem_tanks should be a list[ChemicalTank] but was '
                                f'{type(self.hardware.chem_tanks).__name__}')

        self.elec_tanks: list[ElectricTank] = []
        if self.hardware.elec_tanks:
            if isinstance(self.hardware.elec_tanks, list):
                for tank in self.hardware.elec_tanks:
                    self.elec_tanks.append(tank)
                    tank.attach_to_sat(self)
            else:
                # self.hardware.elec_tanks is of an inappropriate type.
                raise TypeError(f'self.hardware.elec_tanks should be a list[ElectricTank] but was '
                                f'{type(self.hardware.elec_tanks).__name__}')

        # Setup thrusters
        self.chem_thrusters: list[ChemicalThruster] = []
        if self.hardware.chem_thrusters:
            if isinstance(self.hardware.chem_thrusters, list):
                for thruster in self.hardware.chem_thrusters:
                    self.chem_thrusters.append(thruster)
                    thruster.attach_to_sat(self)
            else:
                # self.hardware.chem_thrusters is of an inappropriate type.
                raise TypeError(f'self.hardware.chem_thrusters should be a list[ChemicalThruster] but was '
                                f'{type(self.hardware.chem_thrusters).__name__}')

        self.elec_thrusters: list[ElectricThruster] = []
        if self.hardware.elec_thrusters:
            if isinstance(self.hardware.elec_thrusters, list):
                for thruster in self.hardware.elec_thrusters:
                    self.elec_thrusters.append(thruster)
                    thruster.attach_to_sat(self)
            else:
                # self.hardware.elec_thrusters is of an inappropriate type.
                raise TypeError(f'self.hardware.elec_thrusters should be a list[ElectricThruster] but was '
                                f'{type(self.hardware.elec_thrusters).__name__}')

        # Setup power systems
        self.solar_power_system: SolarPowerSystem | None = None
        if self.hardware.solar_power_system is not None:
            if isinstance(self.hardware.solar_power_system, SolarPowerSystem):
                self.solar_power_system = self.hardware.solar_power_system
                self.solar_power_system.attach_to_sat(self)
            else:
                # self.hardware.solar_power_system is of an inappropriate type.
                raise TypeError(f'self.hardware.solar_power_system should be a SolarPowerSystem but was '
                                f'{type(self.hardware.solar_power_system).__name__}')

        self.nuclear_power_system: NuclearPowerSystem | None = None
        if self.hardware.nuclear_power_system is not None:
            if isinstance(self.hardware.nuclear_power_system, NuclearPowerSystem):
                self.nuclear_power_system = self.hardware.nuclear_power_system
                self.nuclear_power_system.attach_to_sat(self)
            else:
                # self.hardware.nuclear_power_system is of an inappropriate type.
                raise TypeError(f'self.hardware.nuclear_power_system should be a NuclearPowerSystem but was '
                                f'{type(self.hardware.nuclear_power_system).__name__}')

        # Setup imagers
        self.imagers: list[Imager] = []
        if self.hardware.imagers is not None:
            if isinstance(self.hardware.imagers, list):
                for imager in self.hardware.imagers:
                    self.imagers.append(imager)
                    imager.attach_to_sat(self)
            else:
                # self.hardware.imagers is of an inappropriate type.
                raise TypeError(f'self.hardware.imagers should be a list[Imager] but was '
                                f'{type(self.hardware.imagers).__name__}')

        self.orbit = None
        self.dry_mass = self.GetField('DryMass')

        gp.Initialize()
        self.Initialize()

    def __repr__(self):
        return f'Spacecraft with name {self._name}'

    @classmethod
    def from_dict(cls, specs_dict: dict):
        # TODO bugfix: StateType and DryMass values in dict not being used. Add parsing of CoordSys with correct case.

        # Get spacecraft name
        specs = specs_dict.copy()  # take a copy of the dictionary to avoid editing the original
        try:
            name = specs['Name']
            specs.pop('Name')
        except KeyError:
            raise SyntaxError('Spacecraft name required')

        sc = cls(name)  # create an instance of the Spacecraft class

        # Get spacecraft hardware specs
        try:
            hardware = specs['Hardware']
            specs.pop('Hardware')
        except KeyError:
            logging.info('No hardware parameters specified in Spacecraft dictionary - none will be built')
            hardware = {}

        hardware_obj = Spacecraft.SpacecraftHardware.from_dict(hardware)  # build wrapper Hardware object from specs
        sc.hardware = sc.update_hardware(hardware_obj)  # apply the new Hardware object to the spacecraft

        # use any Orbit params specified in the specs dictionary
        try:
            orbit = specs['Orbit']
            specs.pop('Orbit')
        except KeyError:
            logging.info('No orbit parameters specified in Spacecraft dictionary - none will be built')
            orbit = {}

        if not orbit:  # orbit dict is empty
            sc.orbit = OrbitState()
        else:
            sc.orbit = OrbitState.from_dict(orbit)  # build wrapper Orbit object from specs
        sc.orbit.apply_to_spacecraft(sc)  # apply the new Hardware object to the spacecraft

        # Apply remaining specs
        for spec in specs:
            attr_name = gmat_str_to_py_str(spec, True)
            setattr(sc, attr_name, specs[spec])
            sc.SetField(spec, specs[spec])

        gp.Initialize()  # initialize GMAT as a whole
        sc.Initialize()  # initialize the completed Spacecraft object
        sc.Validate()  # validate the completed Spacecraft object
        return sc

    def update_from_runtime_object(self):
        self.gmat_obj = gmat.GetRuntimeObject(self._name)
        self.was_propagated = True

    def update_hardware(self, hardware: SpacecraftHardware):
        self.hardware = hardware

        # Attach thrusters and tanks to the Spacecraft
        if self.hardware.chem_thrusters is not None:
            for thruster in self.hardware.chem_thrusters:
                # if not thruster:
                #     raise RuntimeError(f"No chemical thrusters found, chemical thruster list is: "
                #                        f"{self.chem_thrusters}\n{self.hardware.chem_thrusters}")
                if thruster is not None:
                    thruster.attach_to_sat(self)
                    thruster.attach_to_tanks(thruster.tanks)

        if self.hardware.elec_thrusters is not None:
            for thruster in self.hardware.elec_thrusters:
                # if not thruster:
                #     raise RuntimeError(f"No electric thrusters found, electric thruster list is:
                #     {self.elec_thrusters}")
                if thruster is not None:
                    thruster.attach_to_sat(self)
                    thruster.attach_to_tanks(thruster.tanks)

        if self.hardware.chem_tanks is not None:
            for tank in self.hardware.chem_tanks:
                if tank is not None:
                    tank.attach_to_sat(self)

        if self.hardware.elec_tanks is not None:
            for tank in self.hardware.elec_tanks:
                if tank is not None:
                    tank.attach_to_sat(self)

        self.chem_thrusters = self.hardware.chem_thrusters
        self.elec_thrusters = self.hardware.elec_thrusters

        self.chem_tanks = self.hardware.chem_tanks
        self.elec_tanks = self.hardware.elec_tanks

        self.solar_power_system = self.hardware.solar_power_system
        if self.solar_power_system is not None:
            self.hardware.solar_power_system.attach_to_sat(self)

        return self.hardware

    def update_orbit(self, orbit: OrbitState):
        self.orbit = orbit
        pass

    # TODO re-implement optional coord_sys argument that specifies a coord system that the state will be expressed in
    #  (e.g. MarsInertial for Tut04_Mars_B-Plane_Targeting.py)
    def GetState(self, state_type: str = 'Current') -> list[float]:
        # Get latest data (e.g. from mission run)
        up_to_date_obj = self.GetObject()

        allowed_state_types: list[str] = list(gp.OrbitState().allowed_state_elements.keys())
        if state_type != 'Current':
            if state_type not in allowed_state_types:
                raise AttributeError(f'Given state_type is invalid. Valid options are: '
                                     f'{[state for state in allowed_state_types]}')
            up_to_date_obj.SetField('DisplayStateType', state_type)

        state: list[float | None] = [None] * 6
        for i in range(13, 19):
            state[i - 13] = float(up_to_date_obj.GetField(i))  # int field refs used to be state type agnostic

        return state

    def GetKeplerianState(self):
        return rvector6_to_list(self.gmat_obj.GetKeplerianState())

    def GetCartesianState(self):
        return rvector6_to_list(self.gmat_obj.GetCartesianState())

    def GetCoordinateSystem(self) -> gp.OrbitState.CoordinateSystem:
        return gp.OrbitState.CoordinateSystem.from_sat(self)

    @property
    def ChemicalThrusters(self):
        return self.hardware.ChemicalThrusters

    @property
    def ElectricThrusters(self):
        return self.hardware.ElectricThrusters

    @property
    def ChemicalTanks(self):
        return self.hardware.ChemicalTanks

    @property
    def ElectricTanks(self):
        return self.hardware.ElectricTanks

    def add_tanks(self, tanks: gp.FuelTank | list[gp.FuelTank] | str) -> bool:
        """
        Add a tank object to a Spacecraft's list of Tanks.

        Note: GMAT Spacecraft Tanks field takes a string containing strings for each tank, e.g.:
         "'ChemicalTank1', 'ElectricTank1'". This is handled by this method.

        :type tanks: list[ChemicalTank | ElectricTank]
        :param tanks:
        :return:
        """
        current_tanks_value: str = self.GetField('Tanks')
        current_tanks_list: list = gmat_field_string_to_list(current_tanks_value)

        # Add tanks by getting name of each tank, adding it to a list, then attaching this list to end of existing one
        if isinstance(tanks, str):
            current_tanks_list = [tanks]
            tank = gmat.GetObject(tanks)
            self.SetStringParameter(104, tank.GetName())  # 104 for sat's ADD_HARDWARE
            current_tanks_list.extend(tank.GetName())
        elif isinstance(tanks, gp.FuelTank):
            self.SetStringParameter(104, tanks.GetName())  # 104 for sat's ADD_HARDWARE
            current_tanks_list.append(tanks.GetName())
        else:  # tanks is a list of Tanks
            for tank in tanks:
                tanks_to_set: list = [tank.GetName()]
                current_tanks_list.extend(tanks_to_set)
                self.SetStringParameter(104, tank.GetName())  # 104 for sat's ADD_HARDWARE

        value = list_to_gmat_field_string(current_tanks_list)
        self.SetField('Tanks', value)

        return True

    def add_thrusters(self, thrusters: list[ChemicalThruster | ElectricThruster] | str | gp.Thruster) -> bool:
        current_thrusters_value: str = self.GetField('Thrusters')
        current_thrusters_list: list = gmat_field_string_to_list(current_thrusters_value)

        # Add tanks by getting name of each tank, adding it to a list, then attaching this list to end of existing one
        if isinstance(thrusters, str):
            thruster: gmat.GmatBase = gmat.GetObject(thrusters)
            self.SetStringParameter(104, thruster.GetName())  # 104 for sat's ADD_HARDWARE
        elif isinstance(thrusters, gp.Thruster):
            self.SetStringParameter(104, thrusters.GetName())  # 104 for sat's ADD_HARDWARE
        else:
            for thruster in thrusters:
                thrusters_to_set: list = [thruster.GetName()]
                current_thrusters_list.extend(thrusters_to_set)
                self.SetStringParameter(104, thruster.GetName())  # 104 for sat's ADD_HARDWARE

        value = list_to_gmat_field_string(current_thrusters_list)
        self.SetField('Thrusters', value)

        return True

    def add_sps(self, solar_power_system: gp.SolarPowerSystem | gp.SolarPowerSystem) -> bool:
        self.SetStringParameter(104, solar_power_system.GetName())  # 104 for sat's ADD_HARDWARE
        if self.GetField('PowerSystem') == '':
            self.SetField('PowerSystem', solar_power_system.GetName())
            return True
        else:
            return False

    def add_nps(self, nuclear_power_system: gp.NuclearPowerSystem | gp.NuclearPowerSystem) -> bool:
        self.SetStringParameter(104, nuclear_power_system.GetName())  # 104 for sat's ADD_HARDWARE
        if self.GetField('PowerSystem') == '':
            self.SetField('PowerSystem', nuclear_power_system.GetName())
            return True
        else:
            return False
