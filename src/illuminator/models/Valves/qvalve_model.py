import pandas as pd


class qvalve_python:
    def __init__(self):
        self.q_eboiler_net = 0
        self.q_eboiler_stor = 0
        self.q_stor_net = 0


    def route(self, q_eboiler, q_stor):
        if q_stor > 0:                                 # filling the storage
            if q_eboiler >= q_stor:
                self.q_eboiler_stor = q_stor
                self.q_eboiler_net = q_eboiler - q_stor
                self.q_stor_net = 0
            else:
                self.q_eboiler_stor = q_eboiler
                self.q_eboiler_net = 0
                self.q_stor_net = q_eboiler - q_stor

        else:                                       # emptying the storage
            self.q_eboiler_stor = 0
            self.q_eboiler_net = q_eboiler
            self.q_stor_net = -q_stor

        re_params = {'q_eboiler' : q_eboiler, 'q_stor' : q_stor,
                     'q_eboiler_net' : self.q_eboiler_net, 'q_stor_net': self.q_stor_net,
                     'q_eboiler_stor' : self.q_eboiler_stor}
        return re_params
