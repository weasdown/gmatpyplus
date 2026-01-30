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
            self.assertTrue((direction_field == tank.direction).all(), f'direction_field from GMAT object '
                                                                       f'({direction_field}) is not equal to direction argument '
                                                                       f'({tank.direction}).')

    def test_chemical_tank(self):
        ct1: gp.ChemicalTank = gp.ChemicalTank('CT1', 500, True, 1000, 10, 10, 0.5, 1000, gp.PressureModel.BlowDown,
                                               self.fuel_com, self.fuel_moi, self.direction, self.second_direction,
                                               self.hw_origin_in_bcs)

        self._test_tank(ct1)

    def test_electric_tank(self):
        et1: gp.ElectricTank = gp.ElectricTank('ET1', 500, True, self.fuel_com, self.fuel_moi, self.direction,
                                               self.second_direction, self.hw_origin_in_bcs)

        self._test_tank(et1)
