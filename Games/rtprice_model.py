import csv
import pandas as pd
class rtprice_python():

    def __init__(self) -> None:
        """
        Used in Python based Mosaik simulations as an addition to the rtprice_mosaik.rtpriceSim class.

        ...

        Attributes
        ----------
        self.consumption : int
            ???
        self.buy_price : int
            ???
        self.sell_price : int
            ???
        self.bought : dict
            ???
        self.sold : dict
            ???
        self.TC : dict
            ???
        self.TR : dict
            ???

        See Also
        --------
        Instantiating this class also creates the RTprice_result.csv file.
        """
        self.consumption = 0
        self.buy_price = 0
        self.sell_price = 0
        self.bought = {}
        self.sold = {}
        self.TC = {}
        self.TR = {}
        with open('Result/RTprice_result.csv', "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Time', 'Player', 'Sell', 'Buy', 'Total Costs', 'Total Revenue'])


    def clear(self, time:pd.Timestamp, buy_price:float, sell_price:float, buy:dict, sell:dict) -> dict:
        """
        Methods for acquiring buy and sell prices alongside bookkeeping for overall results.

        ...

        Parameters
        ----------
        time : pd.Timestamp
            The current timestamp
        buy_price : float
            The proposed buy price (?)
        sell_price : float
            The proposed sell price (?)
        buy : dict
            A collection of players/customers and their proposed buy values
        sell : dict
            A collection of players/customers and their proposed sell values
        
        Returns
        -------
        re_params : dict
            Collection of parameters and their respective values.
            Parameters are: buy_price, sell_price.
        See Also
        --------
        In addition to its function, this method also appends data to the RTprice_results.csv file 
        """
        self.buy_price = buy_price
        self.sell_price = sell_price
        if buy:
            for agent, quantity in buy.items():
                self.TC.setdefault(agent, 0)
                self.TC[agent] += -quantity/4*self.buy_price
                self.bought.setdefault(agent, 0)
                self.bought[agent] = quantity
        if sell:
            for agent, quantity in sell.items():
                self.TR.setdefault(agent, 0)
                self.TR[agent] += quantity/4*self.sell_price
                self.sold.setdefault(agent, 0)
                self.sold[agent] = quantity

        # Bookkeeper
        with open('Result/RTprice_result.csv', "a", newline='') as csvfile:
            writer = csv.writer(csvfile)
            for name, quantity in self.bought.items():
                agent_name = name
                agent_sold_quantity = self.sold.get(agent_name, 0)
                agent_bought_quantity = quantity
                total_costs = self.TC.get(agent_name, 0)
                total_revenue = self.TR.get(agent_name, 0)

                writer.writerow(
                    [time, agent_name, agent_sold_quantity, agent_bought_quantity, total_costs, total_revenue])

        re_params = {'buy_price': self.buy_price, 'sell_price': self.sell_price}
        return re_params
