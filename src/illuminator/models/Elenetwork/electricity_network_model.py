import pandas as pd


class electricity_network_python:
    def __init__(self, max_congestion, p_loss_m, length) -> None:
        """
        Used in Python based Mosaik simulations as an addition to the electricity_network_mosaik.electricitynetworkSim class.
        
        ...

        Parameters
        ----------
        max_congestion : ???
            ???
        p_loss?m : ???
            ???
        length : ???
            ???

        Attributes
        ----------
        self.max_congestion : ???
            ???
        self.p_loss : ???
            ???
        self.congestion : bool
            ???
        self.p_in : int
            ???
        self.p_out : int
            ???
        self.p_tot : int
            ???
        """
        self.max_congestion = max_congestion
        self.p_loss = p_loss_m*length
        self.congestion = False
        self.p_in = 0
        self.p_out = 0
        self.p_tot = 0
    def electricitynetwork(self, p_in:int, p_out:int) -> dict:
        """
        Description

        ...
        
        Parameters
        ----------
        p_in : int
            ???
        p_out : int
            ???

        Returns
        -------
        re_params : dict
            Collection of parameters and their respective values
        """
        self.p_in = p_in
        self.p_out = p_out
        self.p_tot = sum(p_in) - sum(p_out) - self.p_loss
        if self.p_tot > self.max_congestion:
            self.congestion = True

        re_params = {'p_tot': self.p_tot, 'p_in': self.p_in, 'p_out': self.p_out, 'p_loss': self.p_loss,
                     'congestion': self.congestion}
        return re_params    
