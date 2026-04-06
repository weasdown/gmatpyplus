# For testing hardware adding to Spacecraft, for issue #58.
# See https://github.com/weasdown/gmatpyplus/issues/58#issue-3859050067

import gmatpyplus as gp

example_orbit: dict = {
    'CoordSys': 'EarthMJ2000Eq',
    'Epoch': '21545',
    'DisplayStateType': 'Keplerian',
    'SMA': 7200
}

# Includes 1 ChemicalTank (Tank1) and 3 ChemicalThrusters (Thr1, Thr2, Thr3).
sat_params = {
    'Name': 'stuff',
    'Hardware': {
        'ChemicalTanks': [
            {
                'Name': 'Tank1',
                'AllowNegativeFuelMass': True,
                'FuelMass': 1000,
                'Pressure': 1000,
                'Temperature': 30,
                'RefTemperature': 30,
                'Volume': 1,
                'FuelDensity': 1000,
                'PressureModel': 'PressureRegulated',
            }
        ],
        'ChemicalThrusters': [
            {
                'Name': "Thr1",
                'CoordinateSystem': 'Local',
                'Origin': 'Earth',
                'Axes': 'VNB',
                'DutyCycle': 1,
                'ThrustScaleFactor': 1,
                'DecrementMass': True,
                'Tanks': 'Tank1',
            },
            {
                'Name': "Thr2",
                'CoordinateSystem': 'Local',
                'Origin': 'Earth',
                'Axes': 'VNB',
                'DutyCycle': 1,
                'ThrustScaleFactor': 1,
                'DecrementMass': True,
                'Tanks': 'Tank1',
            },
            {
                'Name': "Thr3",
                'CoordinateSystem': 'Local',
                'Origin': 'Earth',
                'Axes': 'VNB',
                'DutyCycle': 1,
                'ThrustScaleFactor': 1,
                'DecrementMass': True,
                'Tanks': 'Tank1',
            }
        ]
    }
}

# FIXME: RuntimeError: GMAT Initialize failed - GMAT error: "GmatBase Exception Thrown: ObjectInitializer::BuildAssociations: Cannot find hardware element "hr""
sat = gp.Spacecraft.from_dict(sat_params)

sat.Help()
