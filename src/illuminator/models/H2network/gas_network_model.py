import pandas as pd


class gas_network_python:
    def __init__(self, max_congestion, V, leakage):
        self.max_congestion = max_congestion
        self.congestion = False
        self.V = V                      #volume
        self.leakage = leakage
        self.p_int = 0
        self.T = 273.15           #Kelvin STP
        self.R = 4124            # gas constant J/(kg*K)
        self.M = 0.002016         # molar msass kg/mol

    def gasnetwork(self, flow_in, flow_out):
        for i in range(len(flow_in)):
            flow_in[i] = flow_in[i] / 60           #kg/s
        for i in range(len(flow_out)):
            flow_out[i] = flow_out[i] / 60  #kg/s
        flow_tot_s = sum(flow_in) - sum(flow_out) * (1-self.leakage)          #kg/s
        self.p_int = flow_tot_s * self.T * self.R / self.V * self.M / 1e5    # bar


        flow_tot_min = flow_tot_s*60            #kg/min
        if self.p_int > self.max_congestion:
            self.congestion = True

        for i in range(len(flow_in)):
            flow_in[i] = flow_in[i] * 60  # kg/min
        for i in range(len(flow_out)):
            flow_out[i] = flow_out[i] * 60  # kg/min

        re_params = {'flow_tot': flow_tot_min, 'flow_in': flow_in, 'flow_out': flow_out,
                     'congestion': self.congestion, 'p_int': self.p_int}
        return re_params
