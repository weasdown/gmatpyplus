from gmatpyplus.command.gmat_command import GmatCommand


class SolverSequenceCommand(GmatCommand):
    def __init__(self, command_type: str, name: str):
        super().__init__(command_type, name)
