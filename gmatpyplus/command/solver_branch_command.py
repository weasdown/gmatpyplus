from gmatpyplus.command.branch_command import BranchCommand


class SolverBranchCommand(BranchCommand):
    def __init__(self, command_type: str, name: str):
        super().__init__(command_type, name)
