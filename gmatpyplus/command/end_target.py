import gmatpyplus as gp
from command.branch_command import BranchCommand
from gmatpyplus import gmat


class EndTarget(BranchCommand):
    def __init__(self, parent_target: gp.Target, name: str = None):
        if name is None:
            name = f'EndTarget_{parent_target.GetName()}'

        super().__init__('EndTarget', name)

    def Insert(self, command: gp.GmatCommand | gmat.GmatCommand,
               prev: gp.GmatCommand | gmat.GmatCommand = None) -> bool:
        command = gp.extract_gmat_obj(command)
        prev = gp.extract_gmat_obj(prev) if prev is not None else None
        return gp.extract_gmat_obj(self).Insert(command, prev)
