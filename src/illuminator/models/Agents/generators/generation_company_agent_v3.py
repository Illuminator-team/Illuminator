import pandas as pd
from illuminator.builder import ModelConstructor

# construct the model
class GenerationCompanyAgent(ModelConstructor):
    """
    A class to represent a Generation Company Agent.
    This class provides methods to create bids for power plants based on their specifications and market conditions.

    Attributes
    parameters : dict
        Dictionary containing company parameters such as portfolio, company name, automated bidding flag, and manual bids.
    inputs : dict
        Dictionary for potential market inputs (currently empty).
    outputs : dict
        Dictionary containing the generated bids for power plants.
    states : dict
        Dictionary containing the state variables like profit.
    time_step_size : int
        Time step size for the simulation.
    time : int or None
        Current simulation time.

    Methods
    __init__(**kwargs)
        Initializes the Generation Company Agent with the provided parameters.
    step(time, inputs, max_advance)
        Simulates one time step of the Generation Company Agent.
    bid()
        Creates bids for each power plant in the portfolio based on marginal costs or manual inputs.
    """
    # Define the model parameters, inputs, outputs...
    # all parameters will be directly available as attributes
    parameters={'company_name': 'no name',
                'automated_bids': True,
                'bids_manual': None
                }
    inputs={'portfolio': {}
            }
    outputs={
             }
    states={'bids': {},
            'profit': 0
            }

    # define other attributes
    time_step_size=1
    time=None


    def __init__(self, **kwargs) -> None:
        """
        Initialize the Generation Company Agent with the provided parameters.

        Parameters
        ----------
        kwargs : dict
            Additional keyword arguments to initialize the generation company agent,
            including portfolio of power plants, company name, automated bidding flag,
            and manual bids if applicable.
        """
        super().__init__(**kwargs)
        self.portfolio = pd.DataFrame(self.inputs['portfolio'])
        self.automated_bids = self.parameters['automated_bids']
        self.bids_manual = pd.DataFrame(self.parameters['bids_manual'])
        self.company = self.parameters['company_name']
        self.profit = self.states['profit']

        # if the functionality is to be expanded at a later stage for example by including investment decisions, the
        # bank balance of the company could be tracked to base decisions on
        # for now the start bank_balance is 0 could be adapted by adding an initial bank balance input
        #self.bank_balance = 0



    # define step function
    def step(self, time: int, inputs: dict=None, max_advance: int=1) -> None:  # step function always needs arguments self, time, inputs and max_advance. Max_advance needs an initial value.
        """
        Advances the simulation one time step.
        Args:
            time (int): Current simulation time in hours
            inputs (dict): Dictionary containing market inputs and portfolio information
            max_advance (int, optional): Maximum time to advance in hours. Defaults to 1.
        Returns:
            int: Next simulation time in hours
        """
        input_data = self.unpack_inputs(inputs)  # make input data easily accessible
        if 'portfolio' in input_data:
            self.portfolio = process_portfolio(input_data['portfolio'])

        results = self.bid()

        # self.set_outputs({})

        # bids do not represent a physical flow, so they are sent over from states
        self.set_states({'bids': results['bids'].to_dict(), 'profit': self.profit})

        # return the time of the next step (time untill current information is valid)
        return time + self._model.time_step_size


    def bid(self) -> dict:
        """
        Creates bids for each power plant in the portfolio.

        The function creates bids based on either automated marginal cost bidding
        or manual bids provided as input. For automated bidding, the bid capacity
        equals available capacity and bid price equals marginal cost. For manual
        bidding, uses pre-defined bid quantities and prices.

        Returns
        -------
        dict
            Dictionary containing:
            - bids: DataFrame with columns for Company, Capacity, Cost, Availability,
               Available Capacity, Bid Capacity and Bid Price
        """
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


def process_portfolio(data: dict) -> dict:
    """
    Process the portfolio data read from the CSV file.

    Parameters
    ----------
    data : dict
        Dictionary containing the portfolio data read from the CSV file.

    Returns
    -------
    dict
        Dictionary containing the processed portfolio data.
    """
    # process the portfolio data
    portfolio = pd.DataFrame(columns=['Capacity (MW)', 'Cost (€/MWh)', 'Availability'])
    for key, value in data.items():
        if key == 'time':
            continue
        name, attr = key.split('_')
        if attr == 'availability':
            portfolio.at[name, 'Availability'] = int(value)
        elif attr == 'capacity':
            portfolio.at[name, 'Capacity (MW)'] = float(value)
        elif attr == 'cost':
            portfolio.at[name, 'Cost (€/MWh)'] = float(value)
        else:
            raise ValueError(f'Unknown energy technology attribute: {attr}, possible attributes are capacity, cost, availability')
    
    # put the technology names as a column
    portfolio.reset_index(inplace=True)
    portfolio.rename(columns={'index': 'Technology'}, inplace=True)
    
    # Check for NaN values
    if portfolio.isna().any().any():
        raise ValueError("Missing values detected in portfolio data. Ensure all technologies have capacity, cost, and availability values.\n", portfolio)
    
    return portfolio
