class electrolyser_python:
    def __init__(self, eff, fc_eff, resolution):
        self.p_in = None
        self.h_out = None
        self.eff = eff
        self.fc_eff = fc_eff
        self.resolution = resolution

    def electrolyser(self, flow2e):

        # self.p_in = p_ask_e
        # self.p_out = self.p_in * self.eff
        # re_params = {'elec_gen': self.p_out}
        # return re_params
        if flow2e > 0:
            self.p_in = flow2e  # in kW
            conversion = self.p_in * self.resolution * 60  # kJ  # since we are gentting power for 15mins, hence we conver kW to kJ by multiplying with 15mins * 60 seconds in a minute
            hhv = 286.6  # kJ/mol
            mole = conversion / hhv * self.eff  # gives number of moles of hydrogen
            out = 2.02 * mole  # weight of hydrogen is 2.02 grams/mole
            self.h_out = out / 1000  # kg of hydrogen produced
            re_params = {'h2_gen': self.h_out}  #, 'h2_out': 0}
        # elif flow2e < 0:
        #     q = 39.4  # kW/Kg  # this is the amount of power that can be generated from 1 kg of Hydrogen or kWh of energy in 1 hour from 1 kg hydrogen. The power remains constant for a period of 1hr
        #
        #     self.h_out = (flow2e / q) / self.fc_eff  # Kg
        #
        #     re_params = {'h2_out': self.h_out, 'h2_gen': 0}
        else:
            self.h_out = 0
            re_params = {'h2_gen': self.h_out}  #, 'h2_out': 0}

        return re_params
