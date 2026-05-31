from __future__ import annotations

from math import pi

from command.branch_command import BranchCommand
from command.gmat_command import GmatCommand
from command.solver_branch_command import SolverBranchCommand
from command.solver_sequence_command import SolverSequenceCommand
from gmatpyplus import gmat
from gmatpyplus.utils import *


class Achieve(GmatCommand):
    def __init__(self, name: str, solver: gp.DifferentialCorrector | gmat.DifferentialCorrector,
                 variable: str, value: int | float, tolerance: float | int = 0.1):
        super().__init__('Achieve', name)

        self.solver: gp.DifferentialCorrector | gmat.DifferentialCorrector = solver
        self.SetStringParameter('TargeterName', self.solver.GetName())
        self.SetRefObject(self.solver, gmat.SOLVER, self.solver.GetName())

        self.variable = variable
        self.SetStringParameter('Goal', self.variable)

        # Make Parameter for Goal if one doesn't already exist
        if not gp.Moderator().GetParameter(self.variable):
            param_eles = self.variable.split('.')
            param_type = param_eles[-1]
            new_param = gp.Parameter(param_type, self.variable)

            for ele in param_eles:
                if ele in gp.CoordSystems():
                    # print(f'Updating CS for {new_param.GetName()}')
                    # Update the Parameter's COORDINATE_SYSTEM
                    new_param.SetRefObjectName(gmat.COORDINATE_SYSTEM, ele)
                    cs = gmat.GetObject(ele)
                    new_param.SetRefObject(cs, gmat.COORDINATE_SYSTEM)

                    # Also update the Parameter's SPACE_POINT
                    # print(f'Updating CB for {new_param.GetName()}')
                    body = cs.GetField('Origin')
                    new_param.SetRefObjectName(gmat.SPACE_POINT, body)
                    new_param.SetRefObject(gmat.GetObject(body), gmat.SPACE_POINT)

                if ele in gp.SpacecraftObjs():
                    # print(f'Updating S/C for {new_param.GetName()}')
                    # Update the Parameter's SPACECRAFT
                    new_param.SetRefObjectName(gmat.SPACECRAFT, ele)
                    sc = gmat.GetObject(ele)
                    new_param.SetRefObject(sc, gmat.SPACECRAFT)

                if ele in gp.CelestialBodies():
                    # print(f'Updating CB for {new_param.GetName()}')
                    # Update the Parameter's CELESTIAL_BODY (even if COORDINATE_SYSTEM not updated)
                    new_param.SetRefObjectName(gmat.CELESTIAL_BODY, ele)
                    new_param.SetRefObject(gmat.GetObject(ele), gmat.CELESTIAL_BODY)

            new_param.SetSolarSystem(gmat.GetSolarSystem())
            new_param.Initialize()
            # self.SetRefObject(new_param.gmat_base, gmat.PARAMETER)

        #     # param_type is the final element of the self.variable string, e.g. Periapsis for Sat.Earth.Periapsis
        #     param_eles = self.variable.split('.')
        #     param_type = param_eles[-1]
        # new_param = gp.Parameter(param_type, self.variable)
        # for ele in param_eles:
        #     body = 'Earth'
        #     cs = 'EarthMJ2000Eq'
        #     if ele in gp.CelestialBodies():  # a CelestialBody is given, so need to set it as a ref object
        #         # TODO: test this
        #         body = ele
        #
        #     if ele in gp.CoordSystems():
        #         cs = ele
        #
        #     pass
        # new_param.SetRefObjectName(gmat.SPACE_POINT, body)
        # new_param.SetRefObjectName(gmat.COORDINATE_SYSTEM, cs)
        # new_param.Help()
        # print(new_param.gmat_base.GetRefObjectTypeArray())
        # new_param.SetRefObjectName(gmat.CELESTIAL_BODY, ele)

        #     if ele in gp.CoordSystems():  # a CoordinateSystem is given, so need to set it as a ref object
        #         # TODO remove (debugging only)
        #         test_bddot = gmat.Construct('BdotT', 'TestBdotT')
        #         test_bddot.SetRefObjectName(gmat.SPACECRAFT, 'MAVEN')
        #         # test_bddot.SetReference(gmat.GetObject('MAVEN'))
        #         # print(gp.Moderator().gmat_obj.GetListOfFactoryItems(gmat.PARAMETER))
        #         # test_bddot.RenameRefObject(gmat.COORDINATE_SYSTEM, 'EarthMJ2000Eq', ele)
        #         test_bddot.SetRefObjectName(gmat.COORDINATE_SYSTEM, ele)
        #         cs = gmat.GetObject(ele)
        #         test_bddot.SetRefObject(cs, gmat.COORDINATE_SYSTEM, cs.GetName())
        #
        #         # test_bddot.SetRefObjectName(gmat.SPACECRAFT, 'MAVEN')
        #         test_bddot.SetRefObject(gmat.GetObject('MAVEN'), gmat.SPACECRAFT, 'MAVEN')
        #
        #         test_bddot.SetSolarSystem(gmat.GetSolarSystem())
        #         # gmat.Initialize()
        #         mod = gp.Moderator().gmat_obj
        #         mod.SetParameterRefObject(test_bddot, 'BdotT', cs.GetName(), '', '', 1)
        #         test_bddot.Help()
        #         test_bddot.Initialize()
        #
        #         new_param.SetRefObjectName(gmat.COORDINATE_SYSTEM, ele)
        #         # new_param.SetStringParameter(new_param.GetParameterID('CoordinateSystem'), ele)
        #         # new_param.SetRefObject(gmat.GetObject(ele), gmat.COORDINATE_SYSTEM)
        #         new_param.Help()
        #         pass
        #
        # for body in gp.CelestialBodies():
        #     if body in self.variable:
        #         new_param.SetRefObject(gmat.Planet(body), gmat.COORDINATE_SYSTEM)

        self.value = value
        self.SetStringParameter('GoalValue', str(self.value))

        self.tolerance = tolerance
        self.SetStringParameter('Tolerance', str(self.tolerance))

        self.SetSolarSystem()
        self.SetObjectMap(gp.Moderator().GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gp.Sandbox().GetGlobalObjectMap())

        self.Initialize()
        # print(self.GetGeneratingString())
        # gp.Initialize()
        # self.Initialize()

    def SetRefObject(self, obj, type_int: int, obj_name: str = '') -> bool:
        return extract_gmat_obj(self).SetRefObject(extract_gmat_obj(obj), type_int, obj_name)


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


