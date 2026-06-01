import gmatpyplus as gp
from command.gmat_command import GmatCommand
from gmatpyplus import gmat


class EndFiniteBurn(GmatCommand):
    def __init__(self, burn: gp.FiniteBurn | gmat.FiniteBurn, name: str):
        super().__init__('EndFiniteBurn', name)

        # Assign the user-provided FiniteBurn to this command
        self.burn = burn
        self.SetRefObjectName(gmat.FINITE_BURN, self.burn.GetName())

        self.Initialize()
