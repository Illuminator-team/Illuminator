
class fuelcell_python:
    def __init__(self, eff):
        self.p_in = None
        self.p_out = None
        self.eff = eff

    def output(self, h2_consume):
        # hydrogen input will be in Kg. Output will be electricity using the HHv value of hydrogen
        energy = 39.4  # kWh generated from 1 Kg hydrogen in 1 hour
        power = 39.4/60  # kW
        out = (-h2_consume*power*self.eff*15)  #KWh generated from fuelcell taking into consideration its efficiency
        re_params = {'fc_gen': out}
        return re_params