class BeginMissionSequence(GmatCommand):
    def __init__(self):
        super().__init__('BeginMissionSequence', 'BeginMissionSequenceCommand')

        self.SetSolarSystem()
        self.SetObjectMap(gp.Moderator().GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gp.Sandbox().GetGlobalObjectMap())

        self.Initialize()


class EndFiniteBurn(GmatCommand):
    def __init__(self, burn: gp.FiniteBurn | gmat.FiniteBurn, name: str):
        super().__init__('EndFiniteBurn', name)

        # Assign the user-provided FiniteBurn to this command
        self.burn = burn
        self.SetRefObjectName(gmat.FINITE_BURN, self.burn.GetName())

        self.Initialize()


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


class Maneuver(GmatCommand):
    def __init__(self, name: str, burn: gp.ImpulsiveBurn | gp.FiniteBurn, spacecraft: gp.Spacecraft,
                 backprop: bool = False):
        """
        Create a Maneuver command.

        :param name:
        :param burn:
        :param spacecraft:
        :param backprop:
        """

        super().__init__('Maneuver', name)

        self.burn = burn
        self.SetStringParameter(self.gmat_obj.GetParameterID('Burn'), self.burn.name)

        self.spacecraft = spacecraft
        self.SetStringParameter(self.gmat_obj.GetParameterID('Spacecraft'), self.spacecraft.name)
        self.burn.SetSpacecraftToManeuver(self.spacecraft)  # update burn's assigned spacecraft

        self.backprop = backprop
        self.SetBooleanParameter(self.gmat_obj.GetParameterID('BackProp'), self.backprop)

        self.SetSolarSystem()
        self.SetObjectMap(gp.Moderator().GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gp.Sandbox().GetGlobalObjectMap())

        self.Initialize()


