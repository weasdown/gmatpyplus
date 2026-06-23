import logging

from gmatpyplus.foundation import GmatObject


class AtmosphereModel(GmatObject):
    def __init__(self, name: str = 'AtmoModel', atmo_model: str = 'JacchiaRoberts', f107: int = 150,
                 f107a: int = 150,
                 magnetic_index=3, cssi_space_weather_file='SpaceWeather-All-v1.2.txt',
                 schatten_file='SchattenPredict.txt'):

        self.atmo_model = str(atmo_model)
        self.allowed_models = ['JacchiaRoberts', 'MSISE86', 'MSISE90', 'NRLMSISE00', 'MarsGRAM2005']
        if self.atmo_model not in self.allowed_models:
            raise AttributeError(f'model parameter must be one of the following: {self.allowed_models}')

        super().__init__(atmo_model, name)

        if (not isinstance(f107, (int, float))) or (f107 < 0):
            raise TypeError('f107 must be an integer or float greater than 0')
        else:
            if (f107 > 400) or (f107 < 50):
                logging.warning('Realistic values of f107 are between 50 and 400 inclusive')
            self.f107 = f107
            self.SetField('F107', self.f107)

        if (not isinstance(f107a, (int, float))) or (f107a < 0):
            raise TypeError('f107a must be an integer or float greater than 0')
        else:
            if (f107 > 400) or (f107 < 50):
                logging.warning('Realistic values of f107a are between 50 and 400 inclusive')
            self.f107a = f107a
            self.SetField('F107A', self.f107a)

        if (not isinstance(magnetic_index, (int, float))) or (magnetic_index < 0) or (magnetic_index > 9):
            raise TypeError('magnetic_index must be an integer or float between 0 and 9 inclusive')
        else:
            self.magnetic_index = magnetic_index
            self.SetField('MagneticIndex', self.magnetic_index)

        if cssi_space_weather_file:
            self.cssi_space_weather_file = cssi_space_weather_file
            self.SetField('CSSISpaceWeatherFile', self.cssi_space_weather_file)
        else:
            self.cssi_space_weather_file = None

        if schatten_file:
            self.schatten_file = schatten_file
            self.SetField('SchattenFile', self.schatten_file)
        else:
            self.schatten_file = None

        # # TODO: complete merging these fields into AtmosphereModel() (from Drag())
        # self.historic_weather_source = historic_weather_source
        # self.SetField('HistoricWeatherSource', self.historic_weather_source)
        #
        # self.predicted_weather_source = predicted_weather_source
        # self.SetField('PredictedWeatherSource', self.predicted_weather_source)
        #
        # self.cssi_space_weather_file = cssi_space_weather_file
        # self.SetField('CSSISpaceWeatherFile', self.cssi_space_weather_file)
        #
        # self.schatten_file = schatten_file
        # self.SetField('SchattenFile', self.schatten_file)
        #
        # self.schatten_error_model = schatten_error_model
        # self.SetField('SchattenErrorModel', self.schatten_error_model)
        #
        # self.schatten_timing_model = schatten_timing_model
        # self.SetField('SchattenTimingModel', self.schatten_timing_model)

# class ExponentialAtmosphere(AtmosphereModel):
#     def __init__(self):
#         super().__init__()
#         raise NotImplementedError
#
#
# class SimpleExponentialAtmosphere(AtmosphereModel):
#     def __init__(self):
#         super().__init__()
#         raise NotImplementedError
