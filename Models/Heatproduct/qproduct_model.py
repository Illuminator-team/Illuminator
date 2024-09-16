class qproduct_python():

    def __init__(self, utilities):
        self.production = 0
        self.utilities = utilities

    def generation(self, qproduct):
        self.production = self.utilities * qproduct  # m^3/min

        re_params = {'qproduct_gen': self.production}
        return re_params
