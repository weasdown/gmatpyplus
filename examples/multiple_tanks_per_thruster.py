import gmatpyplus as gp

sc = gp.Spacecraft('SC1')

tank1 = gp.ChemicalTank('Tank1', fuel_mass=100, temperature=30)
tank2 = gp.ChemicalTank('Tank2', fuel_mass=50, temperature=80)
tank3 = gp.ChemicalTank('Tank3', fuel_mass=60, temperature=25)

tanks = [tank1, tank2, tank3]

thruster1 = gp.ChemicalThruster('Thruster1', tanks, {tank1: 0.5, tank2: 0.3, tank3: 0.2})
thruster2 = gp.ChemicalThruster('Thruster2', tank1)

sc.add_tanks(tanks)
sc.add_thrusters([thruster1, thruster2])

# # Uncomment any of the lines below to view the attributes for that object.
sc.Help()
# thruster1.Help()
# thruster2.Help()
# tank1.Help()
