import unittest

import gmatpyplus as gp
import gmatpyplus.hardware as h
from gmatpyplus.load_gmat import gmat
from gmatpyplus.spacecraft import Spacecraft


class TestSpacecraft(unittest.TestCase):
    # @classmethod
    # def setUpClass(cls):
    #     print("\nsetUpClass method: Runs before all tests...")

    def setUp(self):
        self.sat_1 = Spacecraft('TS1',
                                hardware=Spacecraft.SpacecraftHardware(
                                    chem_tanks=gp.ChemicalTank('ChemTank1'),
                                    chem_thrusters=gp.ChemicalThruster('ChemThruster1', 'ChemTank1'),
                                    elec_tanks=gp.ElectricTank('ElecTank1'),
                                    elec_thrusters=gp.ElectricThruster('ElecThruster1', 'ElecTank1'),
                                    solar_power_system=h.SolarPowerSystem('SolarPowerSystem1'),
                                    nuclear_power_system=h.NuclearPowerSystem('NuclearPowerSystem1'),
                                    imagers=h.Imager('Imager1')
                                )
                                )

    # def setUp(self):
    #     print("\nRunning setUp method...")
    #     self.book_1 = Book('Deep Work', 'Cal Newport', 304, 15, 0.05)
    #     self.book_2 = Book('Grit', 'Angela Duckworth', 447, 16, 0.15)

    def tearDown(self):
        gmat.Clear()

    def test_thrusters(self):
        hardware_list = self.sat_1.GetField('AddHardware')

        # Check thrusters, tanks, power system fields
        self.assertEqual(self.sat_1.GetField('Thrusters'), '{ChemThruster1, ElecThruster1}')

        # Check AddHardware field
        self.assertIn('ChemThruster1', hardware_list)
        self.assertIn('ElecThruster1', hardware_list)

    # def test_discount(self):
    #     print("Running test_discount...")
    #     # self.assertEqual(self.book_1.apply_discount(), f"${15 - 15 * 0.05}")
    #     # self.assertEqual(self.book_2.apply_discount(), f"${16 - 16 * 0.15}")

    # def test_title(self):
    #     print("Running test_title...")
    #     # self.assertEqual(self.book_1.title, 'Deep Work')
    #     # self.assertIsInstance(self.book_2.title, str)
    #     # self.assertEqual(self.book_2.title, 'Grit')

    # def test_author(self):
    #     print("Running test_author...")
    #     # self.assertEqual(self.book_1.author, 'Cal Newport')
    #     # self.assertEqual(self.book_2.author, 'Angela Duckworth')

    # @classmethod
    # def tearDownClass(cls):
    #     print("\ntearDownClass method: Runs after all tests...")

    def test_tanks(self):
        hardware_list = self.sat_1.GetField('AddHardware')

        # Check Tanks field
        self.assertEqual(self.sat_1.GetField('Tanks'), '{ChemTank1, ElecTank1}')

        # Check AddHardware field
        self.assertIn('ChemTank1', hardware_list)
        self.assertIn('ElecTank1', hardware_list)

    def test_power_system(self):
        # Check Tanks field
        self.assertEqual(self.sat_1.GetField('PowerSystem'), 'SolarPowerSystem1')

        # Check AddHardware field
        self.assertIn('SolarPowerSystem1', self.sat_1.GetField('AddHardware'))

    def test_imagers(self):
        # Check AddHardware field
        self.assertIn('Imager1', self.sat_1.GetField('AddHardware'))


if __name__ == '__main__':
    unittest.main()
