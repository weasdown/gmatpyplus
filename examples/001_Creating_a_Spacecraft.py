import gmatpyplus as gp

# sat_params = {
#     'Name': 'DefaultSC',
#     'Orbit': {
#         'CoordSys': 'EarthMJ2000Eq',
#         'Epoch': '21545',
#         'DisplayStateType': 'Keplerian',
#         'SMA': 7200
#     },
#     'DryMass': 100,  # kg
#     'Hardware': {'ChemicalTanks': [{'Name': 'ChemicalTank1'}],
#                  'ElectricTanks': [{'Name': 'ElectricTank1'}],
#                  'ChemicalThrusters': [{'Name': 'ChemicalThruster1', 'Tanks': 'ChemicalTank1'}],
#                  'ElectricThrusters': [{'Name': 'ElectricThruster1', 'Tanks': 'ElectricTank1'}],
#                  'SolarPowerSystem': {'Name': 'SolarPowerSystem1'},
#                  }
# }

sat_params = {
    'Name': 'DefaultSC',
    'Orbit': {
        'CoordSys': 'EarthMJ2000Eq',
        'Epoch': '21545',
        'DisplayStateType': 'Keplerian',
        'SMA': 7200
    },
    'DryMass': 100,  # kg
    'Hardware': {'ChemicalTanks': [{'Name': 'ChemicalTank1'}],
                 'ElectricTanks': [{'Name': 'ElectricTank1'}],
                 'ChemicalThrusters': [
                     {
                         'Name': 'ChemicalThruster1',
                         'Tanks': ['ChemicalTank1', 'ChemicalTank2'],
                         'MixRatio': {'ChemicalTank1': 0.5, 'ChemicalTank2': 0.3, 'ChemicalTank3': 0.2}
                     }
                 ],
                 'ElectricThrusters': [
                     {
                         'Name': 'ElectricThruster1',
                         'Tanks': ['ElectricTank1', 'ElectricTank2'],
                         'MixRatio': {'ElectricTank1': 0.5, 'ElectricTank2': 0.5}
                     }
                 ],
                 'SolarPowerSystem': {'Name': 'SolarPowerSystem1'},
                 }
}

sat = gp.Spacecraft.from_dict(sat_params)

sat.Help()
