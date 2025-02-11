class load_EV():

    def __init__(self, houses_case, houses_data):
        self.consumption = 0
        self.houses_case = houses_case
        self.houses_data = houses_data
        #self.resolution=resolution#min

    def demand(self, power, n):
        # load_EV gets as input charging power (kW) and n (= number of EVs charging at timestamp)
        # power is in kW
        if self.houses_case == self.houses_data:
            self.consumption = power
        else:
            self.consumption = power * self.houses_case/self.houses_data # scaling if necessary
        re_params = {'load_EV': self.consumption, 'n': n}
        return re_params