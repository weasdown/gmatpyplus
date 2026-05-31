from basics import GmatObject
from force_model.physical_model import PhysicalModel
from solar_system import AtmosphereModel
from utils import *


class ForceModel(GmatObject):
    def __init__(self, name: str = 'DefaultProp_ForceModel', central_body: str = 'Earth',
                 primary_body: str = None, polyhedral_bodies: list = None, gravity_field: GravityField = None,
                 point_masses: str | list[str] | PointMassForce = None, drag: DragForce = None,
                 srp: bool | SolarRadiationPressure = False, relativistic_correction: bool = False,
                 error_control: list = None, user_defined: list[str] = None):
        super().__init__('ForceModel', name)

        def validate_point_masses(pm) -> list[ForceModel.PointMassForce]:
            celestial_bodies = CelestialBodies()

            # point_masses is a single string
            if isinstance(point_masses, str):
                # point mass for a body cannot be set if that body is already in an attached GravityField
                if self.gravity and (self.central_body in point_masses):
                    raise SyntaxError(f'Point mass for {self.central_body} cannot be used because '
                                      f'{self.central_body} is already set as the central body')

                return [ForceModel.PointMassForce(body=point_masses)]

            # point_masses is a single PointMassForce
            elif isinstance(point_masses, ForceModel.PointMassForce):
                if self.gravity and (self.central_body in point_masses.primary_body):
                    raise SyntaxError(f'Point mass for {self.central_body} cannot be used because a GravityField '
                                      f'containing {self.central_body} is already set')
                return [point_masses]

            # point_masses is a list (presumably of celestial body strings)
            elif isinstance(point_masses, list):
                if not all(isinstance(f, str) for f in point_masses):
                    raise TypeError('If point_masses is a list, its items must be strings of celestial body names')

                if not all([f in celestial_bodies for f in point_masses]):
                    raise SyntaxError(f'Not all strings in point_masses are valid celestial body names')

                if self.gravity and (any(f in self.central_body for f in point_masses)):
                    # FIXME: breaks Tut04 DeepSpace FM
                    # TODO don't assume Earth
                    raise SyntaxError(f'Point mass for {self.central_body} cannot be used because '
                                      f'{self.central_body} is already set as the central body')

                # point_masses is a valid list of celestial body name strings
                pmf_list = []
                for body in point_masses:
                    pmf_list.append(ForceModel.PointMassForce(name=f'PointMassForce_{body}', body=body))
                return pmf_list

            else:  # point_masses is not of a valid type
                raise SyntaxError('point_masses must be a single string, list of strings, or a single PointMassForce')

        # TODO define allowed values (different to defaults)
        self._allowed_values = {'arg': 'value'}
        defaults = {'error_control': ['RSSStep'], 'point_masses': ['Earth'], 'primary_bodies': []}

        self.central_body = self.GetField('CentralBody')
        if central_body is not None:
            self.central_body = central_body
            self.SetStringParameter('CentralBody', self.central_body)

        self.gravity = gravity_field

        # TODO replace below with creation of GravityFields
        #  PrimaryBodies is alias for GravityFields as per page 162 of GMAT Architectucral Specification
        # self.gravity = None
        # if primary_bodies is not None:
        #     if isinstance(primary_bodies, str):
        #         primary_bodies = [primary_bodies]
        #     self.primary_bodies = primary_bodies
        #
        #     primary_bodies_objs = [gmat.Planet(body_name) for body_name in self.primary_bodies]
        #     for body_obj in primary_bodies_objs:
        #         prim_bod_param_id = self.GetParameterID("PrimaryBodies")
        #         print(f'PrimaryBodies param: ID {prim_bod_param_id}, type: {self.GetParameterTypeString(prim_bod_param_id)}')
        #         print(f'body_obj type: {body_obj.GetTypeName()}, IsOfType CelestialBody: {body_obj.IsOfType("CelestialBody")}')
        #         # grav_fields = [self.GravityField()]
        #         self.SetStringParameter(3, body_obj.GetName())  # 3 for BODY_NAME
        #         self.SetRefObject(body_obj, gmat.CELESTIAL_BODY, body_obj.GetName())
        #     # self.Help()
        #     # self.SetField('PrimaryBodies', self.primary_bodies)
        #     # self._primary_bodies = primary_bodies if primary_bodies else self.central_body
        #     self.Initialize()
        #     self.Help()

        # TODO don't setup gravity field if none specified - breaks interplanetary where grav field irrelevant
        self.primary_body: str = primary_body
        if self.primary_body is None:  # self.primary_body is None
            self.gravity = gravity_field
            if gravity_field is not None:
                if isinstance(gravity_field, ForceModel.GravityField):
                    self.gravity: ForceModel.GravityField = gravity_field
                else:
                    raise TypeError(f'gravity_field type not recognized - {type(gravity_field).__name__}.'
                                    f' Must be None or a gp.ForceModel.GravityField')
            else:  # gravity_field and self.primary_body are both None - use default
                # TODO: are there cases where we wouldn't want a PrimaryBody or GravityField?
                self.primary_body = 'Earth'
                self.gravity = self.GravityField()  # create default (Earth-based) GravityField

        else:  # self.primary_body is not None
            if self.gravity is not None and (self.primary_body != self.gravity.body):
                raise AttributeError(
                    f'If a primary_body and gravity_field are both specified, the primary_body must be '
                    f'equal to the gravity_field\'s body. Specified primary_body and gravity_field: '
                    f'{self.primary_body} and {self.gravity.body}')

            allowed_primaries = gp.utils.CelestialBodies()
            if self.primary_body not in allowed_primaries:
                raise AttributeError(f'Specified primary_body "{self.primary_body}" is not recognized. Please use one '
                                     f'of the following:\n{allowed_primaries}')

        if self.gravity is not None:
            self.AddForce(self.gravity)  # add the GravityField to the ForceModel within GMAT

        self._polyhedral_bodies = polyhedral_bodies

        self.point_mass_forces: list[ForceModel.PointMassForce] | None = None
        if point_masses is not None:
            self.point_mass_forces = validate_point_masses(point_masses)  # raises exception if point_masses invalid
            for force in self.point_mass_forces:
                self.AddForce(force)

        # if just srp=True, create and use a default srp object
        if not srp:
            self.srp = None
        elif isinstance(srp, ForceModel.SolarRadiationPressure):
            self.srp = srp
            self.AddForce(self.srp)
        else:
            self.srp = ForceModel.SolarRadiationPressure(fm=self)
            self.AddForce(self.srp)

        if not drag:
            self.drag = False
        elif isinstance(drag, ForceModel.DragForce):
            self.drag = drag
            self.AddForce(self.drag)
        else:
            self.drag = ForceModel.DragForce(fm=self)  # create and use a default drag model
            self.AddForce(self.drag)

        # Add other effects
        self.relativistic_correction = relativistic_correction
        self.error_control = error_control
        self.user_defined = user_defined

        # for attr in self._allowed_values:  # TODO check supplied args are allowed
        #     # use supplied value. If not given (None), use default
        #     setattr(self, f'_{attr}', defaults[attr]) if attr is None else attr
        #
        # # TODO option 1: refer to OrbitState for how to tidily define defaults - implement here
        # # TODO option 2: implement below method of default setting in other classes
        # for attr in defaults:
        #     setattr(self, f'_{attr}', defaults[attr]) if attr is None else attr

        # check_valid_args(primary_bodies=primary_bodies)

        gp.Initialize()
        self.Initialize()

    def __repr__(self):
        return f'ForceModel with name {self.name}'

    def AddForce(self, force: PhysicalModel):
        # Nothing returned from GMAT so no return from this method
        gp.extract_gmat_obj(self).AddForce(gp.extract_gmat_obj(force))

    class PrimaryBody:
        # TODO complete arguments
        # TODO: use fact that PrimaryBody is alias for GravityField - in init call GravityField.__init__
        def __init__(self, fm: ForceModel, body: str = 'Earth',
                     gravity: ForceModel.GravityField = None,
                     drag: ForceModel.DragForce | bool = False):
            self._force_model = fm
            self._body = body if body else self._force_model.central_body
            self._gravity = gravity if gravity else ForceModel.GravityField()
            self._drag = drag if drag else ForceModel.DragForce(self._force_model)

    class DragForce(PhysicalModel):
        def __init__(self, fm: ForceModel = None, name: str = 'DragForce', atmo_model: str = 'JacchiaRoberts',
                     drag_model: str = 'Spherical', f107: int = 150, f107a: int = 150, magnetic_index: int = 3,
                     historic_weather_source: str = 'ConstantFluxAndGeoMag',
                     predicted_weather_source: str = 'ConstantFluxAndGeoMag',
                     cssi_space_weather_file: str = 'SpaceWeather-All-v1.2.txt',
                     schatten_file: str = 'SchattenPredict.txt', schatten_error_model: str = 'Nominal',
                     schatten_timing_model: str = 'NominalCycle',
                     density_model='Only used if atmo_model is MarsGRAM2005', input_file=None):
            # TODO remove unused args once moved to AtmosphereModel()

            super().__init__('DragForce', name)

            self.primary_body: str = fm.central_body if fm else 'Earth'
            # TODO: move to AtmosphereModel as appropriate
            self.allowed_values = {'models': {'Earth': ['JacchiaRoberts', 'MSISE86', 'MSISE90', 'NRLMSISE00'],
                                              'Mars': 'MarsGRAM2005'},
                                   'drag_model': ['Spherical', 'SPADFile'],
                                   'historic_weather_source': ['ConstantFluxAndGeoMag', 'CSSISpaceWeatherFile'],
                                   'predicted_weather_source': 'SchattenFile',
                                   'schatten_error_model': ['Nominal', 'PlusTwoSigma', 'MinusTwoSigma'],
                                   'schatten_timing_model': ['NominalCycle', 'EarlyCycle', 'LateCycle'],
                                   'density_model': ['High', 'Mean', 'Low']}
            allowed_models = self.allowed_values['models'][self.primary_body]
            if atmo_model not in allowed_models:
                raise AttributeError(f'model parameter must be one of the following: {allowed_models}')
            else:
                self.atmosphere_model = AtmosphereModel(atmo_model=atmo_model)
                self.SetReference(self.atmosphere_model)
                self.SetField('AtmosphereModel', self.atmosphere_model.atmo_model)

            if self.atmosphere_model == 'MarsGRAM2005':
                if density_model != 'Only used if atmo_model is MarsGRAM2005':
                    if density_model in self.allowed_values['density_model']:
                        self.density_model = density_model
                    else:
                        raise AttributeError('density_model must be "High", "Mean" or "Low" (default is "Mean")')
                else:
                    self.density_model = 'Mean'  # default density model
                self.SetField('DensityModel', self.density_model)

                self.input_file = input_file
                self.SetField('InputFile', self.input_file)
            elif self.atmosphere_model:
                self.density_model = None
                self.input_file = None
                self.drag_model = drag_model
                self.f107 = f107
                self.f107a = f107a
                self.magnetic_index = magnetic_index
            else:  # these four fields must not be used if no atmosphere model is specified
                self.drag_model = None
                self.f107 = None
                self.f107a = None
                self.magnetic_index = None

            if not fm:
                self.force_model = None
            else:
                self.force_model = fm
                self.force_model.AddForce(self)

    class FiniteThrust(PhysicalModel):
        def __init__(self, name: str = 'FiniteThrust'):
            super().__init__('FiniteThrust', name)
            raise NotImplementedError

    class Harmonic:
        def __init__(self):
            raise NotImplementedError

    class HarmonicGravity(Harmonic):
        def __init__(self):
            super().__init__()
            raise NotImplementedError

    class HarmonicField(PhysicalModel):
        def __init__(self):
            super().__init__('HarmonicField', 'HarmonicField')
            raise NotImplementedError

    class GravityField(PhysicalModel):
        # TODO change parent class back to HarmonicField if appropriate
        def __init__(self, name: str = None, body: str = 'Earth', model: str = 'JGM-2', degree: int = 4,
                     order: int = 4, stm_limit: int = 100, gravity_file: str = 'JGM2.cof', tide_file: str = None,
                     tide_model: str = None):
            if name is None:
                name = f'GravField_{body}_{model}_{degree}_{order}'
            super().__init__('GravityField', name)

            self.body = body
            self.SetStringParameter(3, self.body)  # 3 for BODY_NAME

            allowed_models = {'Sun': [None, 'Other'], 'Venus': [None, 'MGNP-180U', 'Other'],
                              'Earth': [None, 'JGM-2', 'JGM-3', 'EGM-96', 'Other'], 'Mars': [None, 'Mars-50C', 'Other'],
                              'Jupiter': [None, 'Other'], 'Saturn': [None, 'Other'], 'Uranus': [None, 'Other'],
                              'Neptune': [None, 'Other'], 'Pluto': [None, 'Other'], 'Luna': [None, 'LP-165', 'Other']}
            # check whether the specified model is defined for the specified body
            self.model = model
            if self.model is not None:
                if model == 'Other':
                    # TODO: add support for 'Other' model option (user would pass a path to a model file)
                    raise NotImplementedError
                elif model not in allowed_models[self.body]:
                    raise AttributeError(f'Specified model "{self.model}" is not recognized for body "{self.body}". '
                                         f'Valid models for that body are:\n\t{allowed_models[self.body]}')

            self.degree = degree
            self.SetIntegerParameter('Degree', int(self.degree))

            self.order = order
            self.SetIntegerParameter('Order', self.order)

            # self.gmat_obj = gmat.GravityField(self.name, self.body, self.degree, self.order)
            # self.gp_obj = gp.GmatObject.from_gmat_obj(self.gmat_obj)

            self.stm_limit = stm_limit
            self.SetIntegerParameter('StmLimit', self.stm_limit)

            self.gravity_file = gravity_file
            self.SetStringParameter('PotentialFile', self.gravity_file)

            self.tide_file = tide_file
            if self.tide_file:
                self.SetStringParameter('TideFile', self.tide_file)

            if tide_model:
                if tide_model not in [None, 'Solid', 'SolidAndPole']:
                    raise SyntaxError('Invalid tide_model given - must be None, "Solid" or "SolidAndPole"')
                else:
                    self._tide_model = tide_model
                    self.SetStringParameter('TideModel', self._tide_model)

    class ODEModel(PhysicalModel):
        def __init__(self, name: str):
            super().__init__('ODEModel', name)
            raise NotImplementedError

    class PointMassForce(PhysicalModel):
        # An object representing the point mass force for a single celestial body

        # fields: ['Covariance', 'Epoch', 'ElapsedSeconds', 'BodyName', 'DerivativeID', 'GravConst', 'Radius',
        # 'EstimateMethod', 'PrimaryBody']
        def __init__(self, name: str = 'PMF', body: str = None):
            super().__init__('PointMassForce', name)
            if body:
                self.primary_body = body
            else:
                self.primary_body = 'Earth'
            self.SetField('BodyName', body)

    class SolarRadiationPressure(PhysicalModel):
        def __init__(self, fm: ForceModel = None, name: str = 'SRP', model: str = 'Spherical', flux: float | int = 1367,
                     nominal_sun: float | int = 149597870.691):
            super().__init__('SolarRadiationPressure', name)

            if model in ['Spherical', 'SPADFile', 'NPlate']:
                self.model = model
            else:
                raise AttributeError('Invalid model given for SolarRadiationPressure. Must be "Spherical", "SPADFile"'
                                     ' or "NPlate')
            if 1200 < flux < 1450:
                self.flux = flux
            else:
                raise AttributeError('flux argument must be between 1200 and 1450 (default is 1367)')

            if 135e6 < nominal_sun < 165e6:
                self.nominal_sun = nominal_sun
            else:
                raise AttributeError('nominal_sun argument must be between 135e6 and 165e6 (default is 149597870.691)')

            self.force_model = fm
            if self.force_model:
                self.force_model.AddForce(self)
