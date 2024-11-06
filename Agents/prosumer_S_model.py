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
            The starting point in time.
        time : pandas.Timestamp
            A representation of the current point in time.
        generators : pandas.DataFrame
            Generated values used for populating the self.generator variable with forecasted data
        demands : pandas.DataFrame
            Demand values used for populating the self.demands variable with forecasted data
        storages : pandas.DataFrame
            Storage values used for populating the self.storages variable with forecasted data
        em_accepted_bids : list
            ???
        ft_transactions : list
            ???

        Returns
        -------
        self.re_params : dict
            Returns a dictionary used in steps (???)
            
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
    def prosumer(self, start:pd.Timestamp, time:pd.Timestamp, generators:pd.DataFrame, demands:pd.DataFrame, storages:pd.DataFrame, em_accepted_bids:list, ft_transactions:list) -> dict:
        """
        Initializes all given parameters and returns 

        ...

        Parameters
        ----------
        start : pandas.Timestamp
            The starting point in time.
        time : pandas.Timestamp
            A representation of the current point in time.
        generators : pandas.DataFrame
            Generated values used for populating the self.generator variable with forecasted data
        demands : pandas.DataFrame
            Demand values used for populating the self.demands variable with forecasted data
        storages : pandas.DataFrame
            Storage values used for populating the self.storages variable with forecasted data
        em_accepted_bids : list
            ???
        ft_transactions : list
            ???

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
    Inherits Prosumer_python, does nothing else different
    """
    pass
