import pandas as pd
from illuminator.builder import ModelConstructor

class JusticeAgent(ModelConstructor):
    parameters = {'social_parameters': None, # dictionary with a, b,c, d keys per company and values
                  'justice_step': None}
    inputs = {'market_results': None,
              'demand': 0,
              'marketclearingprice': 0}
    outputs = {'justice_score': None,
               'alpha_scores': {}
               }
    states = {'beta_scores': {}}

    """
       A class to represent a Justice Agent.
       This class provides methods to create bids for power plants based on their specifications and market conditions.

       Attributes

       Methods
       __init__(**kwargs)

       step()
        Simulates one time step of the Justice Agent.
       """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.social_parameters = self.parameters['social_parameters']
        self.alpha_factors = {company: sum(params.values()) for company, params in
                              self.social_parameters.items()}
        self.justice_step = self.parameters['justice_step']
        self.beta_scores = dict.fromkeys(self.social_parameters) # creates a dictionary for the beta scores

    def step(self, time: int, inputs: dict=None, max_advance: int=1) -> None:

        input_data = self.unpack_inputs(inputs)
        self.market_results = input_data['market_results']
        #market results format pd.DataFrame({'Company': [company], 'Supplied Capacity (MW)': [supplied_capacity],
                                 #   'Revenue (€)': [revenue], 'Total Costs (€)': [costs]
                                  #  ,'Profit (€)': [revenue - costs]})
        self.demand = input_data['demand'] # currently unused
        self.market_clearing_price = input_data['market_clearing_price'] # currently unused

        # always determine/update the share of each company at each point in time
        determine_share(self)

        if time % self.justice_step == 0:
            calculate_justice_score(self)

        return time + self._model.time_step_size

    def determine_share(self):
        beta_scores_sum = 0
        beta_scores_t = dict.fromkeys(self.beta_scores)

        # Calculate beta scores for all companies
        for index, company in self.market_results['Company'].items():
            supplied_capacity = self.market_results['Company'].loc[index,'Supplied Capacity (MW)']
            beta_scores_t[company] = supplied_capacity/self.demand
            beta_scores_sum += beta_scores_t[company]

        beta_sum =sum(beta_scores_t.values())

        if (beta_sum < 1):
            min_key = min(beta_scores_t, key=beta_scores_t.get)
            beta_min = beta_scores_t[min_key]
            rest = 1 - beta_sum
            beta_scores_t[min_key] += rest

        # add beta at t to overall beta
        for key in self.beta_scores.keys():
            self.beta_scores[key] += beta_scores_t[key]


    def calculate_justice_score(self):
        self.justice_score = 0
        for company in self.beta_scores.keys():
            self.justice_score += self.alpha_factors[company] * self.beta_scores[company]
        return self.justice_score