from datetime import datetime

def match_trades(supply_offers, demand_requests) -> list:
    """
    Unknown description.
    Not used by any of the 5 test cases

    ...

    Parameters
    ----------
    supply_offers : list or dictionary (hard to tell)
        ???
    demand_requests : list or dictionary (hard to tell)
        ???

    Returns
    -------
    trades : list
        Description
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

                trades.append([request_time, request_player, offer_player, trade_quantity, trade_price])

                request_quantity -= trade_quantity
                offer_quantity -= trade_quantity

                supply_offers[supply_offers.index(best_offer)] = \
                    (offer_player, [offer_time, offer_quantity, offer_price])
            else:                                                     # No offer found for the request and exit the loop
                break

    trades.sort(key=lambda x: x[0])
    return trades


## Hard coded values defined here.
# Usage
supply_offers = [('prosumer_0', ['2012-01-01 00:00:00', 17, 4]),
                 ('prosumer_0', ['2012-01-01 00:30:00', 17, 4]),
                 ('prosumer_1', ['2012-01-01 00:30:00', 10, 2]),
                 ('prosumer_2', ['2012-01-01 00:30:00', 98, 20])]

demand_requests = [('prosumer_0', ['2012-01-01 00:15:00', 17, 4]),
                   ('prosumer_3', ['2012-01-01 00:00:00', 8, 10]),
                   ('prosumer_4', ['2012-01-01 00:30:00', 30, 50])]

trades = match_trades(supply_offers, demand_requests)
print(trades)

transactions = {}

for trade in trades:
    timestamp, request_player, offer_player, trade_quantity, trade_price = trade

    if request_player not in transactions:
        transactions[request_player] = {'sell': [], 'buy': []}

    if offer_player:
        if offer_player not in transactions:
            transactions[offer_player] = {'sell': [], 'buy': []}

        transactions[request_player]['buy'].append([timestamp, trade_quantity, trade_price])
        transactions[offer_player]['sell'].append([timestamp, trade_quantity, trade_price])

print(transactions)

total_costs = {}
total_revenue = {}

for player, transaction in transactions.items():
    total_costs[player] = sum(quantity * price for _, quantity, price in transaction['buy'])
    total_revenue[player] = sum(quantity * price for _, quantity, price in transaction['sell'])

print(total_costs)
print(total_revenue)