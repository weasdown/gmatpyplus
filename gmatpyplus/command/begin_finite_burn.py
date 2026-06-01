import gmatpyplus as gp
from gmatpyplus import gmat
from gmatpyplus.command.gmat_command import GmatCommand


class BeginFiniteBurn(GmatCommand):
    def __init__(self, burn: gp.FiniteBurn | gmat.FiniteBurn, spacecraft: gp.Spacecraft | gmat.Spacecraft,
                 name: str = ''):
        super().__init__('BeginFiniteBurn', name)

        # Assign the user-provided FiniteBurn to this command
        self.burn = burn
        self.SetRefObjectName(gmat.FINITE_BURN, self.burn.GetName())

        # Assign the user-provided Spacecraft to the FiniteBurn
        self.spacecraft = spacecraft
        self.burn.SetRefObject(self.spacecraft, gmat.SPACECRAFT, self.spacecraft.GetName())
        # self.spacecraft.Help()
        # print(type(self.spacecraft))
        # self.burn.SetSpacecraftToManeuver(gp.extract_gmat_obj(self.spacecraft))  # update FiniteBurn's associated Spacecraft
        gp.FiniteBurn.SetSpacecraftToManeuver(self.burn, gp.extract_gmat_obj(
            self.spacecraft))  # update FiniteBurn's associated Spacecraft

        self.Initialize()
