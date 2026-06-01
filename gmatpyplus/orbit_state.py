from __future__ import annotations

import gmatpyplus as gp
from basics import GmatObject
from gmatpyplus import gmat
from utils import Barycenter, CelestialBodies, CoordSystems, gmat_str_to_py_str, GroundStations, LibrationPoints, \
    SpacecraftObjs, py_str_to_gmat_str


class OrbitState:
    class CoordinateSystem(GmatObject):
        # TODO convert __init__ params to args with default values

        # TODO complete - will be able to create each type of Axes, for use in CoordinateSystem
        class Axes(GmatObject):
            def __init__(self, axes_type: str, name: str):
                super().__init__(axes_type, name)
                self.Initialize()

        def __init__(self, name: str, origin: str = 'Earth', axes: str = 'MJ2000Eq', primary: str = None,
                     secondary: str = None, xaxis: str = None, yaxis: str = None, zaxis: str = None, epoch: str = None,
                     alignment_vec_x: int = None, alignment_vec_y: int = None, alignment_vec_z: int = None,
                     constraint_vec_x: int = None, constraint_vec_y: int = None, constraint_vec_z: int = None,
                     constraint_ref_vec_x: int = None, constraint_ref_vec_y: int = None,
                     constraint_ref_vec_z: int = None,
                     constraint_coord_sys: str = None, ref_object: str = None
                     ):
            # TODO: remove kwargs if possible, if not document as another 2do
            # TODO complete allowed values - see User Guide pages 335-339 (PDF pg 344-348)
            #  and src/base/coordsystem/CoordinateSystem.cpp/CreateLocalCoordinateSystem
            super().__init__('CoordinateSystem', name)
            self.allowed_values = {'Axes': ['MJ2000Eq', 'MJ2000Ec', 'ICRF',
                                            'MODEq', 'MODEc', 'TODEq', 'TODEc', 'MOEEq', 'MOEEc', 'TOEEq', 'TOEEc',
                                            'ObjectReferenced', 'Equator', 'BodyFixed', 'BodyInertial',
                                            'GSE', 'GSM', 'Topocentric', 'BodySpinSun'],
                                   'CentralBody': CelestialBodies(),
                                   'Origin': (CelestialBodies() + SpacecraftObjs() + LibrationPoints() + Barycenter()
                                              + GroundStations()),
                                   'AxesTypeSpecific': {
                                       'ObjectReferenced': {
                                           'Primary': (CelestialBodies() + SpacecraftObjs() + LibrationPoints() +
                                                       Barycenter() + GroundStations()),
                                           'Secondary': (CelestialBodies() + SpacecraftObjs() + LibrationPoints() +
                                                         Barycenter() + GroundStations()),
                                           'XAxis': ['R', 'V', 'N', '-R', '-V', '-N', None],
                                           'YAxis': ['R', 'V', 'N', '-R', '-V', '-N', None],
                                           'ZAxis': ['R', 'V', 'N', '-R', '-V', '-N', None],
                                       },
                                       'TOE': {
                                           'Epoch': '21545'
                                       },
                                       'MOE': {
                                           'Epoch': '21545'
                                       },
                                       'LocalAlignedConstrained': {
                                           'AlignmentVectorX': 1,
                                           'AlignmentVectorY': 0,
                                           'AlignmentVectorZ': 0,
                                           'ConstraintVectorX': 0,
                                           'ConstraintVectorY': 0,
                                           'ConstraintVectorZ': 1,
                                           'ConstraintReferenceVectorX': 0,
                                           'ConstraintReferenceVectorY': 0,
                                           'ConstraintReferenceVectorZ': 1,
                                           'ConstraintCoordinateSystem': 'EarthMJ2000Eq',
                                           'ReferenceObject': (CelestialBodies() + SpacecraftObjs() +
                                                               LibrationPoints() + Barycenter() +
                                                               GroundStations())
                                       }
                                   },
                                   }

            # Parse origin argument
            if origin not in self.allowed_values['Origin']:
                raise AttributeError(f'Specified origin "{origin}" is not recognized. Please specify one of the '
                                     f'following:\n\t{self.allowed_values["Origin"]}')
            else:
                self.origin = gmat.GetObject(origin)  # get current (default) origin
                # attach new origin to CoordinateSystem
                self.SetStringParameter(1, self.origin.GetName())  # 1 for ORIGIN_NAME, 2 for J2000_BODY_NAME
                self.SetRefObject(self.origin, gmat.SPACE_POINT, self.origin.GetName())

            # Parse axes argument
            if axes not in self.allowed_values['Axes']:
                raise AttributeError(f'Specified axes type "{axes}" is not recognized. Please specify one of the '
                                     f'following:\n\t{self.allowed_values["Axes"]}')
            else:
                if axes in list(self.allowed_values['AxesTypeSpecific'].keys()):
                    axes_specific_values = self.allowed_values['AxesTypeSpecific'][axes]

                    # TODO set params/ref objs for all axes types
                    if axes == 'ObjectReferenced':
                        self.primary = primary
                        self.secondary = secondary
                        self.xaxis = xaxis
                        self.yaxis = yaxis
                        self.zaxis = zaxis

                    elif (axes == 'TOE') or (axes == 'MOE'):
                        self.epoch = epoch

                    elif axes == 'LocalAlignedConstrained':
                        self.alignment_vec_x = alignment_vec_x
                        self.alignment_vec_y = alignment_vec_y
                        self.alignment_vec_z = alignment_vec_z
                        self.constraint_vec_x = constraint_vec_x
                        self.constraint_vec_y = constraint_vec_y
                        self.constraint_vec_z = constraint_vec_z
                        self.constraint_ref_vec_x = constraint_ref_vec_x
                        self.constraint_ref_vec_y = constraint_ref_vec_y
                        self.constraint_ref_vec_z = constraint_ref_vec_z
                        self.constraint_coord_sys = constraint_coord_sys
                        self.ref_object = ref_object

            self.axes: OrbitState.CoordinateSystem.Axes = OrbitState.CoordinateSystem.Axes(axes, f'{origin}_{axes}')
            self.SetRefObject(self.axes, gmat.AXIS_SYSTEM, self.axes.name)

            # gp.Initialize()
            self.Initialize()

        def __repr__(self):
            return f'A CoordinateSystem with origin {self.origin} and axes {self.axes}'

        @staticmethod
        def Construct(name: str, central_body: str, axes: str):
            print('In static Construct')
            return gmat.Construct('CoordinateSystem', name, central_body, axes)

        @classmethod
        def from_sat(cls, sc: gp.Spacecraft) -> OrbitState.CoordinateSystem:
            name = sc.gmat_obj.GetRefObjectName(gmat.COORDINATE_SYSTEM)
            sc_cs_gmat_obj = sc.gmat_obj.GetRefObject(gmat.COORDINATE_SYSTEM, name)
            origin = sc_cs_gmat_obj.GetField('Origin')
            axes = sc_cs_gmat_obj.GetField('Axes')
            coord_sys: OrbitState.CoordinateSystem = cls(name=name, origin=origin, axes=axes)
            return coord_sys

        @property
        def name(self) -> str:
            name = getattr(self, '_name', self.gmat_obj.GetName())
            return name

        @name.setter
        def name(self, name):
            self._name = name
            self.gmat_obj.SetName(name)

        def Help(self):
            return GmatObject.Help(self.gmat_obj)

    def __init__(self, **kwargs):
        self.allowed_state_elements = {
            'Cartesian': {'X', 'Y', 'Z', 'VX', 'VY', 'VZ'},
            'Keplerian': {'SMA', 'ECC', 'INC', 'RAAN', 'AOP', 'TA'},
            'ModifiedKeplerian': {'RadApo', 'RadPer', 'INC', 'RAAN', 'AOP', 'TA'},
            'SphericalAZFPA': {'RMAG', 'RA', 'DEC', 'VMAG', 'AZI', 'FPA'},
            'SphericalRADEC': {'RMAG', 'RA', 'DEC', 'VMAG', 'RAV', 'DECV'},
            'Equinoctial': {'SMA', 'EquinoctialH', 'EquinoctialK',
                            'EquinoctialP', 'EquinoctialQ', 'MLONG'},
            'ModifiedEquinoctial': {'SemilatusRectum', 'ModEquinoctialF', 'ModEquinoctialG',
                                    'ModEquinoctialH', 'ModEquinoctialH', 'TLONG'},
            'AlternativeEquinoctial': {'SMA', 'EquinoctialH', 'EquinoctialK',
                                       'AltEquinoctialP', 'AltEquinoctialQ', 'MLONG'},
            'Delaunay': {'Delaunayl', 'Delaunayg', 'Delaunayh', 'DelaunayL', 'DelaunayG', 'DelaunayH'},
            'OutgoingAsymptote': {'OutgoingRadPer', 'OutgoingC3Energy', 'OutgoingRHA',
                                  'OutgoingDHA', 'OutgoingBVAZI', 'TA'},
            'IncomingAsymptote': {'IncomingRadPer', 'IncomingC3Energy', 'IncomingRHA',
                                  'IncomingDHA', 'IncomingBVAZI', 'TA'},
            'BrouwerMeanShort': {'BrouwerShortSMA', 'BrouwerShortECC', 'BrouwerShortINC',
                                 'BrouwerShortRAAN', 'BrouwerShortAOP', 'BrouwerShortMA'},
            'BrouwerMeanLong': {'BrouwerLongSMA', 'BrouwerLongECC', 'BrouwerLongINC',
                                'BrouwerLongRAAN', 'BrouwerLongAOP', 'BrouwerLongMA'}
        }
        # TODO complete self._allowed_values - see pg 599 of GMAT User Guide (currently missing Planetodetic)
        self._allowed_values = {'display_state_type': list(self.allowed_state_elements.keys()),
                                # TODO: get names of any other user-defined coordinate systems and add to allowlist
                                'coord_sys': CoordSystems(),
                                # TODO: define valid state_type values - using display_state_type ones for now
                                'state_type': list(self.allowed_state_elements.keys()),
                                }

        # TODO complete this list
        self._gmat_fields = {'EpochFormat': {'A1ModJulian',
                                             'TAIModJulian',
                                             'UTCModJulian',
                                             'TDBModJulian',
                                             'TTModJulian',
                                             'A1Gregorian',
                                             'TAIGregorian',
                                             'UTCGregorian',
                                             'TDBGregorian',
                                             'TTGregorian'},
                             'Epoch': type(int),
                             # 'CoordinateSystem' will also include user-defined ones
                             'CoordinateSystem': {'EarthMJ2000Eq', 'EarthMJ2000Ec', 'EarthFixed', 'EarthICRF'},
                             'StateType': {},
                             'DisplayStateType': {}
                             }

        self._key_param_defaults = {'date_format': 'TAIModJulian', 'epoch': str(21545), 'coord_sys': 'EarthMJ2000Eq',
                                    'display_state_type': 'Cartesian', 'sc': None}

        fields_remaining: list[str] = list(self._key_param_defaults.keys())

        # use Cartesian as default StateType
        if 'display_state_type' not in kwargs:
            self._display_state_type = 'Cartesian'
        else:  # state_type is specified but may not be valid
            if kwargs['display_state_type'] not in list(self.allowed_state_elements.keys()):
                # invalid display_state_type was given
                raise SyntaxError(f'Invalid display_state_type parameter given: {kwargs["display_state_type"]}\n'
                                  f'Valid values are: {self.allowed_state_elements.keys()}')
            else:
                self._display_state_type = kwargs['display_state_type']
            fields_remaining.remove('display_state_type')

        # Set key parameters to value in kwargs, or None if not specified
        # TODO: add validity checking of other kwargs against DisplayStateType
        for param in fields_remaining:
            if param in kwargs:  # arguments must be without leading underscores
                setattr(self, f'_{param}', kwargs[param])
            else:
                setattr(self, f'_{param}', self._key_param_defaults[param])

    def apply_to_spacecraft(self, sc: gp.Spacecraft):
        """
        Apply the properties of this OrbitState to a spacecraft.

        :param sc:
        :return:
        """

        attrs_to_set = []
        # Find out which class attributes are set and apply all of them to the spacecraft
        instance_attrs = self.__dict__.copy()  # get a copy of the instance's current attributes

        # remove attributes that are just for internal class use and shouldn't be applied to a spacecraft
        for attr in ('allowed_state_elements', '_allowed_values', '_gmat_fields', '_key_param_defaults', '_sc'):
            instance_attrs.pop(attr)

        attrs_to_set.extend(list(instance_attrs))

        # extend attrs_to_set with the elements corresponding to the current state_type
        try:  # state_type is recognized
            elements_for_given_state_type = self.allowed_state_elements[self._display_state_type]
            attrs_to_set.extend(elements_for_given_state_type)
        except KeyError:  # state_type attribute invalid
            raise AttributeError(f'Invalid state_type set as attribute: {self._display_state_type}')

        for attr in attrs_to_set:
            try:
                # TODO bugfix: setting element e.g. ECC to 'Cartesian'
                # TODO bugfix: setting DisplayStateType to 'Cartesian'
                gmat_attr = py_str_to_gmat_str(attr)
                val = getattr(self, attr)
                if gmat_attr == 'CoordSys':
                    gmat_attr = 'CoordinateSystem'
                if val is not None:
                    if (gmat_attr == 'Epoch') and (not isinstance(val, str)):
                        val = str(val)
                    sc.SetField(gmat_attr, val)
                raise AttributeError
            except AttributeError:
                # print(f'No value set for attr {attr} - skipping')
                pass

    @classmethod
    def from_dict(cls, orbit_dict: dict, sc: gp.Spacecraft = None) -> OrbitState:
        o_s: OrbitState = cls()  # create OrbitState object, with sc set as None by default

        try:
            o_s._display_state_type = orbit_dict['DisplayStateType']  # get display_state_type from dict (required)
            orbit_dict.pop('DisplayStateType')  # remove DisplayStateType so we don't try setting it again later
        except KeyError:
            try:  # maybe the user used the old name, StateType, instead of DisplayStateType
                o_s._display_state_type = orbit_dict['StateType']
                orbit_dict.pop('StateType')  # remove StateType so we don't try setting it again later
            except KeyError:
                raise KeyError(f"Required parameter 'DisplayStateType' was not found in OrbitState.from_dict")

        o_s._allowed_values['coord_sys'] = CoordSystems()

        # TODO parse orbit params in orbit_dict

        for attr in orbit_dict:  # initialize other key attrs to None
            if attr[0].islower():
                raise SyntaxError(f'Invalid attribute found - {attr}. Must be in GMAT string format')
            setattr(o_s, gmat_str_to_py_str(attr, True), orbit_dict[attr])

        return o_s
