from math import pi

import gmatpyplus as gp
from gmatpyplus.command.solver_sequence_command import SolverSequenceCommand
from gmatpyplus import gmat


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
