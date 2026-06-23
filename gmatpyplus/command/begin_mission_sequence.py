import gmatpyplus as gp
from gmatpyplus.command.gmat_command import GmatCommand


class BeginMissionSequence(GmatCommand):
    def __init__(self):
        super().__init__('BeginMissionSequence', 'BeginMissionSequenceCommand')

        self.SetSolarSystem()
        self.SetObjectMap(gp.Moderator().GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gp.Sandbox().GetGlobalObjectMap())

        self.Initialize()
