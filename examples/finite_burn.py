# Tutorial 02: Simple Orbit Transfer. Perform a Hohmann Transfer from Low Earth Orbit (LEO) to Geostationary orbit (GEO)
# Written by William Easdown Babb

from __future__ import annotations

import os

import gmatpyplus as gp

log_path = os.path.normpath(f'{gp.logs_dir}/GMAT-Log-finite_burn.txt')
gp.gmat.UseLogFile(log_path)
gp.gmat.EchoLogFile(False)  # set to True to view log output in console (e.g. live iteration results)

sat_params = {
    'Name': 'DefaultSC',
    'DisplayStateType': 'Keplerian',
    'DateFormat': 'UTCGregorian',
    'Hardware': {'Tanks': {'chemical': [{'Name': 'ChemicalTank1'}],
                           'electric': [{'Name': 'ElectricTank1'}]},
                 'Thrusters': {'chemical': [{'Name': 'ChemicalThruster1', 'Tanks': 'ChemicalTank1'}],
                               'electric': [{'Name': 'ElectricThruster1', 'Tanks': 'ElectricTank1'}]},
                 'SolarPowerSystem': {'Name': 'SolarPowerSystem1'},
                 }
}
sat = gp.Spacecraft.from_dict(sat_params)

prop = gp.PropSetup('DefaultProp', gator=gp.PropSetup.Propagator('RungeKutta89'),
                    accuracy=9.999999999999999e-12)

fb1 = gp.FiniteBurn('FiniteBurn1', sat.elec_thrusters[0])

print(f'Sat state before running: {sat.GetState()}')
print(f"Epoch before running: {sat.GetEpoch()}")

# Mission Command Sequence
mcs = [
    gp.BeginFiniteBurn(fb1, sat, 'Turn Thruster On'),
    gp.Propagate('Prop 10 days', sat, prop, (f'{sat.name}.ElapsedDays', 10)),
    gp.EndFiniteBurn(fb1, 'Turn Thruster Off'),
]

gp.RunMission(mcs)  # Run the mission

print(f'Sat state after running: {sat.GetState()}')
print(f'Epoch after running: {sat.GetField("Epoch")}')

script_path = os.path.normpath(f'{gp.scripts_dir}/finite_burn.script')
gp.gmat.SaveScript(script_path)
