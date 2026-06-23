import gmatpyplus as gp
from gmatpyplus.foundation import GmatObject


class Propagator(GmatObject):  # variable called gator in GMAT Python examples
    # Labelled in GMAT GUI as "Integrator"
    def __init__(self, integrator: str = 'PrinceDormand78', name: str = 'Prop', **kwargs):
        # TODO: change **kwargs to proper parsing here (for usability)
        # TODO: add parsing of rest of arguments (see defaults in User Guide)
        integrator_allowed_types = ['RungeKutta89', 'PrinceDormand78', 'PrinceDormand45', 'RungeKutta68',
                                    'RungeKutta56', 'AdamsBashforthMoulton', 'SPK', 'Code500', 'STK', 'CCSDS-OEM'
                                                                                                      'PrinceDormand853',
                                    'RungeKutta4', 'SPICESGP4']
        if integrator in integrator_allowed_types:
            self.integrator = integrator
        else:
            raise AttributeError(f'integrator must be one of the following: {integrator_allowed_types}')

        if name == 'Prop':
            name = f'{name}_{integrator}'

        super().__init__(integrator, name)

        gp.Initialize()
        # self.Initialize()
