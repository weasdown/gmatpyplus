from __future__ import annotations

import logging
from enum import Enum
from typing import TypeVar, Generic, Union, Callable

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

            self.solar_power_system: SolarPowerSystem | None = solar_power_system
            self.nuclear_power_system: NuclearPowerSystem | None = nuclear_power_system

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
            sc_hardware.chem_tanks = cp_tanks_objs if cp_tanks_objs != [None] else []

            # parse ElectricTanks
            ep_tanks_list: list[dict] = hw.get('ElectricTanks', [{}])
            ep_tanks_objs = []
            for index, ep_tank in enumerate(ep_tanks_list):
                ep_tanks_objs.append(ElectricTank.from_dict(ep_tank))
            sc_hardware.elec_tanks = ep_tanks_objs if ep_tanks_objs != [None] else []

            # parse ChemicalThrusters
            cp_thrusters_list: list[dict] = hw.get('ChemicalThrusters', [{}])
            cp_thruster_objs = []
            for index, cp_thruster in enumerate(cp_thrusters_list):
                cp_thruster_objs.append(ChemicalThruster.from_dict(cp_thruster))
            sc_hardware.chem_thrusters = cp_thruster_objs if cp_thruster_objs != [None] else []

            # parse ElectricThrusters
            ep_thrusters_list: list[dict] = hw.get('ElectricThrusters', [{}])
            ep_thruster_objs = []
            for index, ep_thruster in enumerate(ep_thrusters_list):
                ep_thruster_objs.append(ElectricThruster.from_dict(ep_thruster))
            sc_hardware.elec_thrusters = ep_thruster_objs if ep_thruster_objs != [None] else []

            # parse solar power systems
            solar_power_systems: dict = hw.get('SolarPowerSystem', {})
            sc_hardware.solar_power_system = gp.SolarPowerSystem.from_dict(solar_power_systems)

            # FIXME: parse nuclear_power_system, imager
            if hw.get('NuclearPowerSystem') is not None:
                raise NotImplementedError(
                    'Adding a NuclearPowerSystem to SpacecraftHardware from a dictionary is not yet supported.')
            if hw.get('Imagers') is not None:
                raise NotImplementedError(
                    'Adding Imagers to SpacecraftHardware from a dictionary is not yet supported.')

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

        self.hardware: Spacecraft.SpacecraftHardware = hardware if hardware is not None else self.SpacecraftHardware()

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
        self.solar_power_system: SolarPowerSystem | None = self.hardware.solar_power_system
        if self.hardware.solar_power_system is not None:
            assert isinstance(self.solar_power_system,
                              SolarPowerSystem), f'self.hardware.solar_power_system must be a SolarPowerSystem but was a {type(self.hardware.solar_power_system).__name__}.'
            self.solar_power_system.attach_to_sat(self)

        self.nuclear_power_system: NuclearPowerSystem | None = self.hardware.nuclear_power_system
        if self.nuclear_power_system is not None:
            assert isinstance(self.nuclear_power_system,
                              gp.NuclearPowerSystem), f'self.hardware.nuclear_power_system must be a NuclearPowerSystem but was a {type(self.hardware.nuclear_power_system).__name__}.'
            self.nuclear_power_system.attach_to_sat(self)

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
        sc.hardware = sc._update_hardware(hardware_obj)  # apply the new Hardware object to the spacecraft

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

    def _update_hardware(self, hardware: SpacecraftHardware):
        self.hardware: Spacecraft.SpacecraftHardware = hardware

        # Attach thrusters and tanks to the Spacecraft
        if self.hardware.chem_thrusters:
            for thruster in self.hardware.chem_thrusters:
                # if not thruster:
                #     raise RuntimeError(f"No chemical thrusters found, chemical thruster list is: "
                #                        f"{self.chem_thrusters}\n{self.hardware.chem_thrusters}")
                if thruster is not None:
                    thruster.attach_to_sat(self)
                    thruster.attach_to_tanks(thruster.tanks)

        if self.hardware.elec_thrusters:
            for thruster in self.hardware.elec_thrusters:
                # if not thruster:
                #     raise RuntimeError(f"No electric thrusters found, electric thruster list is:
                #     {self.elec_thrusters}")
                if thruster is not None:
                    thruster.attach_to_sat(self)
                    thruster.attach_to_tanks(thruster.tanks)

        if self.hardware.chem_tanks:
            for tank in self.hardware.chem_tanks:
                if tank is not None:
                    tank.attach_to_sat(self)

        if self.hardware.elec_tanks:
            for tank in self.hardware.elec_tanks:
                if tank is not None:
                    tank.attach_to_sat(self)

        self.chem_thrusters = self.hardware.chem_thrusters
        self.elec_thrusters = self.hardware.elec_thrusters

        self.chem_tanks = self.hardware.chem_tanks
        self.elec_tanks = self.hardware.elec_tanks

        self.solar_power_system = self.hardware.solar_power_system
        if self.solar_power_system is not None:
            self.solar_power_system.attach_to_sat(self)

        return self.hardware

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

        state: list = [None] * 6
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


