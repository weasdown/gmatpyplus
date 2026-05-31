from physical_model import PhysicalModel


class PointMassForce(PhysicalModel):
    # An object representing the point mass force for a single celestial body

    # fields: ['Covariance', 'Epoch', 'ElapsedSeconds', 'BodyName', 'DerivativeID', 'GravConst', 'Radius',
    # 'EstimateMethod', 'PrimaryBody']
    def __init__(self, name: str = 'PMF', body: str | None = None):
        super().__init__('PointMassForce', name)
        if body:
            self.primary_body = body
        else:
            self.primary_body = 'Earth'
        self.SetField('BodyName', str(body))
