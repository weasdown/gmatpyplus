import gmatpyplus as gp
from gmatpyplus.command.solver_branch_command import SolverBranchCommand
from gmatpyplus import gmat


class Target(SolverBranchCommand):
    def __init__(self, name: str, solver: gp.DifferentialCorrector | gmat.DifferentialCorrector,
                 solve_mode: str = 'Solve', exit_mode: str = 'SaveAndContinue',
                 command_sequence: list[gp.GmatCommand] = None, show_progress_window: bool = False):
        if command_sequence is None:
            # Make sure the command sequence includes at least an EndTarget command
            command_sequence = [gp.EndTarget(self, f'EndTarget for Target "{self.name}"')]

        super().__init__('Target', name)

        self.command_sequence = command_sequence

        # Get default solver then replace if the user has provided a solver object
        self.def_solver_name = self.GetRefObjectName(gmat.SOLVER)
        self.solver = gmat.GetObject(self.def_solver_name)
        if solver:
            self.solver: gp.DifferentialCorrector | gmat.DifferentialCorrector = solver
            new_solver_name = self.solver.GetName()
            self.SetStringParameter('Targeter', new_solver_name)

        self.solve_mode = solve_mode
        self.SetStringParameter('SolveMode', self.solve_mode)

        self.exit_mode = exit_mode
        self.SetStringParameter('ExitMode', self.exit_mode)

        self.command_sequence: list[gp.GmatCommand] = command_sequence

        self.show_progress_window = show_progress_window
        self.SetBooleanParameter('ShowProgressWindow', self.show_progress_window)

        self.SetSolarSystem()
        self.SetObjectMap(gp.Moderator().GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gp.Sandbox().GetGlobalObjectMap())

        # # Make sure the final item in the command sequence is an EndTarget object
        if not isinstance(command_sequence[-1], gmat.EndTarget | gp.EndTarget):
            command_sequence.append(gp.EndTarget(self))

        # Add each of Target's sub-commands to the mission sequence
        for command in self.command_sequence:
            self.Append(gp.extract_gmat_obj(command))
