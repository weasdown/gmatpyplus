# Tutorial 02: Simple Orbit Transfer. Perform a Hohmann Transfer from Low Earth Orbit (LEO) to Geostationary orbit (GEO)
# Written by William Easdown Babb

from __future__ import annotations
from load_gmat import gmat
import gmatpyplus as gp
import os

log_path = os.path.normpath(f'{os.getcwd()}/examples/logs/GMAT-Tut02-Log.txt')
gmat.UseLogFile(log_path)
gmat.EchoLogFile(False)  # set to True to view log output in console (e.g. live iteration results)

sat = gp.Spacecraft('DefaultSC')

prop = gp.PropSetup('NonDefaultProp', gator=gp.PropSetup.Propagator('RungeKutta89'),
                    accuracy=9.999999999999999e-12)

toi = gp.ImpulsiveBurn('TOI')
goi = gp.ImpulsiveBurn('GOI')

dc1 = gp.DifferentialCorrector('DC1')

print(f'Sat state before running: {sat.GetState()}')
print(f"Epoch before running: {sat.GetField('Epoch')}")

# Targeting sequence to adjust parameters of the two burns (TOI and GOI) to achieve desired final orbit
tg1 = gp.Target('Hohmann Transfer', dc1, exit_mode='SaveAndContinue', command_sequence=[
    # Vary the velocity of the TOI burn to achieve an apoapsis with RMAG = 42165 km
    gp.Vary('Vary TOI', dc1, f'{toi.name}.Element1'),
    gp.Maneuver('Perform TOI', toi, sat),
    gp.Propagate('Prop To Apoapsis', sat, prop, f'{sat.name}.Earth.Apoapsis'),
    gp.Achieve('Achieve RMAG = 42165', dc1, f'{sat.name}.Earth.RMAG', 42164.169, 0.1),

    # Vary the velocity of the GOI burn to achieve an eccentricity of 0.005
    gp.Vary('Vary GOI', dc1, f'{goi.name}.Element1', max_step=0.2),
    gp.Maneuver('Perform GOI', goi, sat),
    gp.Achieve('Achieve ECC = 0.005', dc1, f'{sat.name}.Earth.ECC', 0.005, 0.0001)
])

# Mission Command Sequence
mcs = [
    gp.Propagate('Prop To Periapsis', sat, prop, f'{sat.name}.Earth.Periapsis'),
    tg1,  # Target command and its command sequence
    gp.Propagate('Prop One Day', sat, prop, (f'{sat.name}.ElapsedDays', 1))
]

gp.RunMission(mcs)  # Run the mission

print(f'Sat state after running: {sat.GetState()}')
print(f'Epoch after running: {sat.GetField("Epoch")}')

script_path = os.path.normpath(f'{os.getcwd()}/examples/scripts/Tut02-SimpleOrbitTransfer.script')
gmat.SaveScript(script_path)
