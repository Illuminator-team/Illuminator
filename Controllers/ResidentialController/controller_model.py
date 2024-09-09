
class controller_python:
    def __init__(self, soc_min:int, soc_max:int, h2_soc_min:int, h2_soc_max:int, fc_eff:float) -> None:
        """
        Used in Python based Mosaik simulations as an addition to the controller_mosaik.controlSim class.

        ...

        Parameters
        ----------
        soc_min : int 
            The minimum state of charge (SOC)
        soc_max : int 
            The maximum state of charge (SOC)
        h2_soc_min : int
            ???
        h2_soc_max : int
            ???
        fc_eff : float
            ???

        Attributes
        ----------
        self.soc_min : int 
            The minimum state of charge (SOC)
        self.soc_max : int 
            The maximum state of charge (SOC)
        self.soc_max_h2 : ???
            ???
        self.soc_min_h2 : ???
            ???
        self.fc_eff : ???
            ???
        
        self.dump : int
            ???
        self.flow_b : int
            ???
        self.flow_e : int
            ???
        self.fc_out : int
            ???
        """
        self.soc_max_b = soc_max
        self.soc_min_b = soc_min
        self.soc_max_h2 = h2_soc_max
        self.soc_min_h2 = h2_soc_min
        self.fc_eff = fc_eff

        self.dump = 0
        self.flow_b = 0
        self.flow_e = 0
        self.fc_out = 0

    def control(self, wind_gen:float, pv_gen:float, load_dem:float, soc:int, h2_soc:int) -> dict:#, fc_gen):
    # def control(self,soc , pv_gen, load_dem, wind_gen):
        """
        Checks the state of flow based on wind and solar energy generation compared to demand.

        ...

        Parameters
        ----------
        wind_gen : float
            ???
        pv_gen : float 
            ???
        load_dem : float
            ???
        soc : int
            Value representing the state of charge (SOC)
        h2_soc : int
            ???
        
        Returns
        -------
        re_params : dict
            Collection of parameters and their respective values
        """
        self.soc_b = soc
        self.soc_h = h2_soc
        flow = wind_gen + pv_gen - load_dem  # kW

        if flow < 0:  # means that the demand is not completely met and we need support from battery and fuel cell
            if self.soc_b > self.soc_min_b:  # checking if soc is above minimum. It can be == to soc_max as well.
                self.flow_b = flow
                self.flow_e = 0
                self.h_out = 0

            elif self.soc_b <= self.soc_min_b:
                self.flow_b = 0
                self.flow_e = 0
                q = 39.4
                self.h_out = (flow / q) / self.fc_eff

                print('Battery Discharged')


        elif flow > 0:  # means we have over generation and we want to utilize it for charging battery and storing hydrogen
            if self.soc_b < self.soc_max_b:
                self.flow_b = flow
                self.flow_e = 0
                self.h_out = 0
            elif self.soc_b == self.soc_max_b:
                self.flow_b = 0
                if self.soc_h < self.soc_max_h2:
                    self.flow_e = flow
                    self.dump = 0
                    self.h_out = 0
                elif self.soc_h == self.soc_max_h2:
                    self.flow_e = 0
                    self.dump = flow
                    self.h_out = 0

        re_params = {'flow2b': self.flow_b, 'flow2e': self.flow_e, 'dump': self.dump, 'h2_out':self.h_out}
        return re_params
