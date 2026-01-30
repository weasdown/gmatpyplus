# Tests setting complex properties on chemical and electric tanks.
import unittest

import numpy as np

import gmatpyplus as gp


class TestTanks(unittest.TestCase):
    def test_chemical_tank(self):
        fuel_com: np.ndarray = np.array([0, 0.1, 0.2])
        fuel_moi: np.ndarray = np.array([0.2, 0.1, 0])
        direction = np.array([1, 0, 0])
        second_direction = np.array([0, 1, 0])

        # ct1: gp.ChemicalTank = gp.ChemicalTank('CT1')
        ct1: gp.ChemicalTank = gp.ChemicalTank('CT1', 500, True, 1000, 10, 10, 0.5, 1000, gp.PressureModel.BlowDown,
                                               fuel_com, fuel_moi,
                                               direction,
                                               second_direction)

        ct1.Help()

        # Test the gp.ChemicalTank's direction matches the direction argument.
        self.assertTrue((direction == ct1.direction).all(), f'gp.ChemicalTank direction attribute ({ct1.direction})'
                                                            f' is not equal to direction argument ({direction}).')

        # Test the gp.ChemicalTank's direction matches GMAT's internal direction values.
        direction_x_field = float(ct1.GetField('DirectionX'))
        direction_y_field = float(ct1.GetField('DirectionY'))
        direction_z_field = float(ct1.GetField('DirectionZ'))
        direction_field = np.array([direction_x_field, direction_y_field, direction_z_field])
        self.assertTrue((direction_field == ct1.direction).all(), f'direction_field from GMAT object '
                                                                  f'({direction_field}) is not equal to direction argument '
                                                                  f'({ct1.direction}).')