class PressureModel(Enum):
    """Describes the pressure model for a ``ChemicalTank``."""
    PressureRegulated = 'PressureRegulated',
    BlowDown = 'BlowDown'


class FuelType(Enum):
    chemical = 'Chemical'
    electric = 'Electric'

    @property
    def tank(self) -> str:
        return f'{self.value}Tank'

    @property
    def tank_builder(self) -> Callable:
        return ChemicalTank if self == FuelType.chemical else ElectricTank

    @property
    def thruster(self) -> str:
        return f'{self.value}Thruster'

    @property
    def thruster_builder(self) -> Callable:
        return ChemicalThruster if self == FuelType.chemical else ElectricThruster


class FuelTank(GmatObject, Generic[T]):
    def __init__(self, tank_type: str, name: str, fuel_mass: float = 756, allow_negative_fuel_mass: bool = False,
                 fuel_centre_of_mass: np.ndarray = np.array([0, 0, 0]),
                 fuel_moment_of_inertia: np.ndarray = np.array([99, 0, 0, 99, 0, 99]),
                 direction: np.ndarray = np.array([0, 0, 1]), second_direction: np.ndarray = np.array([0, -1, 0]),
                 hw_origin_in_bcs: np.ndarray = np.array([0, 0, 0])) -> None:
        """
        Superclass of ``ChemicalTank`` and ``ElectricTank``.

        """
        """
        Attributes for Chemical Tank:
        
                   Field                                   Type   Value
           --------------------------------------------------------
        
           DirectionX                              Real   0
           DirectionY                              Real   0
           DirectionZ                              Real   1
           SecondDirectionX                        Real   0
           SecondDirectionY                        Real   -1
           SecondDirectionZ                        Real   0
           HWOriginInBCSX                          Real   0
           HWOriginInBCSY                          Real   0
           HWOriginInBCSZ                          Real   0
           AllowNegativeFuelMass                Boolean   false
           FuelMass                                Real   756
           FuelCenterOfMassX                       Real   0
           FuelCenterOfMassY                       Real   0
           FuelCenterOfMassZ                       Real   0
           FuelMomentOfInertiaXX                   Real   99
           FuelMomentOfInertiaXY                   Real   0
           FuelMomentOfInertiaXZ                   Real   0
           FuelMomentOfInertiaYY                   Real   99
           FuelMomentOfInertiaYZ                   Real   0
           FuelMomentOfInertiaZZ                   Real   99
           Pressure                                Real   1500
           Temperature                             Real   20
           RefTemperature                          Real   20
           Volume                                  Real   0.75
           FuelDensity                             Real   1260
           PressureModel                           List   PressureRegulated
        """
        assert tank_type in ['ChemicalTank', 'ElectricTank']  # Confirm tank_type is valid.
        super().__init__(tank_type, name)
        self._tank_type: str = tank_type  # 'ChemicalTank' or 'ElectricTank'
        self.name = name

        # TODO convert fuel mass and allow_negative_fuel_mass if ... is not None items to remove direct setting of parameters, as for fuel COM/MOI.
        self.fuel_mass: float = self.GetRealParameter('FuelMass')  # kg
        if fuel_mass is not None:
            self.fuel_mass = fuel_mass
            self.SetRealParameter('FuelMass', self.fuel_mass)

        self.allow_negative_fuel_mass: bool = self.GetBooleanParameter('AllowNegativeFuelMass')  # Boolean
        if allow_negative_fuel_mass is not None:
            self.allow_negative_fuel_mass = allow_negative_fuel_mass
            self.SetBooleanParameter('AllowNegativeFuelMass', self.allow_negative_fuel_mass)

        # Get fuel centre of mass from GMAT object.
        self._fuel_centre_of_mass: np.ndarray = self.fuel_centre_of_mass
        # TODO consider whether to remove equality checks - not used elsewhere but does save re-setting the parameters in GMAT.
        # Set new fuel centre of mass if provided.
        if (fuel_centre_of_mass is not None) and not ((fuel_centre_of_mass == self._fuel_centre_of_mass).all()):
            self.fuel_centre_of_mass = fuel_centre_of_mass

        # Get fuel moment of inertia from GMAT object.
        self._fuel_moment_of_inertia: np.ndarray = self.fuel_moment_of_inertia
        # Set new fuel moment of inertia if provided.
        if (fuel_moment_of_inertia is not None) and not (
                (fuel_moment_of_inertia == self._fuel_moment_of_inertia).all()):
            self.fuel_moment_of_inertia = fuel_moment_of_inertia

        # Get direction from GMAT object.
        self._direction: np.ndarray = self.direction
        # Set new direction if provided.
        if (direction is not None) and not ((direction == self._direction).all()):
            self.direction = direction

        # Get second direction from GMAT object.
        self._second_direction: np.ndarray = self.second_direction
        # Set new second direction if provided.
        if (second_direction is not None) and not ((second_direction == self._second_direction).all()):
            self.second_direction = second_direction

        # Get hardware origin in BCS from GMAT object.
        self._hw_origin_in_bcs: np.ndarray = self.hw_origin_in_bcs
        # Set new hardware origin in BCS if provided.
        if (hw_origin_in_bcs is not None) and not ((hw_origin_in_bcs == self._hw_origin_in_bcs).all()):
            self.hw_origin_in_bcs = hw_origin_in_bcs

        self.spacecraft: gp.Spacecraft | None = None

        try:
            self.Initialize()
        except RuntimeError as re:
            if "Fuel volume exceeds tank capacity" in str(re):
                volume: float = self.GetRealParameter('Volume')
                tank_fuel_mass: float = self.GetRealParameter('FuelMass')
                fuel_density: float = self.GetRealParameter('FuelDensity')
                volume_remaining: float = volume - tank_fuel_mass / fuel_density
                raise RuntimeError(
                    f'{str(re).rstrip()}: (volume - fuelMass / density) < 0.0 ({volume_remaining})') from re
            else:
                raise

    def __repr__(self):
        return f'{self._tank_type} with name {self.name}'

    @staticmethod
    def _from_dict(tank_type: type, tank_dict: dict[str, Union[str, int, float]]) -> T:
        if tank_type == gp.ChemicalTank:
            tank: gp.ChemicalTank = gp.ChemicalTank(str(tank_dict['Name']))
        elif tank_type == gp.ElectricTank:
            tank: gp.ElectricTank = gp.ElectricTank(str(tank_dict['Name']))
        else:
            raise SyntaxError(f'Invalid thr_type found in Tank.from_dict: {tank_type}'
                              f"\nMust be 'Chemical' or 'Electric'")

        fields: list[str] = list(tank_dict.keys())
        fields.remove('Name')
        for field in fields:
            try:
                tank.SetField(field, tank_dict[field])
            except Exception as ex:
                # TODO remove if (debugging only)
                if field != 'AllowNegativeFuelMass':
                    raise RuntimeError(f'Faulting field: {field}. GMAT error:\n\t{ex}')

        tank.Validate()

        return tank

    def attach_to_sat(self, sat: Spacecraft):
        self.spacecraft = sat
        assert self.spacecraft is not None
        self.spacecraft.add_tanks([gp.extract_gmat_obj(self)])

    def _DepleteFuel(self, delta_m: float) -> None:
        """Depletes fuel from the tank and updates the tank's ``fuel_mass``."""
        # ElectricTank::DepleteFuel() in ElectricTank.cpp in GMAT's source code has its body commented out, so return None.
        if isinstance(self, ElectricTank):
            return None

        self.fuel_mass -= delta_m
        if self.fuel_mass < 0:
            raise HardwareException(f'Fuel in tank {self.name} completely exhausted.')

        return None

    @property
    def direction(self) -> np.ndarray:
        """
        Gets the ``direction`` vector set on this ``Tank``'s GMAT object.

        Returns a ``numpy.ndarray`` by combining the elements of the internal vector (``DirectionX``, ``DirectionY``, ``DirectionZ``).
        """
        axes: list[str] = ['X', 'Y', 'Z']
        direction: dict = {axis: float(self.gmat_obj.GetField(f'Direction{axis}')) for axis in axes}
        return np.array(list(direction.values()))

    @direction.setter
    def direction(self, direction: np.ndarray) -> None:
        self._direction = direction
        self.SetRealParameter('DirectionX', direction[0])
        self.SetRealParameter('DirectionY', direction[1])
        self.SetRealParameter('DirectionZ', direction[2])

    @property
    def fuel_centre_of_mass(self) -> np.ndarray:
        fuel_com_x: float = self.GetRealParameter('FuelCenterOfMassX')
        fuel_com_y: float = self.GetRealParameter('FuelCenterOfMassY')
        fuel_com_z: float = self.GetRealParameter('FuelCenterOfMassZ')
        self._fuel_centre_of_mass: np.ndarray = np.array([fuel_com_x, fuel_com_y, fuel_com_z])
        return self._fuel_centre_of_mass

    @fuel_centre_of_mass.setter
    def fuel_centre_of_mass(self, fuel_centre_of_mass: np.ndarray) -> None:
        self._fuel_centre_of_mass = fuel_centre_of_mass
        self.SetRealParameter('FuelCenterOfMassX', fuel_centre_of_mass[0])
        self.SetRealParameter('FuelCenterOfMassY', fuel_centre_of_mass[1])
        self.SetRealParameter('FuelCenterOfMassZ', fuel_centre_of_mass[2])

    @property
    def fuel_moment_of_inertia(self) -> np.ndarray:
        fuel_moi_xx: float = self.GetRealParameter('FuelMomentOfInertiaXX')
        fuel_moi_xy: float = self.GetRealParameter('FuelMomentOfInertiaXY')
        fuel_moi_xz: float = self.GetRealParameter('FuelMomentOfInertiaXZ')
        fuel_moi_yy: float = self.GetRealParameter('FuelMomentOfInertiaYY')
        fuel_moi_yz: float = self.GetRealParameter('FuelMomentOfInertiaYZ')
        fuel_moi_zz: float = self.GetRealParameter('FuelMomentOfInertiaZZ')
        self._fuel_moment_of_inertia: np.ndarray = np.array(
            [fuel_moi_xx, fuel_moi_xy, fuel_moi_xz, fuel_moi_yy, fuel_moi_yz, fuel_moi_zz])
        return self._fuel_moment_of_inertia

    @fuel_moment_of_inertia.setter
    def fuel_moment_of_inertia(self, fuel_moment_of_inertia: np.ndarray) -> None:
        self._fuel_moment_of_inertia = fuel_moment_of_inertia
        self.SetRealParameter('FuelMomentOfInertiaXX', fuel_moment_of_inertia[0])
        self.SetRealParameter('FuelMomentOfInertiaXY', fuel_moment_of_inertia[1])
        self.SetRealParameter('FuelMomentOfInertiaXZ', fuel_moment_of_inertia[2])
        self.SetRealParameter('FuelMomentOfInertiaYY', fuel_moment_of_inertia[3])
        self.SetRealParameter('FuelMomentOfInertiaYZ', fuel_moment_of_inertia[4])
        self.SetRealParameter('FuelMomentOfInertiaZZ', fuel_moment_of_inertia[5])

    @property
    def hw_origin_in_bcs(self) -> np.ndarray:
        hw_origin_in_bcs_x: float = self.GetRealParameter('HWOriginInBCSX')
        hw_origin_in_bcs_y: float = self.GetRealParameter('HWOriginInBCSY')
        hw_origin_in_bcs_z: float = self.GetRealParameter('HWOriginInBCSZ')
        self._hw_origin_in_bcs: np.ndarray = np.array([hw_origin_in_bcs_x, hw_origin_in_bcs_y, hw_origin_in_bcs_z])
        return self._hw_origin_in_bcs

    @hw_origin_in_bcs.setter
    def hw_origin_in_bcs(self, hw_origin_in_bcs: np.ndarray) -> None:
        self._hw_origin_in_bcs = hw_origin_in_bcs
        self.SetRealParameter('HWOriginInBCSX', hw_origin_in_bcs[0])
        self.SetRealParameter('HWOriginInBCSY', hw_origin_in_bcs[1])
        self.SetRealParameter('HWOriginInBCSZ', hw_origin_in_bcs[2])

    @property
    def second_direction(self) -> np.ndarray:
        """
        Gets the ``second_direction`` vector set on this ``Tank``'s GMAT object.

        Returns a ``numpy.ndarray`` by combining the elements of the internal vector (``SecondDirectionX``, ``SecondDirectionY``, ``SecondDirectionZ``).
        """
        axes: list[str] = ['X', 'Y', 'Z']
        second_direction: dict = {axis: float(self.gmat_obj.GetField(f'SecondDirection{axis}')) for axis in axes}
        return np.array(list(second_direction.values()))

    @second_direction.setter
    def second_direction(self, second_direction: np.ndarray) -> None:
        self._direction = second_direction
        self.SetRealParameter('SecondDirectionX', second_direction[0])
        self.SetRealParameter('SecondDirectionY', second_direction[1])
        self.SetRealParameter('SecondDirectionZ', second_direction[2])

    # TODO implement FuelTank.UpdateTank() method
    def UpdateTank(self):
        """
        Updates pressure and volume data using the ideal gas law.

        GMAT fuel tanks can operate in a pressure-regulated mode (constant pressure, constant temperature) or in a blow-down mode.
        When the tank runs in blow-down mode, the pressure is calculated using the ideal gas law:

        ``PV=nRT``

        The right side of this equation is held constant.  Given an initial pressure ``P_i`` and an initial volume
        ``V_i``, the new pressure is given by

        ``P_f = ``(P_i V_i) / V_f``

        The pressurant volume ``V_G`` is calculated from the tank volume ``V_T``, the fuel mass ``M_F``, and the fuel
        density ``rho`` using

        ``V_G = V_T - M_F / rho``

        Mass is depleted from the tank by integrating the mass flow over time, as is described in the ``Thruster`` documentation.
        """
        # ElectricTank::UpdateTank() in ElectricTank.cpp in GMAT's source code has its body commented out, so return None.
        if isinstance(self, ElectricTank):
            return None

        raise NotImplementedError('FuelTank.UpdateTank is not yet implemented.')


