class electrolyser_python:
    def __init__(self, eff,  resolution, term_eff, rated_power, ramp_rate):
        self.p_in = None
        self.h_out = None
        self.eff = eff
        self.resolution = resolution
        self.term_eff = term_eff
        self.rated_power = rated_power
        self.ramp_rate = ramp_rate
        self.p_in_last = 0  # power input during the last step


    def ramp_rate_limit(self, desired_power):
        # Limit the change in power based on the ramp rate
        power_change = desired_power - self.p_in_last
        if abs(power_change) > self.ramp_rate:
            desired_power = self.p_in_last + self.resolution * self.ramp_rate
        return desired_power

    def electrolyser(self, flow2e, temperature=15, pressure=100):
        q_product=0
        desired_power = min(self.rated_power, flow2e)
        e_consume = self.ramp_rate_limit(desired_power)
        if e_consume > 0:

            q_product = e_consume * self.term_eff
            conversion = e_consume * self.resolution * 60  # kJ
            hhv = 286.6  # kJ/mol
            mole = conversion / hhv * self.eff  # gives number of moles of hydrogen
            out = 2.02 * mole  # weight of hydrogen is 2.02 grams/mole
            h_mass = out / 1000  # kg of hydrogen produced in 15 min
            self.h_out = h_mass * 11.2 / self.resolution  # m^3/min at NTP
            re_params = {'h2_gen': self.h_out, 'flow2e': flow2e, 'q_product': q_product, 'e_consume': e_consume}
        else:
            self.h_out = 0
            re_params = {'h2_gen': self.h_out, 'flow2e': flow2e, 'q_product': q_product, 'e_consume': e_consume}
        return re_params
