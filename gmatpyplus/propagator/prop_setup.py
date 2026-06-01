import gmatpyplus as gp
from force_model import ForceModel
from foundation import GmatObject
from propagator.propagator import Propagator


class PropSetup(GmatObject):  # variable called prop in GMAT Python examples
    def __init__(self, name: str, fm: ForceModel = None, gator: Propagator = None,
                 initial_step_size: int = 60, accuracy: int | float = 1e-12, min_step: int = 0, max_step: int = 2700,
                 max_step_attempts: int = 50, stop_if_accuracy_violated: bool = True):
        # TODO add other args as per pg 449 (PDF pg 458) of User Guide
        super().__init__('PropSetup', name)

        # Create a ForceModel and Propagator
        self.force_model = fm if fm else ForceModel()
        self.gator = gator if gator else Propagator()
        self.SetReference(self.gator)

        if initial_step_size is not None:
            self.initial_step_size = initial_step_size
            self.SetRealParameter('InitialStepSize', self.initial_step_size)

        if accuracy is not None:
            self.accuracy = accuracy
            self.SetRealParameter('Accuracy', self.accuracy)

        if min_step is not None:
            self.min_step = min_step
            self.SetRealParameter('MinStep', self.min_step)

        if max_step is not None:
            self.max_step = max_step
            self.SetRealParameter('MaxStep', self.max_step)

        if max_step_attempts is not None:
            self.max_step_attempts = max_step_attempts
            self.SetIntegerParameter('MaxStepAttempts', self.max_step_attempts)

        if stop_if_accuracy_violated is not None:
            self.stop_if_accuracy_violated = stop_if_accuracy_violated
            self.SetBooleanParameter('StopIfAccuracyIsViolated', self.stop_if_accuracy_violated)

        self.SetReference(self.force_model)
        self.psm = self.GetPropStateManager()

        gp.Initialize()
        self.Initialize()

    def AddPropObject(self, sc: gp.Spacecraft):
        obj = gp.extract_gmat_obj(sc)
        self.gmat_obj.AddPropObject(obj)  # GMAT function does not give a return value

    def PrepareInternals(self):
        self.gmat_obj.PrepareInternals()

    def GetPropagator(self):
        return self.gmat_obj.GetPropagator()

    def GetState(self):
        return self.gator.gmat_obj.GetState()

    def GetPropStateManager(self):
        return self.gmat_obj.GetPropStateManager()

    def SetObject(self, sc):
        self.psm.SetObject(sc.gmat_obj)
