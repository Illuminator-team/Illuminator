import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import csv


def match_trades(supply_offers:list, demand_requests:list) -> list:
    """
    Matches supply offers and demand requests to create trades. 

    ...

    Parameters
    ----------
    supply_offers : list
        Unsorted list of supply offers containing the name of the supplier, the offers's date and value
    demand_requests : list
        Unsorted list of demand requests containing the name of the trader, the request's date and value

    Returns
    -------
    trades : list
        Returns a sorted list of trades based on supply and demand
    """
    trades = []

    # Sort demand requests in descending order based on price
    demand_requests.sort(key=lambda x: (x[1][2], datetime.strptime(x[1][0], '%Y-%m-%d %H:%M:%S')))
    demand_requests.sort(key=lambda x: x[1][2], reverse=True)

    for request in demand_requests:
        request_player, request_info = request
        request_time, request_quantity, request_price = request_info

        while request_quantity > 0:
            best_offer = None
            best_price_diff = float('-inf')

            for offer in supply_offers:
                offer_player, offer_info = offer
                offer_time, offer_quantity, offer_price = offer_info
                if offer_time != request_time:
                    continue
                if offer_price < request_price and request_price - offer_price > best_price_diff and offer_quantity > 0:
                    best_offer = offer
                    best_price_diff = request_price - offer_price

            if best_offer:
                offer_player, offer_info = best_offer
                offer_time, offer_quantity, offer_price = offer_info

                trade_price = request_price
                trade_quantity = min(request_quantity, offer_quantity)

                trades.append([request_time, request_player, request_quantity, request_price,
                               offer_player, offer_quantity, offer_price, trade_quantity, trade_price])

                request_quantity -= trade_quantity
                offer_quantity -= trade_quantity

                supply_offers[supply_offers.index(best_offer)] = \
                    (offer_player, [offer_time, offer_quantity, offer_price])
            else:  # No offer found for the request and exit the loop
                break

    trades.sort(key=lambda x: x[0])
    return trades


class p2ptrading_python:
    def __init__(self) -> None:
        """
        Used in Python based Mosaik simulations as an addition to the p2ptrading_mosaik.p2ptradingSim class.
        
        ...

        Attributes
        ----------
        self.supply_offers : list
            ???
        self.demand_requests : list
            ???
        self.players : pd.DataFrame
            ???
        self.cleared : bool
            ???
        self.trades : list
            ???
        self.transactions : dict
            ???
        """
        self.supply_offers = []
        self.demand_requests = []
        self.players = pd.DataFrame # Seemingly another misunderstanding of how to create a DF object
        self.cleared = False
        self.trades = []
        self.transactions = {}

    def p2ptrading(self, current_time:pd.Timestamp, players:pd.DataFrame) -> dict:
        """
        Description

        ...

        Parameters
        ----------
        current_time : pd.Timestamp
            The current time during trading
        players : pd.Dataframe
            The players, their names, demand bids and supply bids (?)
        
        Returns
        -------
        re_params : dict
            Collection of parameters and their respective values
        
        See Also
        --------
        This method creates the Ftrading_results.csv, saving data into it.
        """
        re_params = {'quantity_traded': 0, 'transactions': None}
        if not players.empty and not self.cleared:
            self.players = players

            for _, row in players.iterrows():
                if row['supply_offers'] is not None and row['supply_offers'] != 0:
                    for bid in row['supply_offers']:
                        self.supply_offers.append((row['name'], bid))
                if row['demand_requests'] is not None and row['demand_requests'] != 0:
                    for bid in row['demand_requests']:
                        self.demand_requests.append((row['name'], bid))

            self.trades = match_trades(self.supply_offers, self.demand_requests)

            # Organize self.transactions
            for trade in self.trades:
                timestamp, request_player, request_quantity, request_price, \
                    offer_player, offer_quantity, offer_price, trade_quantity, trade_price = trade

                if request_player not in self.transactions:
                    self.transactions[request_player] = {'sell': [], 'buy': []}

                if offer_player:
                    if offer_player not in self.transactions:
                        self.transactions[offer_player] = {'sell': [], 'buy': []}

                    self.transactions[request_player]['buy'].append([timestamp, request_quantity, request_price,
                                                                     trade_quantity,  trade_price])
                    self.transactions[offer_player]['sell'].append([timestamp, offer_quantity, offer_price,
                                                                    trade_quantity,  trade_price])

            # Bookkeeper
            if self.transactions:
                total_costs = {}
                total_revenue = {}

                for player, transaction in self.transactions.items():
                    total_costs[player] = sum(quantity/4 * price for _, _, _, quantity, price in transaction['buy'])
                    total_revenue[player] = sum(quantity/4 * price for _, _, _, quantity, price in transaction['sell'])

                with open('Result/Ftrading_results.csv', 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)

                    writer.writerow(['Player', 'Sell', 'Buy', 'Total Costs', 'Total Revenue'])

                    for player, transaction in self.transactions.items():
                        sell_transactions = transaction['sell']
                        buy_transactions = transaction['buy']
                        cost = total_costs[player]
                        revenue = total_revenue[player]

                        writer.writerow([player, sell_transactions, buy_transactions, cost, revenue])

            self.cleared = True
            re_params = {'quantity_traded': 0, 'transactions': self.transactions}
            return re_params

        elif self.cleared:
            quantity_traded = 0
            for trade in self.trades:
                if trade[0] == current_time.strftime('%Y-%m-%d %H:%M:%S'):
                    quantity_traded += trade[7]
            re_params = {'quantity_traded': quantity_traded, 'transactions': self.transactions}
            return re_params
        else:
            return re_params
