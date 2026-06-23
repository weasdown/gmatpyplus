import gmatpyplus as gp
from gmatpyplus import gmat
from gmatpyplus.command.gmat_command import GmatCommand
from gmatpyplus.stop_condition import StopCondition
from gmatpyplus.utils import extract_gmat_obj


class Propagate(GmatCommand):
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
            self.stop_cond: StopCondition = StopCondition(self.sat, stop_cond=self.user_stop_cond,
                                                          gmat_obj=self.stop_cond)
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
