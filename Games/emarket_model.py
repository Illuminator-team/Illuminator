import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import csv

def find_accepted_bids(sorted_supply_bids, sorted_demand_bids, num_s_bid, num_d_bid):
    accepted_supply_bids = []
    for i in range(num_s_bid+1):
        accepted_supply_bids.append(sorted_supply_bids[i])

    accepted_demand_bids = []
    for i in range(num_d_bid+1):
        accepted_demand_bids.append(sorted_demand_bids[i])

    return accepted_supply_bids, accepted_demand_bids

def clear(date_time, supply_bids, demand_bids):
    # Filter bids for the chosen date and time
    supply_bids_for_date_time = [bid for bid in supply_bids if bid[0] == date_time]
    demand_bids_for_date_time = [bid for bid in demand_bids if bid[0] == date_time]

    # Sort bids by price
    supply_bids_for_date_time.sort(key=lambda x: x[2])
    demand_bids_for_date_time.sort(key=lambda x: x[2], reverse=True)

    # Calculate cumulative quantities
    supply_quantity = np.cumsum([bid[1] for bid in supply_bids_for_date_time])
    demand_quantity = np.cumsum([bid[1] for bid in demand_bids_for_date_time])
    supply_price = [bid[2] for bid in supply_bids_for_date_time]
    demand_price = [bid[2] for bid in demand_bids_for_date_time]

    market_quantity = None
    market_price = None
    clearing_quantity = None
    clearing_bid = None
    accepted_supply_bids = None
    accepted_demand_bids = None
    if not supply_price or not demand_price:
        return market_quantity, market_price, clearing_bid, clearing_quantity, accepted_supply_bids, accepted_demand_bids
    # Clear
    x = supply_quantity
    y = supply_price
    points_s = [[0, y[0]]]  # Initialize with the starting point [0, y[0]]

    for i in range(len(x)):
        points_s.append([x[i], y[i]])  # Add the next vertex [x[i], y[i]]
        if i < len(x) - 1:
            points_s.append([x[i], y[i + 1]])
            new_points_s = []               # Drop duplicates
            for point in points_s:
                if point not in new_points_s:
                    new_points_s.append(point)
            points_s = new_points_s

    x = demand_quantity
    y = demand_price
    points_d = [[0, y[0]]]  # Initialize with the starting point [0, y[0]]

    for i in range(len(x)):
        points_d.append([x[i], y[i]])  # Add the next vertex [x[i], y[i]]
        if i < len(x) - 1:
            points_d.append([x[i], y[i + 1]])
            new_points_d = []               # Drop duplicates
            for point in points_d:
                if point not in new_points_d:
                    new_points_d.append(point)
            points_d = new_points_d

    if points_s[0][1] > points_d[0][1]:  # Supply price >  demand price at 0
        return [market_quantity, market_price, clearing_bid, clearing_quantity, accepted_supply_bids, accepted_demand_bids]

    s_bid = -1
    for i in range(len(points_s) - 1):
        x1, y1 = points_s[i]
        x2, y2 = points_s[i + 1]
        if x1 == x2:  # Vertical segment in supply curve
            d_bid = 0
            for j in range(len(points_d) - 1):
                x3, y3 = points_d[j]
                x4, y4 = points_d[j + 1]
                if y3 == y4:
                    if x3 <= x1 <= x4 and y1 <= y3 <= y2:  # Horizontal segment in demand curve
                        market_quantity = x1
                        market_price = y3
                        clearing_bid = demand_bids_for_date_time[d_bid]
                        clearing_quantity = x1 - x3
                        accepted_supply_bids, accepted_demand_bids = \
                            find_accepted_bids(supply_bids_for_date_time, demand_bids_for_date_time, s_bid, d_bid)
                        return [market_quantity, market_price, clearing_bid, clearing_quantity, accepted_supply_bids, accepted_demand_bids]
                    d_bid += 1

        elif y1 == y2:  # Horizontal segment in supply curve
            s_bid += 1
            d_bid = -1
            for j in range(len(points_d) - 1):
                x3, y3 = points_d[j]
                x4, y4 = points_d[j + 1]
                if x3 == x4 and (x1 <= x3 <= x2 and y4 <= y1 <= y3):  # Vertical segment in demand curve
                    market_quantity = x3
                    market_price = y1
                    clearing_bid = supply_bids_for_date_time[s_bid]
                    clearing_quantity = x3 - x1
                    accepted_supply_bids, accepted_demand_bids = \
                        find_accepted_bids(supply_bids_for_date_time, demand_bids_for_date_time, s_bid, d_bid)
                    return [market_quantity, market_price, clearing_bid, clearing_quantity, accepted_supply_bids, accepted_demand_bids]
                if y3 == y4:
                    d_bid += 1

    return None, None, None, None, None, None

    # No intersection
    d_bid = 0
    s_bid = 0
    if points_d[-1][0] > points_s[-1][0] and points_d[-1][1] < points_s[-1][1]:
        s_bid = len(supply_bids_for_date_time) - 1
        for j in range(len(points_d) - 1):
            x3, y3 = points_d[j]
            x4, y4 = points_d[j + 1]
            if y3 == y4:
                if x3 < points_s[-1][0] < x4:
                    market_price = (points_s[-1][1] + y3) / 2
                    market_quantity = points_s[-1][0]
                    clearing_bid = demand_bids_for_date_time[d_bid]
                    clearing_quantity = points_s[-1][0] - x3
                    accepted_supply_bids, accepted_demand_bids = \
                        find_accepted_bids(supply_bids_for_date_time, demand_bids_for_date_time, s_bid, d_bid)
                    return [market_quantity, market_price, clearing_bid, clearing_quantity, accepted_supply_bids, accepted_demand_bids]
                d_bid += 1
    else:
        d_bid = len(demand_bids_for_date_time) - 1
        for i in range(len(points_s) - 1):
            x3, y3 = points_s[i]
            x4, y4 = points_s[i + 1]
            if y3 == y4:
                if x3 < points_d[-1][0] < x4:
                    market_price = (points_d[-1][1] + y3) / 2
                    market_quantity = points_d[-1][0]
                    clearing_bid = supply_bids_for_date_time[s_bid]
                    clearing_quantity = points_d[-1][0] - x3
                    accepted_supply_bids, accepted_demand_bids = \
                        find_accepted_bids(supply_bids_for_date_time, demand_bids_for_date_time, s_bid, d_bid)
                    return [market_quantity, market_price, clearing_bid, clearing_quantity, accepted_supply_bids, accepted_demand_bids]
                s_bid += 1



