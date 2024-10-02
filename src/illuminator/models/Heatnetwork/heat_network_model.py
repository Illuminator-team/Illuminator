import pandas as pd


class heat_network_python:
    def __init__(self, max_temperature, insulation, ext_temp, therm_cond, length, diameter,
                 density, c):
        self.max_temperature = max_temperature
        self.insulation = insulation
        self.ext_temp = ext_temp
        self.t_int = ext_temp
        self.therm_cond = therm_cond
        self.length = length
        self.diameter = diameter
        self.density = density
        self.c = c
        self.congestion = False
        self.q_in = 0
        self.q_out = 0

    def heatnetwork(self, q_in, q_out):
        self.q_in = q_in
        self.q_out = q_out
        q_tot = sum(q_in) - sum(q_out)
        self.t_int = self.t_int + q_tot*15*60/(self.density * self.length * self.diameter * self.c)
        q_loss = (self.therm_cond / self.insulation) * self.diameter * self.length * (self.t_int - self.ext_temp)
        if self.t_int > self.max_temperature:
            self.congestion = True
        else:
            self.congestion = False

        re_params = {'t_int': self.t_int, 'q_in': self.q_in, 'q_out': self.q_out, 'q_loss': q_loss,
                     'congestion': self.congestion}
        return re_params
