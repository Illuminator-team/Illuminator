import pandas as pd


class h2valve_python:
    def __init__(self):
        self.h2_elec_net = 0
        self.h2_elec_stor = 0
        self.h2_stor_net = 0
        self.h2_stor_fc = 0
        self.h2_fc_net = 0

    def route(self, h2_elec, h2_stor, h2_fc):

        if h2_stor > 0:                                 # filling the storage
            self.h2_stor_fc = 0
            self.h2_fc_net = h2_fc
            if h2_elec >= h2_stor:
                self.h2_elec_stor = h2_stor
                self.h2_elec_net = h2_elec - h2_stor
                self.h2_stor_net = 0
            else:
                self.h2_elec_stor = h2_elec
                self.h2_elec_net = 0
                self.h2_stor_net = h2_elec - h2_stor

        else:                                       # emptying the storage
            self.h2_elec_stor = 0
            self.h2_elec_net = h2_elec
            if -h2_stor >= h2_fc:
                self.h2_stor_fc = h2_fc
                self.h2_stor_net = -h2_stor - h2_fc
                self.h2_fc_net = 0
            else:
                self.h2_stor_fc = -h2_stor
                self.h2_stor_net = 0
                self.h2_fc_net = h2_fc + h2_stor

        re_params = {'h2_elec' : h2_elec, 'h2_stor' : h2_stor, 'h2_fc' : h2_fc,
                     'h2_elec_net' : self.h2_elec_net, 'h2_stor_net': self.h2_stor_net, 'h2_fc_net': self.h2_fc_net,
                     'h2_elec_stor' : self.h2_elec_stor, 'h2_stor_fc': self.h2_stor_fc}
        return re_params
