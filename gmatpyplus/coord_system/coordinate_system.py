from gmatpyplus import gmat
from gmatpyplus.coord_system.axes import Axes
from gmatpyplus.foundation import GmatObject
from gmatpyplus.spacecraft import Spacecraft
from gmatpyplus.utils import Barycenter, CelestialBodies, GroundStations, LibrationPoints, SpacecraftObjs


# TODO add CoordinateBase class in a separate file and make it CoordinateSystem's parent type (see CoordinateBase.cpp in GMAT source code).
class CoordinateSystem(GmatObject):
    # TODO convert __init__ params to args with default values
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
        self._allowed_values = {'Axes': ['MJ2000Eq', 'MJ2000Ec', 'ICRF',
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
        if origin not in self._allowed_values['Origin']:
            raise AttributeError(f'Specified origin "{origin}" is not recognized. Please specify one of the '
                                 f'following:\n\t{self._allowed_values["Origin"]}')
        else:
            self.origin = gmat.GetObject(origin)  # get current (default) origin
            # attach new origin to CoordinateSystem
            self.SetStringParameter(1, self.origin.GetName())  # 1 for ORIGIN_NAME, 2 for J2000_BODY_NAME
            self.SetRefObject(self.origin, gmat.SPACE_POINT, self.origin.GetName())

        # Parse axes argument
        if axes not in self._allowed_values['Axes']:
            raise AttributeError(f'Specified axes type "{axes}" is not recognized. Please specify one of the '
                                 f'following:\n\t{self._allowed_values["Axes"]}')
        else:
            if axes in list(self._allowed_values['AxesTypeSpecific'].keys()):
                axes_specific_values = self._allowed_values['AxesTypeSpecific'][axes]

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

        self.axes: Axes = Axes(axes, f'{origin}_{axes}')
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
    def from_sat(cls, sc: Spacecraft) -> CoordinateSystem:
        name = sc.gmat_obj.GetRefObjectName(gmat.COORDINATE_SYSTEM)
        sc_cs_gmat_obj = sc.gmat_obj.GetRefObject(gmat.COORDINATE_SYSTEM, name)
        origin = sc_cs_gmat_obj.GetField('Origin')
        axes = sc_cs_gmat_obj.GetField('Axes')
        coord_sys: CoordinateSystem = cls(name=name, origin=origin, axes=axes)
        return coord_sys

    @property
    def name(self) -> str:
        return self._name if self._name else self.gmat_obj.GetName()

    @name.setter
    def name(self, name):
        self._name = name
        self.gmat_obj.SetName(name)
