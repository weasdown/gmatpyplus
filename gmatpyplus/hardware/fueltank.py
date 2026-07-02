from __future__ import annotations

from enum import Enum
from typing import Generic, TypeVar, Union

import numpy as np

import gmatpyplus as gp
from gmatpyplus.foundation import GmatObject

T = TypeVar('T')


class FuelTank(GmatObject, Generic[T]):
    def __init__(self, tank_type: str, name: str, fuel_mass: float = 756, allow_negative_fuel_mass: bool = False,
                 fuel_centre_of_mass: np.ndarray = np.array([0, 0, 0]),
                 fuel_moment_of_inertia: np.ndarray = np.array([99, 0, 0, 99, 0, 99]),
                 direction: np.ndarray = np.array([0, 0, 1]), second_direction: np.ndarray = np.array([0, -1, 0]),
                 hw_origin_in_bcs: np.ndarray = np.array([0, 0, 0])) -> None:
        """
        Superclass of ``ChemicalTank`` and ``ElectricTank``.

        """
        assert (tank_type == 'ChemicalTank') or (tank_type == 'ElectricTank')  # Confirm tank_type is valid.
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
            tank = ChemicalTank(str(tank_dict['Name']))
        elif tank_type == gp.ElectricTank:
            tank = ElectricTank(str(tank_dict['Name']))
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

    def attach_to_sat(self, sat: gp.Spacecraft):
        self.spacecraft = sat
        self.spacecraft.add_tanks([gp.extract_gmat_obj(self)])

    def _DepleteFuel(self, delta_m: float) -> None:
        """Depletes fuel from the tank and updates the tank's ``fuel_mass``."""
        # ElectricTank::DepleteFuel() in ElectricTank.cpp in GMAT's source code has its body commented out, so return None.
        if isinstance(self, ElectricTank):
            return None

        self.fuel_mass -= delta_m
        if self.fuel_mass < 0:
            raise gp.HardwareException(f'Fuel in tank {self.name} completely exhausted.')

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


class PressureModel(Enum):
    """Describes the pressure model for a ``ChemicalTank``."""
    PressureRegulated = 'PressureRegulated',
    BlowDown = 'BlowDown'


class ChemicalTank(FuelTank):
    def __init__(self, name: str, fuel_mass: int | float = 756, allow_negative_fuel_mass: bool = False,
                 pressure: int | float = 1500, temperature: int | float = 20, ref_temp: int | float = 20,
                 volume: int | float = 0.75, fuel_density: int | float = 1260,
                 pressure_model: PressureModel = PressureModel.PressureRegulated,
                 fuel_centre_of_mass: np.ndarray = np.array([0, 0, 0]),
                 fuel_moment_of_inertia: np.ndarray = np.array([99, 0, 0, 99, 0, 99]),
                 direction: np.ndarray = np.array([0, 0, 1]), second_direction: np.ndarray = np.array([0, -1, 0]),
                 hw_origin_in_bcs: np.ndarray = np.array([0, 0, 0])):
        """
        A ``FuelTank`` that stores fuel used by one or more ``ChemicalThruster``s.

        Attributes for ``ChemicalTank`` and their default value:

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
        self.pressure_model: gp.PressureModel = gp.PressureModel[self.GetStringParameter('PressureModel')]  # string
        if pressure_model is not None:
            self.pressure_model: gp.PressureModel = pressure_model
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
