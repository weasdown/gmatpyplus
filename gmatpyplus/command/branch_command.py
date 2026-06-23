import gmatpyplus as gp
from gmatpyplus import gmat
from gmatpyplus.command.gmat_command import GmatCommand


class BranchCommand(GmatCommand):
    def __init__(self, command_type: str, name: str):
        super().__init__(command_type, name)
        self.command_sequence = []

    def AddBranch(self, command: gp.GmatCommand | gmat.GmatCommand, which: int = 0):
        """
        No return value.
        :param command:
        :param which:
        """
        gp.extract_gmat_obj(self).AddBranch(gp.extract_gmat_obj(command), which)

    def Append(self, command: gp.GmatCommand | gmat.GmatCommand) -> bool:
        command_gmat_obj = gp.extract_gmat_obj(command)
        return gp.extract_gmat_obj(self).Append(command_gmat_obj)
