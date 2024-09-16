import matplotlib.pyplot as plt
import numpy as np
import datetime
from initial_bids import *
from typing import Union


def find_accepted_bids(sorted_supply_bids, sorted_demand_bids, num_s_bid, num_d_bid) -> tuple:
    """
    Unknown description.
    Not used by any of the 5 test cases

    ...

    Parameters
    ----------
    sorted_supply_bids : ???
        ???
    sorted_demand_bids : ???
        ???
    num_s_bid : ???
        ???
    num_d_bid : ???
        ???

    Returns
    -------
    tuple
        Contains the lists of accepted supply and demand bids
    """
    accepted_supply_bids = []
    for i in range(num_s_bid+1):
        accepted_supply_bids.append(sorted_supply_bids[i])

    accepted_demand_bids = []
    for i in range(num_d_bid+1):
        accepted_demand_bids.append(sorted_demand_bids[i])

    return accepted_supply_bids, accepted_demand_bids

def clear(date_time, supply_bids, demand_bids) -> Union[None,tuple]:
    """
    Unknown description.
    Not used by any of the 5 test cases


    ...

    Parameters
    ----------
    date_time : ???
        ???
    supply_bids : ???
        ???
    demand_bids : ???
        ???
    
    Returns
    -------
    None or tuple
        ???
    """
    supply_bids_for_date_time = [bid for bid in supply_bids if bid[0] == date_time]
    demand_bids_for_date_time = [bid for bid in demand_bids if bid[0] == date_time]

    # Sort bids by price
    supply_bids_for_date_time.sort(key=lambda x: x[2])
    demand_bids_for_date_time.sort(key=lambda x: x[2], reverse=True)

    if not supply_bids_for_date_time or not demand_bids_for_date_time:
        return None,None,None,None

    # Calculate cumulative quantities
    supply_quantity = np.cumsum([bid[1] for bid in supply_bids_for_date_time])
    demand_quantity = np.cumsum([bid[1] for bid in demand_bids_for_date_time])
    supply_price = [bid[2] for bid in supply_bids_for_date_time]
    demand_price = [bid[2] for bid in demand_bids_for_date_time]

    y_s = [supply_bids_for_date_time[0][2]] + [bid[2] for bid in supply_bids_for_date_time[1:]] + [
        supply_bids_for_date_time[-1][2]]

    # Plot supply curve
    plt.step([0] + supply_quantity.tolist(), y_s, label='Supply', where='post')


    y_d = [demand_bids_for_date_time[0][2]] + [bid[2] for bid in demand_bids_for_date_time[1:]] + [
        demand_bids_for_date_time[-1][2]]
    # Plot demand curve
    plt.step([0] + demand_quantity.tolist(), y_d, label='Demand', where='post')

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

    market_quantity = None
    market_price = None
    clearing_quantity = None
    clearing_bid = None

    if points_s[0][1] > points_d[0][1]:                                              # Supply price >  demand price at 0
        return market_quantity, market_price, clearing_bid, clearing_quantity

    s_bid = -1
    for i in range(len(points_s) - 1):
        x1, y1 = points_s[i]
        x2, y2 = points_s[i + 1]

        if x1 == x2:                                                                  # Vertical segment in supply curve
            d_bid = 0
            for j in range(len(points_d) - 1):
                x3, y3 = points_d[j]
                x4, y4 = points_d[j + 1]
                if y3 == y4:
                    if x3 <= x1 <= x4 and y1 <= y3 <= y2:                           # Horizontal segment in demand curve
                        market_quantity = x1
                        market_price = y3
                        clearing_bid = demand_bids_for_date_time[d_bid]
                        clearing_quantity = x1 - x3
                        accepted_supply_bids, accepted_demand_bid =\
                            find_accepted_bids(supply_bids_for_date_time, demand_bids_for_date_time, s_bid, d_bid)
                        print(clearing_bid)
                        print('Price: ' + str(market_price) + '\n')
                        print('Quantity: ' + str(market_quantity) + '\n')
                        print('Clearing Quantity: ' + str(clearing_quantity) + '\n')
                        print('S bid ' + str(s_bid) + '\n')
                        print('D bid ' + str(d_bid) + '\n')
                        print('Accepted supply bids ' + str(accepted_supply_bids))
                        print('Accepted demand bids ' + str(accepted_demand_bid))
                        return market_quantity, market_price, clearing_bid, clearing_quantity
                    d_bid += 1

        elif y1 == y2:                                                              # Horizontal segment in supply curve
            s_bid += 1
            d_bid = -1
            for j in range(len(points_d) - 1):
                x3, y3 = points_d[j]
                x4, y4 = points_d[j + 1]
                if x3 == x4 and (x1 <= x3 <= x2 and y4 <= y1 <= y3):                  # Vertical segment in demand curve
                    market_quantity = x3
                    market_price = y1
                    clearing_bid = supply_bids_for_date_time[s_bid]
                    clearing_quantity = x3 - x1
                    accepted_supply_bids, accepted_demand_bid = \
                        find_accepted_bids(supply_bids_for_date_time, demand_bids_for_date_time, s_bid, d_bid)
                    print(clearing_bid)
                    print('Price: ' + str(market_price) + '\n')
                    print('Quantity: ' + str(market_quantity) + '\n')
                    print('Clearing Quantity: ' + str(clearing_quantity) + '\n')
                    print('S bid ' + str(s_bid) + '\n')
                    print('D bid ' + str(d_bid) + '\n')
                    print('Accepted supply bids' + str(accepted_supply_bids))
                    print('Accepted demand bids' + str(accepted_demand_bid))
                    return market_quantity, market_price, clearing_bid, clearing_quantity
                if y3 == y4:
                    d_bid += 1
    # No intersection
    s_bid = 0
    d_bid = 0
    if points_d[-1][0] > points_s[-1][0]:
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
                    accepted_supply_bids, accepted_demand_bid = \
                        find_accepted_bids(supply_bids_for_date_time, demand_bids_for_date_time, s_bid, d_bid)
                    print(clearing_bid)
                    print('Price: ' + str(market_price) + '\n')
                    print('Quantity: ' + str(market_quantity) + '\n')
                    print('Clearing Quantity: ' + str(clearing_quantity) + '\n')
                    print('S bid ' + str(s_bid) + '\n')
                    print('D bid ' + str(d_bid) + '\n')
                    print('Accepted supply bids ' + str(accepted_supply_bids))
                    print('Accepted demand bids ' + str(accepted_demand_bid))
                    return market_quantity, market_price, clearing_bid, clearing_quantity
                d_bid += 1
    else:
        d_bid = len(demand_bids_for_date_time) -1
        for i in range(len(points_s) - 1):
            x3, y3 = points_s[i]
            x4, y4 = points_s[i+1]
            if y3 == y4:
                if x3 < points_d[-1][0] < x4:
                    market_price = (points_d[-1][1] + y3) / 2
                    market_quantity = points_d[-1][0]
                    clearing_bid = supply_bids_for_date_time[s_bid]
                    clearing_quantity = points_d[-1][0] - x3
                    accepted_supply_bids, accepted_demand_bid = \
                        find_accepted_bids(supply_bids_for_date_time, demand_bids_for_date_time, s_bid, d_bid)
                    print(clearing_bid)
                    print('Price: ' + str(market_price) + '\n')
                    print('Quantity: ' + str(market_quantity) + '\n')
                    print('Clearing Quantity: ' + str(clearing_quantity) + '\n')
                    print('S bid ' + str(s_bid) + '\n')
                    print('D bid ' + str(d_bid) + '\n')
                    print('Accepted supply bids ' + str(accepted_supply_bids))
                    print('Accepted demand bids ' + str(accepted_demand_bid))
                    return market_quantity, market_price, clearing_bid, clearing_quantity
                s_bid += 1




