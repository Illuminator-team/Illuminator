import pandas as pd
from datetime import datetime, timedelta
from abc import ABC, abstractmethod


def average(self:list, dates:list) -> list:
    """
    Calculate the average of the hourly curve for the day

    ...

    Parameters
    ----------
    self : list
        A nested list containing the calculated energy values for a specific date
    dates : list
        A nested list of dates for a specific date in "YYYY-MM-DD hh:mm:ss" format

    Returns
    -------
    hourly_average : list
        A nested list containin the calculated hourly averages for a given date range
    """
    from collections import defaultdict
    # Creates a dict with list type as values
    # Self is not really "self". It contains different values to the class below
    # In reality it is ex_p_gen or ex_p_dem
    hourly_curve = defaultdict(list)
    hourly_average = []

    # Loops over all items in self
    for row in self:
        # Adds values for 
        for i in range(len(row)):
            hour = dates[i][11:13]
            hourly_curve[hour].append(row[i])

        row_average = []
        for hour in hourly_curve:
            avg = sum(hourly_curve[hour]) / len(hourly_curve[hour])
            row_average.append(avg)
        hourly_average.append(row_average)
        hourly_curve.clear()

    return hourly_average

# NOTE: Mosaik avoids using ABC to prevent python version issues.
class prosumer_python(ABC):
    def __init__(self, eid:list, forecasted_data:list, metrics:list) -> None:
        """
        Used in Python based Mosaik simulations as an addition to the prosumer_mosaik.prosumerSim class.


        ...

        Parameters
        ----------
        eid : list
            ???
        forcasted_data : list
            ???
        metrics : list
            ???
        """
        self.eid = eid
        self.time = []
        self.current_time = None
        self.forecasted_data = forecasted_data[eid]
        self.dates = forecasted_data['dates']
        self.generators = pd.DataFrame()
        self.demands = pd.DataFrame()
        self.storages = pd.DataFrame()
        self.ex_p_gen = []
        self.ex_p_dem = []
        self.ex_soc = []
        self.ex_net = []
        self.ex_excess = []
        self.ex_deficit = []

        self.initialized = False
        self.MC = metrics[eid]['MC']
        self.MB = metrics[eid]['MB']
        self.MO = metrics[eid]['MO']
        self.MR = metrics[eid]['MR']

        self.em_demand_bids = []
        self.em_supply_bids = []
        self.em_accepted_bids = []
        self.steps_em = [False, False, False]  # Steps 1:Initiated 2: Received 3: Completed

        self.p2p_supply_offers = 0
        self.p2p_demand_requests = 0
        self.p2p_transactions = []
        self.steps_p2p = [False, False, False]
        self.re_params = {}

    @abstractmethod
    def prosumer(self, start, time, generators, demands, storages, em_accepted_bids, p2p_transactions):
        pass

    def initialize(self, start:pd.Timestamp, time:pd.Timestamp, generators:pd.DataFrame, demands:pd.DataFrame, storages:pd.DataFrame, em_accepted_bids:list, p2p_transactions:list) -> None:
        """
        An initilization function used for calculation and variable assignment

        ...

        Parameters
        ----------
        start : pandas.Timestamp
            The starting point in time
        time : pandas.Timestamp
            A representation of the current point in time
        generators : pandas.DataFrame
            Generated values used for populating the self.generator variable with forecasted data
        demands : pandas.DataFrame
            Demand values used for populating the self.demands variable with forecasted data
        storages : pandas.DataFrame
            Storage values used for populating the self.storages variable with forecasted data
        em_accepted_bids : list
            ???
        p2p_transactions : list
            ???
        """
        self.em_accepted_bids = em_accepted_bids
        self.p2p_transactions = p2p_transactions
        # Initialize forecasted data and update real time info
        self.ex_net = self.forecasted_data['net']
        self.ex_deficit = self.forecasted_data['deficit']
        self.ex_excess = self.forecasted_data['excess']
        # Obtain time horizon
        start_time_str = start.strftime('%Y-%m-%d %H:%M:%S')
        start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
        self.current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        time_vector = [start_time]
        for i in range(len(self.ex_excess) - 1):
            next_time = time_vector[-1] + timedelta(minutes=15)
            time_vector.append(next_time)
        self.time = [str(time) for time in time_vector]
        # Initialize inputs
        if not generators.empty:
            if not self.ex_p_gen:  # Upload forecasted data for each asset
                for gen in generators['name']:
                    forecasted_generators_data = self.forecasted_data[gen]
                    self.ex_p_gen.append(forecasted_generators_data)
                self.generators = generators
                self.generators['ex_p_gen'] = self.ex_p_gen
                self.generators['av_ex_p_gen'] = average(self.ex_p_gen, self.dates)
                self.initialized = True
            else:
                self.generators['p_gen'] = generators['p_gen']
        if not demands.empty:  # Upload forecasted data for each asset
            if not self.ex_p_dem:
                for dem in demands['name']:
                    forecasted_demands_data = self.forecasted_data[dem]
                    self.ex_p_dem.append(forecasted_demands_data)
                self.demands = demands
                self.demands['ex_p_dem'] = self.ex_p_dem
                self.demands['av_ex_p_dem'] = average(self.ex_p_dem, self.dates)
            else:
                self.demands['p_dem'] = demands['p_dem']
                self.initialized = True
        if not storages.empty:  # Upload forecasted data for each asset
            if not self.ex_soc:
                for dem in storages['name']:
                    forecasted_storages_data = self.forecasted_data[dem]
                    self.ex_soc.append(forecasted_storages_data)
                self.storages = storages
                self.storages['ex_soc'] = self.ex_soc
            else:
                self.storages['soc'] = storages['soc']
                self.initialized = True
        return

    def play_realtime_price(self) -> list:
        """
        Gets the real-time price based on the current time
        
        ...

        Returns
        -------
        re_params : dict
            Returns the calculated hourly averages for a given date range
        """
        index = self.time.index(self.current_time)
        re_params = {'rt_buy': self.ex_deficit[index], 'rt_sell': self.ex_excess[index]}
        return re_params

    def play_flexibility_trading(self, time:pd.Timestamp, p2p_transactions:list) -> dict:
        """
        A method to simulate flexibility trading (?)

        Parameters
        ----------
        time : pandas.Timestamp
            A representation of a point in time
        p2p_transactions : list
            ???

        Returns
        -------
        re_params : dictionary
            The representation of a specific step of trading

        """
        re_params = {}
        if self.steps_p2p == [True, False, False]:  # Step 1: make bids
            self.generators['MO'] = self.MO
            self.demands['MR'] = self.MR
            self.p2p_supply_offers = self.supply(self.ex_excess, 'MO')
            self.p2p_demand_requests = self.demand(self.ex_deficit, 'MR')
            re_params = {'p2p_supply_offers': self.p2p_supply_offers, 'p2p_demand_requests': self.p2p_demand_requests}
            self.steps_p2p[1] = True

        elif self.steps_p2p == [True, True, False] and p2p_transactions:  # Step 2: modify ex_excess and ex_deficit
            p2p_transactions_sell = p2p_transactions['sell']
            p2p_transactions_buy = p2p_transactions['buy']
            if p2p_transactions_sell is not None:
                for bid in p2p_transactions_sell:
                    index = self.time.index(bid[0])
                    self.ex_excess[index] -= bid[3]
                    self.ex_excess[index] = round(self.ex_excess[index], 5)
                    self.generators.loc[self.generators['MO'] == bid[2], 'ex_p_gen'].to_list()[0][index] -= bid[3]

            if p2p_transactions_buy is not None:
                for bid in p2p_transactions_buy:
                    index = self.time.index(bid[0])
                    self.ex_deficit[index] += bid[3]
                    self.ex_deficit[index] = round(self.ex_deficit[index], 5)
                    self.demands.loc[self.demands['MR'] == bid[2], 'ex_p_dem'].to_list()[0][index] -= bid[3]

            self.steps_p2p[2] = True

        if self.steps_p2p[2]:
            p2p_transactions_sell = p2p_transactions['sell']
            p2p_transactions_buy = p2p_transactions['buy']
            if p2p_transactions_sell is not None:
                for bid in p2p_transactions_sell:
                    if bid[0] == time.strftime('%Y-%m-%d %H:%M:%S'):
                        re_params = {'p2p2p': bid[3]}
            if p2p_transactions_buy is not None:
                for bid in p2p_transactions_buy:
                    if bid[0] == time.strftime('%Y-%m-%d %H:%M:%S'):
                        re_params = {'p2p2p': -bid[3]}

        return re_params

    def play_electricity_market(self, time:pd.Timestamp, em_accepted_bids:list) -> dict:
        """
        A method to simulate the electricity market?

        Parameters
        ----------
        time : pandas.Timestamp
            A representation of a point in time
        em_accepted_bids : list
            ???

        Returns
        -------
        re_params : dictionary
            A dictionary representing a specific step of trading based on supply and demand

        """
        re_params = {}
        if self.steps_em == [True, False, False]:  # Step 1: make bids
            self.generators['MC'] = self.MC
            self.demands['MB'] = self.MB
            self.em_supply_bids = self.supply(self.ex_excess, 'MC')
            self.em_demand_bids = self.demand(self.ex_deficit, 'MB')
            re_params = {'em_supply_bids': self.em_supply_bids, 'em_demand_bids': self.em_demand_bids}
            self.steps_em[1] = True

        elif self.steps_em == [True, True, False] and em_accepted_bids:  # Step 2: modify ex_excess and ex_deficit
            accepted_supply_bids = em_accepted_bids['supply_bids']
            if accepted_supply_bids is not None:
                for bid in accepted_supply_bids:
                    index = self.time.index(bid[0])
                    self.ex_excess[index] -= bid[1]
                    self.ex_excess[index] = round(self.ex_excess[index], 5)
                    self.generators.loc[self.generators['MC'] == bid[2], 'ex_p_gen'].to_list()[0][index] -= bid[1]

            accepted_demand_bids = em_accepted_bids['demand_bids']
            if accepted_demand_bids is not None:
                for bid in accepted_demand_bids:
                    index = self.time.index(bid[0])
                    self.ex_deficit[index] += bid[1]
                    self.ex_deficit[index] = round(self.ex_deficit[index], 5)
                    self.demands.loc[self.demands['MB'] == bid[2], 'ex_p_dem'].to_list()[0][index] -= bid[1]

            self.steps_em[2] = True

        if self.steps_em[2]:
            accepted_supply_bids = em_accepted_bids['supply_bids']
            if accepted_supply_bids is not None:
                for bid in accepted_supply_bids:
                    if bid[0] == time.strftime('%Y-%m-%d %H:%M:%S'):
                        re_params = {'p2em': bid[1]}
            accepted_demand_bids = em_accepted_bids['demand_bids']
            if accepted_demand_bids is not None:
                for bid in accepted_demand_bids:
                    if bid[0] == time.strftime('%Y-%m-%d %H:%M:%S'):
                        re_params = {'p2em': -bid[1]}
        return re_params

    def supply(self, ex_excess:list, metric:str) -> list:
        """
        Provides a list of supplies

        Parameters
        ----------
        ex_excess : list
            The list of excess energy in chronological order (???)
        metric : str
            A two character string. Options:[MC, MB, MO, MR]

        Returns
        -------
        bids : list
            List object representing supply

        """
        bids = []
        for excess in ex_excess:
            if excess > 0:
                hour = ex_excess.index(excess)
                sorted_indexes = self.generators.sort_values(metric, ascending=False).index.tolist()
                tot_p_dem = 0
                if not self.demands.empty:
                    for i in range(len(self.demands['ex_p_dem'])):
                        tot_p_dem += self.demands['ex_p_dem'][i][hour]
                tot = 0
                for i in sorted_indexes:
                    production = self.generators.loc[i, 'ex_p_gen'][hour]
                    if production > tot_p_dem != 0:
                        production -= tot_p_dem
                        tot_p_dem = 0
                        tot += production
                        bids.append([self.dates[hour], production, self.generators.loc[i, metric]])
                    elif production < tot_p_dem != 0:
                        tot_p_dem -= production
                    elif tot_p_dem == 0 and production != 0:
                        tot += production
                        bids.append([self.dates[hour], production, self.generators.loc[i, metric]])
                if int(tot) != int(excess):
                    print('supply bids error')
        if not bids:
            bids = None
        return bids

    def demand(self, ex_deficit:list, metric:str) -> list:
        """
        Provides a list of demand

        Parameters
        ----------
        ex_deficit : list
            The energy deficits in chronological order
        metric : str
            A two character string. Options:[MC, MB, MO, MR]

        Returns
        -------
        bids : list
            The representation of demand

        """
        bids = []
        for time in self.time:
            hour = self.time.index(time)
            deficit = ex_deficit[hour]
            if deficit < 0:
                sorted_indexes = self.demands.sort_values(metric, ascending=False).index.tolist()
                tot_p_gen = 0
                if not self.generators.empty:
                    for i in range(len(self.generators['ex_p_gen'])):               #-1
                        tot_p_gen += self.generators['ex_p_gen'][i][hour]
                tot = 0
                for i in sorted_indexes:
                    consumption = self.demands.loc[i, 'ex_p_dem'][hour]
                    if consumption > tot_p_gen != 0:
                        consumption -= tot_p_gen
                        tot_p_gen = 0
                        tot += consumption
                        bids.append([self.dates[hour], consumption, self.demands.loc[i, metric]])
                    elif consumption < tot_p_gen != 0:
                        tot_p_gen -= consumption
                    elif tot_p_gen == 0 and consumption != 0:
                        tot += consumption
                        bids.append([self.dates[hour], consumption, self.demands.loc[i, metric]])
                if round(tot) != round(-deficit):
                    print('demand bids error')
        if not bids:
            bids = None
        return bids
