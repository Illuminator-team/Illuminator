import pandas as pd
import matplotlib.pyplot as plt

class GenerationCompanyAgent:
    def __init__(self, company, portfolio, automated_bids = True, bids_manual = None):
        self.portfolio = pd.DataFrame(portfolio)
        self.automated_bids = automated_bids
        self.bids_manual = pd.DataFrame(bids_manual)
        self.company = company

        # if the functionality is to be expanded at a later stage for example by including investment decisions, the
        # bank balance of the company could be tracked to base decisions on
        # for now the start bank_balance is 0 could be adapted by adding an initial bank balance input
        #self.bank_balance = 0

    def bid(self):
        #print("entered bid function of gen agent")
        portfolio_for_bidding = self.portfolio.copy()
        portfolio_for_bidding['Company'] = self.company
        columns = ['Company'] + portfolio_for_bidding.columns[:-1].tolist()
        portfolio_for_bidding = portfolio_for_bidding[columns]

        portfolio_for_bidding['Available Capacity (MW)'] = portfolio_for_bidding['Capacity (MW)'] * portfolio_for_bidding['Availability']

        if self.automated_bids:
            # automatic Marginal Cost Bidding
            portfolio_for_bidding['Bid Capacity (MW)'] = portfolio_for_bidding['Available Capacity (MW)']
            portfolio_for_bidding['Bid Price (€/MWh)'] = portfolio_for_bidding['Cost (€/MWh)']
        else:
            # manual bids given as input
            portfolio_for_bidding['Bid Capacity (MW)'] = self.bids_manual['Bid Capacity (MW)']
            portfolio_for_bidding['Bid Price (€/MWh)'] = self.bids_manual['Bid Price (€/MWh)']

        if sum(portfolio_for_bidding['Available Capacity (MW)']) < sum((portfolio_for_bidding['Bid Capacity (MW)'])):
            print('Warning: The bid capacity of company' + str(self.company)+' is higher than the available capacity.')
        if sum(portfolio_for_bidding['Available Capacity (MW)']) > sum((portfolio_for_bidding['Bid Capacity (MW)'])):
            print('Warning: Company' + str(self.company)+' has a higher available capacity than what was bid in the market.')

        self.bids = portfolio_for_bidding
        return {'bids' : portfolio_for_bidding}

    # profit per company is calculated by operator
    # could be implemented for multiple time steps
    #def update_revenue(self, profit):
    #    self.revenue += profit[self.company]
     #   return