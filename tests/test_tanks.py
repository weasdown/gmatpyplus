# Tests setting complex properties on chemical and electric tanks.
import unittest

import numpy as np

import gmatpyplus as gp


class TestTanks(unittest.TestCase):
    def setUp(self):
        self.fuel_com: np.ndarray = np.array([0, 0.1, 0.2])
        self.fuel_moi: np.ndarray = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
        self.direction: np.ndarray = np.array([1, 0, 0])
        self.second_direction: np.ndarray = np.array([0, 1, 0])
        self.hw_origin_in_bcs: np.ndarray = np.array([0.2, 0.4, 0.6])

    def _test_tank(self, tank: gp.FuelTank):
        with self.subTest('direction'):
            # Test the gp.FuelTank's direction matches the direction argument.
            self.assertTrue((self.direction == tank.direction).all(),
                            f'gp.FuelTank direction attribute ({tank.direction}) is not equal to direction argument '
                            f'({self.direction}).')

            # Test the gp.FuelTank's direction matches GMAT's internal direction values.
            direction_x_field = float(tank.GetField('DirectionX'))
            direction_y_field = float(tank.GetField('DirectionY'))
            direction_z_field = float(tank.GetField('DirectionZ'))
            direction_field = np.array([direction_x_field, direction_y_field, direction_z_field])
            self.assertTrue((direction_field == tank.direction).all(),
                            f'direction_field from GMAT object ({direction_field}) is not equal to direction '
                            f'argument ({tank.direction}).')

        with self.subTest('second direction'):
            # Test the gp.FuelTank's second direction matches the second direction argument.
            self.assertTrue((self.second_direction == tank.second_direction).all(),
                            f'gp.FuelTank second_direction attribute ({tank.second_direction}) is not equal to '
                            f'second_direction argument ({self.second_direction}).')

            # Test the gp.FuelTank's second_direction matches GMAT's internal second_direction values.
            second_direction_x_field = float(tank.GetField('SecondDirectionX'))
            second_direction_y_field = float(tank.GetField('SecondDirectionY'))
            second_direction_z_field = float(tank.GetField('SecondDirectionZ'))
            second_direction_field = np.array(
                [second_direction_x_field, second_direction_y_field, second_direction_z_field])
            self.assertTrue((second_direction_field == tank.second_direction).all(),
                            f'second_direction_field from GMAT object ({second_direction_field}) is not equal to '
                            f'gp.FuelTank second_direction attribute ({tank.second_direction}).')

        with self.subTest('fuel centre of mass'):
            # Test the gp.FuelTank's fuel centre of mass matches the fuel centre of mass argument.
            self.assertTrue((self.fuel_com == tank.fuel_centre_of_mass).all(),
                            f'gp.FuelTank fuel centre of mass attribute ({tank.direction}) is not equal to fuel '
                            f'centre of mass argument ({self.fuel_com}).')

            # Test the gp.FuelTank's direction matches GMAT's internal direction values.
            fuel_com_x_field = float(tank.GetField('FuelCenterOfMassX'))
            fuel_com_y_field = float(tank.GetField('FuelCenterOfMassY'))
            fuel_com_z_field = float(tank.GetField('FuelCenterOfMassZ'))
            fuel_com_field = np.array([fuel_com_x_field, fuel_com_y_field, fuel_com_z_field])
            self.assertTrue((fuel_com_field == tank.fuel_centre_of_mass).all(),
                            f'fuel_com_field from GMAT object ({fuel_com_field}) is not equal to gp.FuelTank '
                            f'fuel_centre_of_mass attribute ({tank.fuel_centre_of_mass}).')

    def test_chemical_tank(self):
        ct1: gp.ChemicalTank = gp.ChemicalTank('CT1', 500, True, 1000, 10, 10, 0.5, 1000, gp.PressureModel.BlowDown,
                                               self.fuel_com, self.fuel_moi, self.direction, self.second_direction,
                                               self.hw_origin_in_bcs)

        self._test_tank(ct1)

    def test_electric_tank(self):
        et1: gp.ElectricTank = gp.ElectricTank('ET1', 500, True, self.fuel_com, self.fuel_moi, self.direction,
                                               self.second_direction, self.hw_origin_in_bcs)

        self._test_tank(et1)


if __name__ == '__main__':
    unittest.main()
