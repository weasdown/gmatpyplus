import gmatpyplus as gp

from command.gmat_command import GmatCommand


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
        # TODO finish __init__() docstring above.

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
