import pandas as pd


class gpcontroller_python:
    def __init__(self, soc_min:int, soc_max:int, h2_soc_min:int, h2_soc_max:int, fc_eff:float):
        """
        Constructor for the gpcontroller_python class

        ...

        Parameters
        ----------
        soc_min : int 
            ???
        soc_max : int 
            ???
        h2_soc_min : int
            ???
        h2_soc_max : int
            ???
        fc_eff : float
            ???

        Attributes
        ----------
        soc_max_b : int
            Uses parameter soc_max
        soc_min_b : int
            Uses parameter soc_min
        soc_max_h2 : int
            Uses parameter h2_soc_max
        soc_min_h2 : int
            Uses parameter h2_soc_min
        fc_eff : float
            Uses parameter fc_eff

        net : int
            = 0 
        deficit : int 
            = 0
        excess : int
            = 0
        flow_b : list
            = []
        flow_e : int
            = 0
        fc_out : int
            = 0
        h_out : int
            = 0 

        generators : pd.DataFrame()
            Empty Dataframe (???)
        demands : pd.DataFrame()
            Empty Dataframe (???)
        batteries : pd.DataFrame()
            Empty Dataframe (???)
        h2_soc : list
            Empty list (???)
        p_gen : list
            Empty list (???)
        p_dem : list
            Empty list (???)
        soc : list
            Empty list (???)
        curtailment : Boolean
            False bool (???)
        """
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


    def gpcontrol(self, generators:pd.DataFrame, demands:pd.DataFrame, batteries:pd.DataFrame, curtail:int) -> dict:#, fc_gen):
        """
        Constructor for the gpcontroller_python class

        ...

        Parameters
        ----------
        generators : pd.DataFrame
            ???
        demands : pd.DataFrame
            ???
        batteries : pd.DataFrame
            ???
        curtail : int
            ???
        
        Returns
        -------
        re_params : dict
            ???
        """
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
