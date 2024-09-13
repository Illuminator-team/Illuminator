# compressed hydrogen storage tank at 700bar and storing about 100kg of hydrogen

class hydrogenstorage_python:
    def __init__(self, initial_set, h2_set):
        self.h2storage_soc = initial_set['initial_soc']
        self.h2storage_soc_min = h2_set['h2storage_soc_min']  # an attribute
        self.h2storage_soc_max = h2_set['h2storage_soc_max']  # an attribute
        self.p_in = None
        self.p_out = None
        self.eff = 0.94  # approx efficiency of compressed hydrogen storage tanks. Roundtrip efficiency
        self.max_h2 = h2_set['max_h2']
        self.min_h2 = h2_set['min_h2']
        self.capacity=h2_set['capacity']

    def charge_h2(self, h2_in):

        h2_flow = min(self.max_h2, h2_in)  # kWh
        if (h2_flow > 0) and (self.flag != 1):
            self.h2discharge = h2_flow * self.eff  # (+ve)  We multiply it with efficiency because while charging we are not 100% efficient, so we should end up with less energy than incoming
            h2_capacity = ((self.h2storage_soc_max - self.h2storage_soc) / 100) * self.capacity  # gives amount of energy that can be stored in the battery
            if self.h2storage_soc >= self.h2storage_soc_max:
                self.flag = 1
                self.h2out = 0
            else:
                if self.h2discharge <= h2_capacity:
                    h2_consumed = self.h2discharge
                    self.h2storage_soc = self.h2storage_soc + (self.h2discharge / self.capacity * 100)
                    # self.powerout = 0  # because we are consuming the incoming energy and nothing is going out
                    self.flag = 0  # Set flag as ready to discharge or charge
                    output_show = h2_flow  # just for showing purpose that what ever is extra is being consumed while internally, a bit less is used to charge battery because of losses

                else:  # Fully-charge Case
                    h2_consumed = h2_capacity / self.eff  # because to reach full soc, it needs more energy considering the losses. Since now we have the option to draw in more energy because it is surplus, we can do this, I think
                    h2_excess = self.h2discharge - h2_consumed
                    output_show = h2_consumed
                    # self.powerout = 0
                    # warn('\n Home Battery is fully discharged!! Cannot deliver more energy!')
                    self.h2storage_soc = self.h2storage_soc_max
                    self.flag = 1  # Set flag as 1 to show fully discharged state
        elif (h2_flow == 0) and (self.flag == 1):
            output_show = 0
        self.h2storage_soc = round(self.h2storage_soc, 3)
        re_params = {
                     # 'p_out': self.powerout,
                     'h2_stored': output_show,
                     'h2_given': 0,
                     'h2storage_soc_min': self.h2storage_soc_min,
                     'h2storagesoc_max': self.h2storage_soc_max,
                     # 'energy_drain': 0,
                     'h2_soc': self.h2storage_soc,
                     'mod': 1,
                     'flag': self.flag}

        return re_params

    def discharge_h2(self, h2_out):
        h2_flow = max(self.min_h2, h2_out)  # kWh
        if (h2_flow < 0) and (self.flag != -1):
            self.h2discharge = h2_flow / self.eff  # (+ve)  We multiply it with efficiency because while charging we are not 100% efficient, so we should end up with less energy than incoming
            h2_capacity = ((self.h2storage_soc_min - self.h2storage_soc) / 100) * self.capacity  # gives amount of energy that can be stored in the battery
            if self.h2storage_soc <= self.h2storage_soc_min:
                self.flag = -1
                self.h2out = 0
            else:
                if self.h2discharge > h2_capacity:
                    h2_given = self.h2discharge
                    self.h2storage_soc = self.h2storage_soc + (self.h2discharge / self.capacity * 100)
                    # self.powerout = 0  # because we are consuming the incoming energy and nothing is going out
                    self.flag = 0  # Set flag as ready to discharge or charge
                    output_show = h2_flow  # just for showing purpose that what ever is extra is being consumed while internally, a bit less is used to charge battery because of losses

                else:  # Fully-discharge Case
                    h2_given = h2_capacity * self.eff
                    h2_excess = self.h2discharge - h2_given
                    output_show = h2_given
                    # self.powerout = 0
                    # warn('\n Home Battery is fully discharged!! Cannot deliver more energy!')
                    self.h2storage_soc = self.h2storage_soc_min
                    self.flag = -1  # Set flag as 1 to show fully discharged state
        else:
            output_show = 0
        self.h2storage_soc = round(self.h2storage_soc, 3)
        re_params = {
            # 'p_out': self.powerout,
            'h2_stored': 0,
            'h2_given': output_show,
            'h2storage_soc_min': self.h2storage_soc_min,
            'h2storage_soc_max': self.h2storage_soc_max,
            # 'energy_drain': 0,
            'h2_soc': self.h2storage_soc,
            'mod': 1,
            'flag': self.flag}

        return re_params

    def output_h2(self, h2_in, h2_out, soc):  # charging power: positive; discharging power:negative
        self.h2storage_soc = soc  # here we assign the value of soc we provide to the attribute self.soc
        data_ret = {}
        # {'p_out',
        # 'soc',
        # 'mod',  # 0 = noaction,1 = charge,-1=discharge
        # 'flag',} # 1 means full charge, -1 means full discharge, 0 means available for control
        # conditions start:
        if h2_in == 0 and h2_out == 0:  # i.e when there isn't a demand of power at all,

            # soc can never exceed the limit so when it is equal to the max, we tell it is completely charged
            if self.h2storage_soc >= self.h2storage_soc_max:
                self.flag = 1  # meaning battery object we created is fully charged

            # soc can never exceed the limit so when it is equal to the min, we tell it is completely discharged
            elif self.h2storage_soc <= self.h2storage_soc_min:
                self.flag = -1

            # if the soc is between the min and max values, it is ready to be discharged or charged as per the situation
            else:
                self.flag = 0  # meaning it is available to operate.

            # here we are sending the current state of the battery
            re_params = {
                         # 'h2_out': 0,
                         'h2_soc': self.h2storage_soc,
                         'h2storage_soc_min': self.h2storage_soc_min,
                         'h2storgae_soc_max': self.h2storage_soc_max,
                         'h2_stored': 0,
                         'h2_given': 0,
                         'mod': 0,
                         'flag': self.flag}
        elif h2_out < 0:  # discharge
            re_params = self.discharge_h2(h2_out)

        else:
            re_params = self.charge_h2(h2_in)

        return re_params
