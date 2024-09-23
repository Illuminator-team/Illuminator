class h2demand_python:

    def __init__(self, houses ):
        self.consumption = 0
        self.houses = houses

    def demand(self, h2demand):


        self.consumption = (self.houses * h2demand) #m^3/min

        re_params = {'h2demand_dem': self.consumption}
        return re_params
