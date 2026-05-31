from __future__ import annotations

import gmatpyplus as gp

from gmatpyplus import gmat


class Validator:
    def __init__(self):
        self.gmat_obj = gmat.Validator.Instance()
        self.SetSolarSystem(gmat.GetSolarSystem())
        self.SetObjectMap(gp.Moderator().GetConfiguredObjectMap())

    def CreateParameter(self, param_type: str, value: str | int | float):
        return self.gmat_obj.CreateParameter(param_type, value)

    def CreateSystemParameter(self, param_created: bool, name: str, manage: int = 1):
        # TODO bugfix: param_created bool not accepted - see GMT-8100 on Jira
        if manage not in [0, 1, 2]:
            raise SyntaxError('manage argument must be 0, 1 or 2')

        return self.gmat_obj.CreateSystemParameter(param_created, name, manage)

    def FindObject(self, name: str):
        return gp.extract_gmat_obj(self).FindObject(name)

    def SetObjectMap(self, om: gmat.ObjectMap) -> bool:
        return gp.extract_gmat_obj(self).SetObjectMap(om)

    def SetSolarSystem(self, ss: gmat.SolarSystem = gmat.GetSolarSystem()) -> bool:
        return gp.extract_gmat_obj(self).SetSolarSystem(ss)

    def ValidateCommand(self, command: gp.GmatCommand | gmat.GmatCommand):
        return gp.extract_gmat_obj(self).ValidateCommand(gp.extract_gmat_obj(command))
