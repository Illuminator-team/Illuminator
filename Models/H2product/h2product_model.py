class h2product_python():

    def __init__(self, houses):
        self.production = 0
        self.num = houses

    def generation(self, h2product):
        self.production = self.num * h2product  # m^3/min

        re_params = {'h2product_gen': self.production}
        return re_params
