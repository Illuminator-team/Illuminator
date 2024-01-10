import csv
class rtprice_python():

    def __init__(self):
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


    def clear(self, time, buy_price, sell_price, buy, sell):
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