# class PropagateMulti(Propagate):
#     # TODO: consider making this a nested/inner class of Propagate, so would call Propagate.Multi()
#     """
#     Note: this command does not exist in standard GMAT. It is here to reduce ambiguity when propagating multiple
#      spacecraft. This class can only be used to propagate multiple spacecraft - to propagate a single spacecraft, use
#       Propagate (which only suports a single spacecraft).
#
#     """
#
#     def __init__(self, name: str = None, prop: gp.PropSetup = None, sat: gp.Spacecraft = None,
#                  stop_cond: Propagate.StopCondition = None, synchronized: bool = False):
#         if not name:  # make sure the new Propagate has a unique name
#             num_propagates: int = len(gmat.GetCommands('Propagate'))
#             name = f'PropagateMulti{num_propagates + 1}'
#
#         super().__init__(name, prop, sat, stop_cond, synchronized)


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


class Vary(SolverSequenceCommand):
    def __init__(self, name: str, solver: gp.DifferentialCorrector | gmat.DifferentialCorrector, variable: str,
                 initial_value: float | int = 1, perturbation: float | int = 0.0001, lower: float | int = 0.0,
                 upper: float | int = pi, max_step: float | int = 0.5, additive_scale_factor: float | int = 0.0,
                 multiplicative_scale_factor: float | int = 1.0):

        user_created_def_ib = False
        def_ib_name = 'DefaultIB'
        def_ib_ele_name = 'DefaultIB.Element1'
        try:
            # an object named DefaultIB existed before Vary's init created one, so assume it's user-owned
            if gmat.GetObject('DefaultIB'):
                user_created_def_ib = True
        except AttributeError:
            # DefaultIB wasn't found, so does not exist
            pass

        super().__init__('Vary', name)

        self.solver = solver
        self.SetRefObject(self.solver, gmat.SOLVER, self.solver.GetName())
        self.SetStringParameter('SolverName', self.solver.GetName())

        self.variable = variable
        self.SetStringParameter('Variable', self.variable)

        if initial_value < lower:
            raise RuntimeError('initial_value is less than lower (minimum value) in Vary.__init__().'
                               f'\n- initial_value:\t{initial_value}'
                               f'\n- lower:\t\t\t{lower}')
        if initial_value > upper:
            raise RuntimeError('initial_value is greater than upper (maximum value) in Vary.__init__().'
                               f'\n- initial_value:\t{initial_value}'
                               f'\n- upper:\t\t\t{upper}')

        self.initial_value = initial_value
        self.SetStringParameter('InitialValue', str(self.initial_value))

        self.perturbation = perturbation
        self.SetStringParameter('Perturbation', str(self.perturbation))

        self.lower = lower
        self.SetStringParameter('Lower', str(self.lower))

        self.upper = upper
        self.SetStringParameter('Upper', str(self.upper))

        self.max_step = max_step
        self.SetStringParameter('MaxStep', str(self.max_step))

        self.additive_scale_factor = additive_scale_factor
        self.SetStringParameter('AdditiveScaleFactor', str(self.additive_scale_factor))

        self.multiplicative_scale_factor = multiplicative_scale_factor
        self.SetStringParameter('MultiplicativeScaleFactor', str(self.multiplicative_scale_factor))

        self.SetSolarSystem()
        self.SetObjectMap(gp.Moderator().GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gp.Sandbox().GetGlobalObjectMap())

        self.Initialize()

        # If a DefaultIB object exists and the user didn't create it, GMAT did while building this command - delete it
        if not user_created_def_ib:
            gmat.Clear(def_ib_name)

        # print(self.GetGeneratingString())

    def RenameRefObject(self, type_id: int, old_name: str, new_name: str) -> bool:
        return gp.extract_gmat_obj(self).RenameRefObject(type_id, old_name, new_name)

    def SetRefObject(self, obj: gmat.GmatBase, type_id: int, name: str) -> bool:
        return gp.extract_gmat_obj(self).SetRefObject(gp.extract_gmat_obj(obj), type_id, name)
