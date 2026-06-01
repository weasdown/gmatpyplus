import gmatpyplus as gp
from command.gmat_command import GmatCommand
from gmatpyplus import gmat
from utils import extract_gmat_obj


class Propagate(GmatCommand):
    class StopCondition:
        def __init__(self, sat: gmat.Spacecraft | gp.Spacecraft, stop_cond: str | tuple,
                     gmat_obj: gmat.StopCondition | gmat.GmatBase):
            self.sat = sat
            self.sat_name = self.sat.GetName()
            self.body = 'Earth'  # TODO remove hard-coding

            self.epoch_var = None
            self.epoch_param_type = None

            self.stop_var = None
            self.stop_param_type = None

            # TODO complete this types/properties list based on options available in GUI Propagate command
            self.stop_param_allowed_types = {
                'Spacecraft': ['A1ModJulian', 'Acceleration', 'AccelerationX', 'AccelerationY', 'AccelerationZ',
                               'AltEquinoctialP', 'AltEquinoctialQ', 'Altitude', 'AngularVelocityX', 'AngularVelocityY',
                               'AngularVelocityZ', 'AOP', 'Apoapsis', 'AtmosDensity', 'AtmosDensityScaleFactor',
                               'AtmosDensityScaleFactorSigma', 'AZI', 'BdotR', 'BdotT', 'BetaAngle', 'BrouwerLongAOP',
                               'BrouwerLongECC', 'BrouwerLongINC', 'BrouwerLongMA', 'BrouwerLongRAAN', 'BrouwerLongSMA',
                               'BrouwerShortAOP', 'BrouwerShortECC', 'BrouwerShortINC', 'BrouwerShortMA',
                               'BrouwerShortRAAN', 'BrouwerShortSMA', 'BVectorAngle', 'BVectorMag', 'C3Energy', 'Cd',
                               'CdSigma', 'Cr', 'CrSigma', 'DCM11', 'DCM12', 'DCM13', 'DCM21', 'DCM22', 'DCM23',
                               'DCM31',
                               'DCM32', 'DCM33', 'DEC', 'DECV', 'DelaunayG', 'Delaunayg', 'DelaunayH', 'Delaunayh',
                               'DelaunayL', 'Delaunayl', 'DLA', 'DragArea', 'DryCenterOfMassX', 'DryCenterOfMassY',
                               'DryCenterOfMassZ', 'DryMass', 'DryMassMomentOfInertiaXX', 'DryMassMomentOfInertiaXY',
                               'DryMassMomentOfInertiaXZ', 'DryMassMomentOfInertiaYY', 'DryMassMomentOfInertiaYZ',
                               'DryMassMomentOfInertiaZZ', 'EA', 'ECC', 'ElapsedDays', 'ElapsedSecs', 'Energy',
                               'EquinoctialH', 'EquinoctialHDot', 'EquinoctialK', 'EquinoctialKDot', 'EquinoctialP',
                               'EquinoctialPDot', 'EquinoctialQ', 'EquinoctialQDot', 'EulerAngle1', 'EulerAngle2',
                               'EulerAngle3', 'EulerAngleRate1', 'EulerAngleRate2', 'EulerAngleRate3', 'FPA', 'HA',
                               'HMAG',
                               'HX', 'HY', 'HZ', 'INC', 'IncomingBVAZI', 'IncomingC3Energy', 'IncomingDHA',
                               'IncomingRadPer',
                               'IncomingRHA', 'Latitude', 'Longitude', 'LST', 'MA', 'MHA', 'MLONG', 'MM',
                               'ModEquinoctialF',
                               'ModEquinoctialG', 'ModEquinoctialH', 'ModEquinoctialK', 'MRP1', 'MRP2', 'MRP3',
                               'OrbitPeriod',
                               'OrbitTime', 'OutgoingBVAZI', 'OutgoingC3Energy', 'OutgoingDHA', 'OutgoingRadPer',
                               'OutgoingRHA', 'Periapsis', 'PlanetodeticAZI', 'PlanetodeticHFPA', 'PlanetodeticLAT',
                               'PlanetodeticLON', 'PlanetodeticRMAG', 'PlanetodeticVMAG', 'Q1', 'Q2', 'Q3', 'Q4', 'RA',
                               'RAAN',
                               'RadApo', 'RadPer', 'RAV', 'RLA', 'RMAG', 'SemilatusRectum', 'SMA',
                               'SPADDragScaleFactor',
                               'SPADDragScaleFactorSigma', 'SPADSRPScaleFactor', 'SPADSRPScaleFactorSigma', 'SRPArea',
                               'SystemCenterOfMassX', 'SystemCenterOfMassY', 'SystemCenterOfMassZ',
                               'SystemMomentOfInertiaXX',
                               'SystemMomentOfInertiaXY', 'SystemMomentOfInertiaXZ', 'SystemMomentOfInertiaYY',
                               'SystemMomentOfInertiaYZ', 'SystemMomentOfInertiaZZ', 'TA', 'TAIModJulian',
                               'TDBModJulian',
                               'TLONG', 'TLONGDot', 'TotalMass', 'TTModJulian', 'UTCModJulian', 'VelApoapsis',
                               'VelPeriapsis',
                               'VMAG', 'VX', 'VY', 'VZ', 'X', 'Y', 'Z']}

            self.goal = None
            self.goal_param_type = None
            self.goalless = None

            self.gmat_obj = gmat_obj
            self.name: str = self.gmat_obj.GetName()

            self.epoch_var: str = self.gmat_obj.GetStringParameter('EpochVar')
            self.epoch_param_type = None  # TODO get correct param type

            self.stop_var: str = self.gmat_obj.GetStringParameter('StopVar')
            self.stop_param_type = None  # TODO get correct param type

            self.goal: str = self.gmat_obj.GetStringParameter('Goal')
            self.goalless = None  # TODO determine correct goalless value or remove attribute entirely if not needed

            (self.stop_param_type,
             self.stop_var,
             self.epoch_param_type,
             self.epoch_var,
             self.goal,
             self.goalless,
             self.body) = self.parse_user_stop_cond(stop_cond)

            self.name = f'StopOn{self.stop_var}'
            self.SetName(self.name)

            self.apply_stop_cond_params(self.epoch_param_type, self.epoch_var, self.stop_param_type, self.stop_var,
                                        self.goal)

        def apply_stop_cond_params(self, epoch_param_type: str, epoch_var: str, stop_param_type: str, stop_var: str,
                                   goal: str | int | float):
            self.SetStringParameter('EpochVar', epoch_var)
            self.SetStringParameter('StopVar', stop_var)
            self.SetStringParameter('Goal', str(goal))

            mod = gp.Moderator()
            validator = gp.Validator()
            validator.SetSolarSystem(gmat.GetSolarSystem())
            validator.SetObjectMap(mod.GetConfiguredObjectMap())

            sat_name = self.sat.GetName()

            # if an epoch parameter does not already exist, make one
            if not mod.GetParameter(epoch_var):
                validator.CreateParameter(epoch_param_type, epoch_var)  # create a Parameter for epoch_var
                param = gp.Validator().FindObject(epoch_var)
                param.SetRefObjectName(gmat.SPACECRAFT, sat_name)  # attach Spacecraft to Parameter

            # if a stop parameter does not already exist, make one
            if not mod.GetParameter(stop_var):
                validator.CreateParameter(stop_param_type, stop_var)  # create a Parameter for stop_var
                param = gp.Validator().FindObject(stop_var)
                param.SetRefObjectName(gmat.SPACECRAFT, sat_name)  # attach Spacecraft to Parameter

        def GetStringParameter(self, param_name: str) -> str:
            return self.gmat_obj.GetStringParameter(param_name)

        def _name_mismatch_error(self, _stop_cond, _sat_name: str):
            return RuntimeError(
                f'Name of satellite given in StopCondition "{_stop_cond}" ({_sat_name}) does'
                f' not match name for Propagate\'s satellite ({self.sat_name})')

        def parse_user_stop_cond(self, stop_cond: str | tuple):
            # TODO feature: convert tuple to 2 or 3 element.
            #  Examples: 2: (sat.name, 'Earth.Periapsis'), 3: (sat.name, 'ElapsedSecs', 12000.0)

            # TODO: get stop_tolerance from stop_cond (no example yet but see pg 652/PDF pg 661 of User Guide)

            if isinstance(stop_cond, tuple) and len(stop_cond) == 2:  # most likely. E.g. ('Sat.ElapsedSecs', 12000)
                stop_var = stop_cond[0]
                sat_from_stop_cond, parameter = stop_var.split('.')
                goal = str(stop_cond[1])

            elif isinstance(stop_cond, str):  # e.g. 'Sat.Earth.Apoapsis'
                stop_var = stop_cond
                sat_from_stop_cond, body, parameter = stop_var.split('.')
                goal = 0

            else:
                # TODO: definitely max of 2 elements?
                raise RuntimeError(f'stop_cond is invalid. Must be a 2-element tuple or a string. Given value: '
                                   f'{stop_cond}')

            stop_var_elements = stop_var.split('.')
            num_stop_var_elements = len(stop_var_elements)

            if num_stop_var_elements == 2:
                sat_name, parameter = stop_var.split('.')
                if sat_name != self.sat.name:
                    raise self._name_mismatch_error(stop_cond, sat_name)
                stop_var = '.'.join([sat_name, parameter])

                # Get body from satellite's coordinate system
                coord_sys_name = gp.GetObject(sat_name).GetField('CoordinateSystem')
                coord_sys_obj = gp.GetObject(coord_sys_name)
                body = coord_sys_obj.GetField('Origin')

            elif num_stop_var_elements == 3:
                sat_name, body, parameter = stop_var.split('.')
                if sat_name != self.sat.name:
                    raise self._name_mismatch_error(stop_cond, sat_name)

            else:
                raise SyntaxError('Invalid number of parts for stop_cond. Must be two (e.g. "Sat.ElapsedSecs") or three'
                                  '(e.g. "Sat.Earth.Periapsis")')

            stop_param_type = stop_var[len(self.sat.GetName()) + 1:]  # remove sat name and . from stop_var

            # following types taken from src/Moderator.CreateDefaultParameters() Time parameters section
            allowed_epoch_param_types = ['ElapsedSecs', 'ElapsedDays', 'A1ModJulian', 'A1Gregorian',
                                         'TAIModJulian', 'TAIGregorian', 'TTModJulian', 'TTGregorian',
                                         'TDBModJulian', 'TDBGregorian', 'UTCModJulian', 'UTCGregorian']
            # TODO: remove hard-coding of epoch_param_type
            # TODO: decide when to use other epoch_param_types
            epoch_param_type = 'A1ModJulian'
            epoch_var = f'{sat_from_stop_cond}.{epoch_param_type}'

            goalless = False
            goalless_params = ['Apoapsis', 'Periapsis']  # TODO: complete list

            # see whether any goalless param names exist in the stop_var string
            if any(x in stop_var for x in goalless_params):
                goalless = True
                stop_param_type = stop_var_elements[len(stop_var_elements) - 1]  # e.g. 'Periapsis'

            return stop_param_type, stop_var, epoch_param_type, epoch_var, goal, goalless, body

        def SetName(self, name: str) -> bool:
            return extract_gmat_obj(self).SetName(name)

        ## TODO refactor to use method from an ancestor class.
        def SetIntegerParameter(self, param_name: str, value: int):
            return extract_gmat_obj(self).SetIntegerParameter(param_name, int(value))

        ## TODO refactor to use method from an ancestor class.
        def SetRealParameter(self, param_name: str, value: float):
            return extract_gmat_obj(self).SetStringParameter(param_name, value)

        ## TODO refactor to use method from an ancestor class.
        def SetStringParameter(self, param_name: str, value: str):
            return extract_gmat_obj(self).SetStringParameter(param_name, str(value))

    def __init__(self, name: str, sat: gp.Spacecraft | gmat.Spacecraft, prop: gp.PropSetup | gmat.GmatBase,
                 user_stop_cond: tuple | str):
        # TODO add None as default for sat, prop, stop_cond and handle appropriately in __init__()
        super().__init__('Propagate', name)
        self.Initialize()

        # Get names of Propagate's ref objects and extract the objects
        prop_ref_name = self.GetRefObjectName(gmat.PROP_SETUP)
        sat_ref_name = self.GetRefObjectName(gmat.SPACECRAFT)

        self.prop = self.GetRefObject(gmat.PROP_SETUP, prop_ref_name)  # use default PropSetup initially
        # apply any user-provided PropSetup
        if prop:
            self.prop = prop
            # clear existing prop to replace it (also clears sat)
            self.TakeAction('Clear', 'Propagator')
            self.SetObject(prop.GetName(), gmat.PROP_SETUP)

        self.sat = gmat.GetObject(sat_ref_name)  # GetRefObject() throws exception for Spacecraft - use gmat.GetObject()
        # apply any user-provided Spacecraft
        if sat:
            self.sat = sat
            self.SetRefObjectName(gmat.SPACECRAFT, self.sat.GetName())

        # TODO confirm this still works if there are multiple stop conditions in the script.
        self.stop_cond = self.GetGmatObject(gmat.STOP_CONDITION)

        # apply any user-provided stop condition
        if user_stop_cond:
            self.user_stop_cond = user_stop_cond
            # update default StopCondition with user-provided values by converting to wrapper StopCondition
            self.stop_cond = self.StopCondition(self.sat, stop_cond=self.user_stop_cond, gmat_obj=self.stop_cond)
            self.TakeAction('Clear', 'StopCondition')  # clear existing StopCond to replace it
            self.SetRefObject(extract_gmat_obj(self.stop_cond), gmat.STOP_CONDITION, self.stop_cond.name)

    def GetGmatObject(self, type_int: int):
        return self.gmat_obj.GetGmatObject(type_int)

    def parse_user_stop_cond(self, stop_cond: str | tuple):
        # TODO feature: convert tuple to 2 or 3 element.
        #  Examples: 2: (sat.name, 'Earth.Periapsis'), 3: (sat.name, 'ElapsedSecs', 12000.0)

        # TODO: get stop_tolerance from stop_cond (no example yet but see pg 652/PDF pg 661 of User Guide)

        if isinstance(stop_cond, tuple) and len(stop_cond) == 2:  # most likely. E.g. ('Sat.ElapsedSecs', 12000)
            stop_var = stop_cond[0]
            goal = str(stop_cond[1])

        elif isinstance(stop_cond, str):  # e.g. 'Sat.Earth.Apoapsis'
            stop_var = stop_cond
            goal = str(stop_var)

        else:
            # TODO: definitely max of 2 elements?
            raise RuntimeError(f'stop_cond is invalid. Must be a 2-element tuple or a string. Given value: '
                               f'{stop_cond}')

        stop_var_elements = stop_var.split('.')
        num_stop_var_elements = len(stop_var_elements)
        if num_stop_var_elements == 2:
            sat, parameter = stop_var.split('.')
            stop_var = '.'.join([sat, parameter])

            # Get body from satellite's coordinate system
            coord_sys_name = gmat.GetObject(sat).GetField('CoordinateSystem')
            coord_sys_obj = gmat.GetObject(coord_sys_name)
            body = coord_sys_obj.GetField('Origin')

        elif num_stop_var_elements == 3:
            sat_from_stop_cond, body, parameter = stop_var.split('.')
            sat_name = self.sat.GetName()
            if sat_from_stop_cond != sat_name:
                raise RuntimeError(
                    f'Name of satellite given in StopCondition "{stop_cond}" ({sat_from_stop_cond}) does'
                    f' not match name for Propagate\'s satellite ({sat_name})')
        else:
            raise SyntaxError('Invalid number of parts for stop_cond. Must be two (e.g. "Sat.ElapsedSecs") or three'
                              '(e.g. "Sat.Earth.Periapsis")')

        stop_param_type = stop_var[len(self.sat.GetName()) + 1:]  # remove sat name and . from stop_var

        # following types taken from src/Moderator.CreateDefaultParameters() Time parameters section
        allowed_epoch_param_types = ['ElapsedSecs', 'ElapsedDays', 'A1ModJulian', 'A1Gregorian',
                                     'TAIModJulian', 'TAIGregorian', 'TTModJulian', 'TTGregorian',
                                     'TDBModJulian', 'TDBGregorian', 'UTCModJulian', 'UTCGregorian']
        # TODO: remove hard-coding of epoch_param_type
        # TODO: decide when to use other epoch_param_types
        epoch_param_type = 'A1ModJulian'
        epoch_var = f'{self.sat.GetName()}.{epoch_param_type}'

        goalless = False
        goalless_params = ['Apoapsis', 'Periapsis']  # TODO: complete list

        # goalless parameter found
        if any(x in goal for x in goalless_params):
            goalless = True
            stop_param_type = stop_var_elements[len(stop_var_elements) - 1]  # e.g. 'Periapsis'
            goal_param_type = stop_param_type  # e.g. 'Periapsis'
            goal = stop_var  # TODO remove - [len(self.sat_name) + 1:]  # remove sat_name, e.g. 'Earth.Periapsis'

        else:  # stop condition is not goalless
            # goal already parsed above
            goal_param_type = stop_param_type

        return stop_param_type, stop_var, epoch_param_type, epoch_var, goal_param_type, goal, goalless, body

    def SetObject(self, obj_name: str, type_int: int):
        return extract_gmat_obj(self).SetObject(obj_name, type_int)

    def SetRefObject(self, obj, type_int: int, obj_name: str, index: int = 0) -> bool:
        return extract_gmat_obj(self).SetRefObject(extract_gmat_obj(obj), type_int, obj_name, index)

    def TakeAction(self, action: str, action_data: str) -> bool:
        return extract_gmat_obj(self).TakeAction(action, action_data)

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