def plot_bids(date_time) -> None:
    """
    Filter bids for the chosen date and time and creates a plot.
    Not used by any of the 5 test cases

    ...

    Parameters
    ----------
    date_time : ???
        ???
    """
    # Filter bids for the chosen date and time

    market_quantity, market_price, clearing_bid, clearing_quantity =\
        clear(date_time, initial_supply_bids, initial_demand_bids)

    if market_quantity is not None:
        plt.axvline(market_quantity, color='blue', linestyle='dashed', label='Market Quantity')

    if market_price is not None:
        plt.axhline(market_price, color='red', linestyle='dashed', label='Market Clearing Price')

    plt.xlabel('MW')
    plt.ylabel('€/MWh')
    plt.title(f'Supply and Demand Bids on {date_time}')
    plt.legend()
    plt.tight_layout()
    plt.show()


# # # # Call the function with the date and time you're interested in
plot_bids('2012-04-15 17:30:00')

# # Define the start and end timestamps
# start_timestamp = datetime.datetime(2012, 4, 15, 1, 30, 0)
# end_timestamp = datetime.datetime(2012, 4, 16, 23, 0, 0)

# # Iterate over each hour of the day
# current_timestamp = start_timestamp
# while current_timestamp <= end_timestamp:
#     plot_bids(current_timestamp.strftime("%Y-%m-%d %H:%M:%S"))
#     current_timestamp += datetime.timedelta(minutes=15)