class ChemicalTank(FuelTank):
    def __init__(self, name: str, fuel_mass: int | float = 756, allow_negative_fuel_mass: bool = False,
                 pressure: int | float = 1500, temperature: int | float = 20, ref_temp: int | float = 20,
                 volume: int | float = 0.75, fuel_density: int | float = 1260,
                 pressure_model: PressureModel = PressureModel.PressureRegulated,
                 fuel_centre_of_mass: np.ndarray = np.array([0, 0, 0]),
                 fuel_moment_of_inertia: np.ndarray = np.array([99, 0, 0, 99, 0, 99]),
                 direction: np.ndarray = np.array([0, 0, 1]), second_direction: np.ndarray = np.array([0, -1, 0]),
                 hw_origin_in_bcs: np.ndarray = np.array([0, 0, 0])):
        """A ``FuelTank`` that stores fuel used by one or more ``ChemicalThruster``s."""
        super().__init__('ChemicalTank', name, fuel_mass, allow_negative_fuel_mass, fuel_centre_of_mass,
                         fuel_moment_of_inertia, direction, second_direction, hw_origin_in_bcs)

        # TODO convert if ... is not None items to remove direct setting of parameters - create getters and setters instead, like in FuelTank.
        self.pressure = self.GetRealParameter('Pressure')  # kPa
        if pressure is not None:
            self.pressure = pressure
            self.SetRealParameter('Pressure', self.pressure)

        self.temperature = self.GetRealParameter('Temperature')  # Celsius
        if temperature is not None:
            self.temperature = temperature
            self.SetRealParameter('Temperature', self.temperature)

        self.ref_temp = self.GetRealParameter('RefTemperature')  # Celsius
        if ref_temp is not None:
            self.ref_temp = ref_temp
            self.SetRealParameter('RefTemperature', self.ref_temp)

        # Volume
        self.volume = self.GetRealParameter('Volume')  # m^3
        if volume is not None:
            self.volume = volume
            self.SetRealParameter('Volume', self.volume)

        # Fuel density
        self.fuel_density = self.GetRealParameter('FuelDensity')  # kg/m^3
        if fuel_density is not None:
            self.fuel_density = fuel_density
            self.SetRealParameter('FuelDensity', self.fuel_density)

        # Pressure Model
        self.pressure_model: PressureModel = PressureModel[self.GetStringParameter('PressureModel')]  # string
        if pressure_model is not None:
            self.pressure_model: PressureModel = pressure_model
            self.SetStringParameter('PressureModel', self.pressure_model.name)

        self.Initialize()

    @classmethod
    def from_dict(cls, cp_tank_dict: dict) -> gp.ChemicalTank | None:
        if cp_tank_dict != {}:
            cp_tank: ChemicalTank = FuelTank[ChemicalTank]._from_dict(gp.ChemicalTank, cp_tank_dict)
            cp_tank.Validate()
            return cp_tank
        else:
            return None

    # def attach_to_sat(self):
    #     return super().attach_to_sat()

    # @classmethod
    # def from_dict(cls, sc: Spacecraft, tank_dict: dict, **kwargs):
    #     tank = super().from_dict(sc, 'chemical', tank_dict)
    #     return tank