class emarket_python:
    def __init__(self, sim_start, sim_end, initial_supply_bids, initial_demand_bids):
        self.sim_start = datetime.strptime(sim_start, '%Y-%m-%d %H:%M:%S')
        self.sim_end = datetime.strptime(sim_end, '%Y-%m-%d %H:%M:%S')
        self.supply_bids = initial_supply_bids
        self.demand_bids = initial_demand_bids
        self.players = pd.DataFrame
        self.s_bidding = True
        self.d_bidding = True
        self.em_prices = []
        self.em_quantities = []
        self.cleared = False
        self.accepted_bids = {}
        self.clearing_bids = []
        self.clearing_quantities = []
        self.accepted_demand_bids = []
        self.accepted_supply_bids = []

    def emarket(self, current_time, players):
        re_params = {}
        if not players.empty and not self.cleared:
            self.players = players

            for _, row in players.iterrows():
                if row['supply_bids'] is not None and row['supply_bids'] != 0:
                    self.supply_bids.extend(row['supply_bids'])
                if row['demand_bids'] is not None and row['demand_bids'] != 0:
                    self.demand_bids.extend(row['demand_bids'])

            # Day ahead clearing
            while current_time <= self.sim_end:
                delta = timedelta(minutes=15)
                time = current_time.strftime("%Y-%m-%d %H:%M:%S")
                market_quantity, market_price, clearing_bid, clearing_quantity,  accepted_supply_bids, accepted_demand_bids = \
                clear(time, self.supply_bids, self.demand_bids)

                self.em_prices += [[current_time, market_price]]
                self.em_quantities += [[current_time, market_quantity]]
                self.clearing_bids += [clearing_bid]
                self.clearing_quantities += [clearing_quantity]
                if accepted_supply_bids is not None:
                    self.accepted_supply_bids += accepted_supply_bids
                if accepted_demand_bids is not None:
                    self.accepted_demand_bids += accepted_demand_bids
                current_time += delta

            # Bookkeeper
            market_results = []
            for i, row in players.iterrows():
                player_id = row['name']
                received_supply_bids = []
                accepted_supply_bids = []
                received_demand_bids = []
                accepted_demand_bids = []
                total_revenue = 0
                total_costs = 0

                if row['supply_bids'] is not None and row['supply_bids'] != 0:
                    supply_bids = row['supply_bids']
                    for bid in supply_bids:
                        received_supply_bids.append(bid.copy())
                        if bid in self.accepted_supply_bids:
                            if bid in self.clearing_bids:  # Resize clearing bid
                                bid[1] = self.clearing_quantities[self.clearing_bids.index(bid)]
                            accepted_supply_bids.append(bid)
                            for price in self.em_prices:
                                price_time = price[0].strftime("%Y-%m-%d %H:%M:%S")
                                if bid[0] == price_time:
                                    total_revenue += bid[1]/4 * price[1]

                if row['demand_bids'] is not None and row['demand_bids'] != 0:
                    demand_bids = row['demand_bids']
                    for bid in demand_bids:
                        received_demand_bids.append(bid.copy())
                        if bid in self.accepted_demand_bids:
                            if bid in self.clearing_bids:  # Resize clearing bid
                                bid[1] = self.clearing_quantities[self.clearing_bids.index(bid)]
                            accepted_demand_bids.append(bid)
                            for price in self.em_prices:
                                price_time = price[0].strftime("%Y-%m-%d %H:%M:%S")
                                if bid[0] == price_time:
                                    total_costs += bid[1]/4 * price[1]

                market_results.append([player_id, received_supply_bids, accepted_supply_bids,
                                       received_demand_bids, accepted_demand_bids,
                                       total_costs, total_revenue])

                self.accepted_bids[player_id] = {
                    'supply_bids': accepted_supply_bids,
                    'demand_bids': accepted_demand_bids
                }

            with open("Result/Emarket_results.csv", mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Player_id", "Received_supply_bids", "Accepted_supply_bids",
                                 "Received_demand_bids", "Accepted_demand_bids",
                                 "Total_costs", "Total_revenue"])
                writer.writerows(market_results)

            re_params = {'market_price': self.em_prices[0][1], 'market_quantity': self.em_quantities[0][1],
                         'accepted_bids': self.accepted_bids}
            self.cleared = True
            return re_params


        elif self.cleared:
            for timestamp, price in self.em_prices:
                if current_time == timestamp:
                    market_price = price
                    for quantity_timestamp, quantity in self.em_quantities:
                        if quantity_timestamp == timestamp:
                            market_quantity = quantity
                            break  # Found matching quantity, exit the loop
                    break  # Found matching timestamp, exit the loop

            if market_quantity == None:
                market_quantity = 0
            if market_price == None:
                market_price = 0

            re_params = {'market_quantity': market_quantity, 'market_price': market_price,
                         'accepted_bids': self.accepted_bids}
            return re_params
