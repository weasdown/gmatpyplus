from force_model.force_model import ForceModel
from force_model.physical_model import PhysicalModel
from solar_system.atmosphere_model import AtmosphereModel


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
