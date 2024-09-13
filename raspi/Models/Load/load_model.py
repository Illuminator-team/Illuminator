class load_python():

    def __init__(self, houses, output_type):
        self.consumption = 0
        self.houses = houses
        self.output_type = output_type

    def demand(self, load):
        # incoming load is in kWh at every 15 min interval
        # incoming value of load is in kWh

        if self.output_type == 'energy':
            self.consumption = (self.houses * load) # kWh
        elif self.output_type == 'power':
            self.consumption = (self.houses * load)/4  # kWh

        re_params = {'load_dem': self.consumption}
        return re_params
