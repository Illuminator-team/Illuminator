import pandas as pd
from illuminator.builder import ModelConstructor
from os import makedirs
from os import path

class JusticeAgent(ModelConstructor):
    """
    Justice evaluator agent that calculates justice metrics for electricity market participants.
    
    This agent monitors market outcomes and calculates justice scores based on company market shares
    and predefined social parameters. It tracks beta scores (market shares) over time and computes
    an overall justice score at specified intervals.

    Parameters
    ----------
    social_parameters : dict
        Dictionary containing social parameter weights (a,b,c,d) for each company
    justice_step : int
        Time step at which to calculate final justice scores
    results_dir : str, optional
        Directory to save justice metric results, defaults to 'justice_agent_results'

    Inputs
    ----------
    market_results : pd.DataFrame
        Market clearing results with company capacities, revenues, costs and profits
    demand : float
        Total market demand
    market_clearing_price : float 
        Market clearing price
    
    Outputs
    ----------
    None

    States 
    -------
    beta_scores : dict
        Cumulative market shares for each company
    justice_score : float
        Overall justice metric
    alpha_scores : dict
        Social parameter weights for each company
    """

    parameters = {'social_parameters': None, # dictionary with a, b,c, d keys per company and values
                  'justice_step': None,
                  'results_dir': 'justice_agent_results'}
    inputs = {'market_results': None,
              'demand': 0,
              'marketclearingprice': 0}
    states = {  'beta_scores': {},
                'justice_score': None,
                'alpha_scores': {}}


    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.social_parameters = self.parameters['social_parameters']
        self.alpha_factors = {company: sum(params.values()) for company, params in
                              self.social_parameters.items()}
        self.justice_step = self.parameters['justice_step']
        self.beta_scores = {k: 0 for k in self.social_parameters} # creates a dictionary for the beta scores initialized to 0
        self.results_dir = self.parameters['results_dir']
        self.justice_score = 0

    def step(self, time: int, inputs: dict=None, max_advance: int=1) -> None:
        """
        Performs a single simulation time step by processing market results and calculating justice metrics.
        Parameters
        ----------
        time : int
            Current simulation time
        inputs : dict
            Dictionary containing input values including 'market_results', 'demand', and 'market_clearing_price'
        max_advance : int, optional
            Maximum time step advancement, defaults to 1
        Returns
        -------
        int
            Next simulation time step
        Notes
        -----
        The method processes market results, determines company shares, and calculates justice 
        scores at specified intervals. Results are saved to CSV files and state variables are updated.
        Market results include company data with supplied capacity, revenue, costs and profits.
        """

        input_data = self.unpack_inputs(inputs)
        market_results = input_data['market_results']
        self.market_results = pd.DataFrame(market_results)
        #market results format pd.DataFrame({'Company': [company], 'Supplied Capacity (MW)': [supplied_capacity],
                                 #   'Revenue (€)': [revenue], 'Total Costs (€)': [costs]
                                  #  ,'Profit (€)': [revenue - costs]})
        self.demand = input_data['demand'] # currently unused
        self.market_clearing_price = input_data['market_clearing_price'] # currently unused

        # always determine/update the share of each company at each point in time
        self.determine_share()

        if time == self.justice_step :
            self.calculate_justice_score()
            #print(self.beta_scores)
            beta_df = pd.DataFrame(self.beta_scores, index=[0])
            if not path.exists(self.results_dir):
                makedirs(self.results_dir)
            beta_df.to_csv(path.join(self.results_dir, f'betascores_{time}.csv'),
                                          index=False)

        self.set_states({'beta_scores': self.beta_scores, 'justice_score' : self.justice_score, 'alpha_scores': self.alpha_factors})

        return time + self._model.time_step_size

    def determine_share(self):
        """
        Calculates market share distribution based on supplied capacity of companies.
        The function calculates beta scores for each company based on their supplied capacity 
        relative to total demand. If the sum of beta scores is less than 1, the remaining share 
        is added to the company with the lowest beta score. The calculated beta scores are then 
        added to the cumulative beta scores.
        Parameters
        ----------
        None
        Returns
        -------
        None
        Notes
        -----
        Updates self.beta_scores dictionary with new cumulative beta scores for each company.
        Uses self.market_results DataFrame containing 'Company' and 'Supplied Capacity (MW)' columns.
        Uses self.demand for total market demand.
        """

        beta_scores_sum = 0
        beta_scores_t = dict.fromkeys(self.beta_scores)

        # Calculate beta scores for all companies
        for index, company in self.market_results['Company'].items():
            supplied_capacity = self.market_results['Supplied Capacity (MW)'].loc[index]
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
            #print(self.beta_scores)


    def calculate_justice_score(self):
        """
        Calculates the justice score based on alpha factors and beta scores.
        The justice score is computed as the sum of products between alpha factors
        and beta scores for each company.
        Returns
        -------
        float
            The calculated justice score, representing the weighted sum of beta scores
        """

        self.justice_score = 0
        for company in self.beta_scores.keys():
            self.justice_score += self.alpha_factors[company] * self.beta_scores[company]
        return self.justice_score