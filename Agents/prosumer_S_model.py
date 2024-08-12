from Agents.prosumer_model import prosumer_python
import pandas as pd

class prosumer_S1(prosumer_python):
    def prosumer(self, start:pd.Timestamp, time:pd.Timestamp, generators:pd.DataFrame, demands:pd.DataFrame, storages:pd.DataFrame, em_accepted_bids:list, ft_transactions:list) -> dict:
        """
        Initializes all given parameters and returns 

        ...

        Parameters
        ----------
        start : pandas.Timestamp
            Description
        time : pandas.Timestamp
            Description
        generators : pandas.DataFrame
            Description
        demands : pandas.DataFrame
            Description
        storages : pandas.DataFrame
            Description
        em_accepted_bids : list
            Description
        ft_transactions : list
            Description

        Returns
        -------
        self.re_params : dict
            Returns a dictionary used in steps
            
        """
        self.initialize(start, time, generators, demands, storages, em_accepted_bids, ft_transactions)

        self.re_params = {}

        if self.initialized:  # Ready to play into the games
            if self.steps_em == [False, False, False]:
                self.steps_em[0] = True
            re_params = self.play_electricity_market(time, self.em_accepted_bids)
            self.re_params.update(re_params)

            if self.steps_em[2]:
                if self.steps_p2p == [False, False, False]:
                    self.steps_p2p[0] = True
                re_params = self.play_flexibility_trading(time, self.p2p_transactions)
                self.re_params.update(re_params)

            re_params = self.play_realtime_price()
            self.re_params.update(re_params)

        return self.re_params


class prosumer_S2(prosumer_python):
    def prosumer(self, start, time, generators, demands, storages, em_accepted_bids, ft_transactions):
        """
        Initializes all given parameters and returns 

        ...

        Parameters
        ----------
        start : pandas.Timestamp
            Description
        time : pandas.Timestamp
            Description
        generators : pandas.DataFrame
            Description
        demands : pandas.DataFrame
            Description
        storages : pandas.DataFrame
            Description
        em_accepted_bids : list
            Description
        ft_transactions : list
            Description

        Returns
        -------
        self.re_params : dict
            Returns a dictionary used in steps
            
            
        """
        self.initialize(start, time, generators, demands, storages, em_accepted_bids, ft_transactions)

        self.re_params = {}

        if self.initialized:  # Ready to play into the games
            if self.steps_p2p == [False, False, False]:
                self.steps_p2p[0] = True
            re_params = self.play_flexibility_trading(time, self.p2p_transactions)
            self.re_params.update(re_params)

            if self.steps_p2p[2]:
                if self.steps_em == [False, False, False]:
                    self.steps_em[0] = True
                re_params = self.play_electricity_market(time, self.em_accepted_bids)
                self.re_params.update(re_params)

            re_params = self.play_realtime_price()
            self.re_params.update(re_params)

        return self.re_params


class prosumer_S3(prosumer_python):
    """
    Inherits Prosumer_pthon, does nothing else different
    """
    pass