class ElectricTank(FuelTank):
    #     # TODO add FuelMass and other fields
    #     # self.fuel_mass = fuel_mass
    #     # self.GmatObj.SetField('FuelMass', self.fuel_mass)

    def __init__(self, name: str, fuel_mass: int | float = 756, allow_negative_fuel_mass: bool = False,
                 fuel_centre_of_mass: np.ndarray = np.array([0, 0, 0]),
                 fuel_moment_of_inertia: np.ndarray = np.array([99, 0, 0, 99, 0, 99]),
                 direction: np.ndarray = np.array([0, 0, 1]), second_direction: np.ndarray = np.array([0, -1, 0]),
                 hw_origin_in_bcs: np.ndarray = np.array([0, 0, 0])
                 ) -> None:
        """
        A ``FuelTank`` that stores fuel used by one or more ``ElectricThruster``s.
        """
        super().__init__('ElectricTank', name, fuel_mass, allow_negative_fuel_mass, fuel_centre_of_mass,
                         fuel_moment_of_inertia, direction, second_direction, hw_origin_in_bcs)

        # TODO take and parse arguments like in ChemicalTank

        self.Initialize()

    @classmethod
    def from_dict(cls, ep_tank_dict: dict) -> gp.ElectricTank | None:
        if ep_tank_dict != {}:
            ep_tank: ElectricTank = FuelTank[ElectricTank]._from_dict(gp.ElectricTank, ep_tank_dict)
            ep_tank.Validate()
            return ep_tank
        else:
            return None


