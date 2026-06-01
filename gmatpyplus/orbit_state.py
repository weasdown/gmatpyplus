from __future__ import annotations

import gmatpyplus as gp
from utils import CoordSystems, gmat_str_to_py_str, py_str_to_gmat_str


class OrbitState:
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
