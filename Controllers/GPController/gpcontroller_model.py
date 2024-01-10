import pandas as pd


class gpcontroller_python:
    def __init__(self, soc_min, soc_max, h2_soc_min, h2_soc_max, fc_eff):
        self.soc_max_b = soc_max
        self.soc_min_b = soc_min
        self.soc_max_h2 = h2_soc_max
        self.soc_min_h2 = h2_soc_min
        self.fc_eff = fc_eff

        self.net = 0                        # Net Power (Gen - Dem)
        self.deficit = 0                    # Power that cannot be provided by batteries
        self.excess = 0                     # Power that cannot be stored in batteries
        self.flow_b = []
        self.flow_e = 0
        self.fc_out = 0         # []?
        self.h_out = 0          # []?

        self.generators = pd.DataFrame()
        self.demands = pd.DataFrame()
        self.batteries = pd.DataFrame()
        self.h2_soc = []
        self.p_gen = []
        self.p_dem = []
        self.soc = []
        self.curtailment = False


    def gpcontrol(self, generators, demands, batteries, curtail):#, fc_gen):

        self.generators = generators
        self.demands = demands
        self.batteries = batteries
        self.net = 0                                # Net difference GEN - DEM
        self.deficit = 0                            # Power that cannot be provided locally
        self.excess = 0                             # Power not used locally
        if not generators.empty:
            self.p_gen = generators['p_gen']
            tot_p_gen = sum(self.p_gen)
            self.net += tot_p_gen
            if curtail == 1 and self.curtailment:                           # Curtail
                for i in range(len(self.p_gen)):
                    self.p_gen = [0] * len(self.p_gen)
                self.net = 0

        if not demands.empty:
            self.p_dem = demands['p_dem']
            tot_p_dem = sum(self.p_dem)
            self.net -= tot_p_dem

        if not batteries.empty:
            self.soc = batteries['soc']
            self.flow_b = [self.net / len(self.soc)] * len(self.soc)       # Power to the batteries (Equally divided)
            if curtail == 1 and self.curtailment:                           # Curtail
                self.flow_b = [2] * len(self.soc)
                self.net -= (2 * len(self.soc))
                self.deficit = self.net
            if self.net <= 0:
                for i in range(len(self.soc)):
                    if self.soc[i] == self.soc_min_b:
                        print('Battery ' + str(i) + ' fully discharged')
                        self.deficit += self.flow_b[i]
                        self.flow_b[i] = 0
                        if curtail == 1 and self.curtailment:
                            self.deficit = self.net
                            self.flow_b = [2] * len(self.soc)
            else:
                for i in range(len(self.soc)):
                    if self.soc[i] == self.soc_max_b:
                        print('Battery ' + str(i) + ' fully charged')
                        self.excess += self.flow_b[i]
                        self.flow_b[i] = 0
        else:
            if self.net < 0:
                self.deficit = self.net
            if self.net > 0:
                self.excess = self.net

        re_params = {'flow2b': self.flow_b, 'net': self.net, 'deficit': self.deficit, 'excess': self.excess,
                     'generator': self.p_gen, 'demand': self.p_dem, 'storage': self.soc}
        return re_params