class Thruster(GmatObject):
    def __init__(self, fuel_type: FuelType, name: str,
                 tanks: gp.FuelTank | gmat.FuelTank | list[gp.FuelTank] | list[gmat.FuelTank],
                 mix_ratio: dict[gp.FuelTank, int | float] = None):
        assert isinstance(tanks, (gp.FuelTank, gmat.FuelTank,
                                  list)), 'tanks must be a gp.FuelTank, gmat.FuelTank, list[gp.FuelTank] or list[gmat.FuelTank].'

        self.fuel_type = fuel_type
        self.thruster_type: str = f'{self.fuel_type.value}Thruster'  # 'ChemicalThruster' or 'ElectricThruster'
        super().__init__(self.thruster_type, name)

        self.spacecraft: gp.Spacecraft | None = None

        self.tanks: list[ChemicalTank | ElectricTank] | None = tanks
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
        if fuel_type == FuelType.chemical:
            thr = ChemicalThruster(name, tanks)
        elif fuel_type == FuelType.electric:
            thr = ElectricThruster(name, tanks)
        else:
            raise SyntaxError(f'Invalid fuel_type found in Thruster.from_dict: {fuel_type}.'
                              f"\nMust be FuelType.chemical or FuelType.electric.")

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

    def attach_to_sat(self, sat: Spacecraft):
        self.spacecraft: Spacecraft = sat
        assert self.spacecraft is not None
        self.spacecraft.add_thrusters([self.gmat_obj])

    def attach_to_tanks(self, tanks: list[FuelTank]):
        gp.extract_gmat_obj(self).SetField('Tank', [tank.GetName() for tank in tanks])

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
    def __init__(self, name: str, tanks: str | gp.ChemicalTank | gmat.ChemicalTank |
                                         list[gp.ChemicalTank] | list[gmat.ChemicalTank],
                 mix_ratio: dict[gp.ChemicalTank, int | float] = None):
        if isinstance(tanks, str):
            tanks: ChemicalTank = ChemicalTank(tanks)
        super().__init__(FuelType.chemical, name, tanks, mix_ratio)

        self.Validate()
        self.Initialize()

    @classmethod
    def from_dict(cls, cp_thr_dict: dict) -> gp.ChemicalThruster | None:
        if cp_thr_dict != {}:
            cp_thr: gp.Thruster = Thruster.from_dict(FuelType.chemical, cp_thr_dict)
            assert isinstance(cp_thr, gp.ChemicalThruster)
            cp_thr.Validate()
            return cp_thr
        else:
            return None


class ElectricThruster(Thruster):
    def __init__(self, name: str, tanks: str | gp.ElectricTank | gmat.ElectricTank |
                                         list[gp.ElectricTank] | list[gmat.ElectricTank],
                 mix_ratio: dict[gp.ElectricTank, int | float] = None):
        super().__init__(FuelType.electric, name, tanks, mix_ratio)
        self.Initialize()

    @classmethod
    def from_dict(cls, ep_thr_dict: dict) -> gp.ElectricThruster | None:
        if ep_thr_dict != {}:
            ep_thr: gp.Thruster = Thruster.from_dict(FuelType.electric, ep_thr_dict)
            assert isinstance(ep_thr, gp.ElectricThruster)
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
