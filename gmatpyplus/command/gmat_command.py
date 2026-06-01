import gmatpyplus as gp
from gmatpyplus import gmat
from utils import extract_gmat_obj


class GmatCommand:
    def __init__(self, command_type: str, name: str):
        self.command_type: str = command_type

        mod = gp.Moderator()
        self.gmat_obj = mod.CreateDefaultCommand(self.command_type)
        # TODO convert all GmatCommand creation to the native Python form e.g. gmat.Propagate() if appropriate

        # Set GMAT object's name
        self.name: str = name
        self.gmat_obj.SetName(name)  # set obj name, as CreateDefaultCommand does not (Jira issue GMT-8095)

        self.SetObjectMap(mod.GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gp.Sandbox().GetGlobalObjectMap())
        self.SetSolarSystem(gmat.GetSolarSystem())

        # # Excluded object types must have key parameters set before they are initialized
        # if not isinstance(self, (gp.Target, gp.EndTarget, gp.Achieve)):
        #     try:
        #         self.Initialize()
        #     except Exception as ex:
        #         raise RuntimeError(f'{self.command_type} command named "{self.name}" failed to initialize in '
        #                            f'GmatCommand.__init__() - see exception below:\n\t{ex}') from ex

    def AddToMCS(self) -> bool:
        return gp.Moderator().AppendCommand(self)

    def GeneratingString(self):
        print(self.GetGeneratingString())

    def GetGeneratingString(self, mode: int = gmat.NO_COMMENTS, prefix: str = '', use_name: str = 'self.name') -> str:
        use_name = self.name
        return self.gmat_obj.GetGeneratingString(mode, prefix, use_name)

    def GetField(self, field: str) -> str:
        return self.gmat_obj.GetField(field)

    def GetMissionSummary(self):
        return self.gmat_obj.GetStringParameter('MissionSummary')

    def GetName(self) -> str:
        return gp.extract_gmat_obj(self).GetName()

    def GetNext(self):
        return gp.extract_gmat_obj(self).GetNext()

    def GetParameterID(self, param_name: str) -> int:
        return gp.extract_gmat_obj(self).GetParameterID(param_name)

    def GetParameterType(self, param: str | int) -> int:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gp.extract_gmat_obj(self).GetParameterType(param)

    def GetParameterTypeString(self, param: str | int) -> str:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gp.extract_gmat_obj(self).GetParameterTypeString(param)

    def GetRefObject(self, type_id: int, name: str, index: int = 0):
        return gp.extract_gmat_obj(self).GetRefObject(type_id, name, index)

    def GetRefObjectName(self, type_int: int) -> str:
        return self.gmat_obj.GetRefObjectName(type_int)

    def GetStringArrayParameter(self, param: str | int) -> tuple:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gp.extract_gmat_obj(self).GetStringArrayParameter(param)

    def GetStringParameter(self, param: str | int) -> str:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gp.extract_gmat_obj(self).GetStringParameter(param)

    def GetTypeName(self) -> str:
        return extract_gmat_obj(self).GetTypeName()

    def Help(self):
        gp.extract_gmat_obj(self).Help()

    def Initialize(self) -> bool:
        try:
            resp = extract_gmat_obj(self).Initialize()
            if not resp:
                raise RuntimeError('Non-true response from Initialize()')
            return resp

        except Exception as ex:
            ex_str = str(ex).replace("\n", "")
            raise RuntimeError(f'Initialize failed for {type(self).__name__} named "{self.name}". See GMAT error below:'
                               f'\n\tGMAT internal exception/error: {ex_str}') from ex

    def SetBooleanParameter(self, param: str | int, value: bool) -> bool:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gp.extract_gmat_obj(self).SetBooleanParameter(param, value)

    def SetField(self, field: str, value) -> bool:
        return self.gmat_obj.SetField(field, value)

    def SetGlobalObjectMap(self, gom: gmat.ObjectMap) -> bool:
        return extract_gmat_obj(self).SetGlobalObjectMap(gom)

    def SetIntegerParameter(self, param: str | int, value: int) -> bool:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gp.extract_gmat_obj(self).SetIntegerParameter(param, value)

    def SetName(self, name: str) -> bool:
        self.name = name
        return self.gmat_obj.SetName(name)

    def SetObjectMap(self, om: gmat.ObjectMap) -> bool:
        return extract_gmat_obj(self).SetObjectMap(om)

    def SetRefObjectName(self, type_id: int, name: str) -> bool:
        return gp.extract_gmat_obj(self).SetRefObjectName(type_id, name)

    def SetSolarSystem(self, ss: gmat.SolarSystem = gmat.GetSolarSystem()) -> bool:
        return extract_gmat_obj(self).SetSolarSystem(ss)

    def SetStringParameter(self, param: str | int, value: str) -> bool:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gp.extract_gmat_obj(self).SetStringParameter(param, value)

    def Validate(self) -> bool:
        try:
            return self.gmat_obj.Validate()
        except Exception as ex:
            raise RuntimeError(f'{type(self).__name__} named "{self.name}" failed to Validate') from ex
