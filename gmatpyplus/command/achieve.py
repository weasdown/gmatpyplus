import gmatpyplus as gp
from gmatpyplus import gmat
from gmatpyplus.command.gmat_command import GmatCommand
from gmatpyplus.utils import extract_gmat_obj


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
