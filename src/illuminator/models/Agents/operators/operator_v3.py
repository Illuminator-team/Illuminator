from os import path
import pandas as pd
import matplotlib.pyplot as plt
from numpy import linspace
# import seaborn as sns
from illuminator.builder import ModelConstructor
from os import makedirs

# construct the model
class Operator_Market(ModelConstructor):
    """
    A class to represent a Market Operator Agent that clears electricity markets.
    This class manages bid processing, price formation, and market clearing calculations.

    Attributes
    ----------
    parameters : dict
        Dictionary containing market parameters such as demand and results directory.
    inputs : dict
        Dictionary containing submitted bids from electricity generators.
    outputs : dict
        Dictionary containing market clearing prices and results per company.
    states : dict
        Dictionary containing state variables like market clearing price.
    time_step_size : int
        Time step size for the simulation in hours.
    time : int or None
        Current simulation time in hours.

    Methods
    -------
    __init__(**kwargs)
        Initializes the Market Operator with the provided parameters.
    step(time, inputs, max_advance)
        Advances simulation by processing bids and calculating market results.
    calculate_balance(bids)
        Determines market clearing price and financial results from submitted bids.
    create_merit_order_curve(all_bids_sorted, demand, market_clearing_price)
        Visualizes merit order curve showing price formation.
    """
    # Define the model parameters, inputs, outputs...
    # all parameters will be directly available as attributes
    parameters={'demand': {}, # to add later 'overbid_penalty'
                'results_dir': 'operator_results'
                }
    inputs={'bids': {} # to add later 'overbid'
            }
    outputs={
             }
    states={'market_clearing_price': 0,
            }

    # define other attributes
    time_step_size=1
    time=None


    def __init__(self, **kwargs) -> None:
        """
        Initialize the Market Operator with provided parameters.

        Parameters
        ----------
        kwargs : dict
            Additional keyword arguments to initialize the market operator,
            including demand values and other market parameters.
        """
        super().__init__(**kwargs)
        self.demand = self.parameters['demand']
        self.results_dir = self.parameters['results_dir']




    # define step function
    def step(self, time: int, inputs: dict=None, max_advance: int=1) -> None:  # step function always needs arguments self, time, inputs and max_advance. Max_advance needs an initial value.
        """
        Advances the simulation one time step, processes bids, calculates market clearing 
        results and stores state information.

        Parameters
        ----------
        time : int
            Current simulation time in hours
        inputs : dict
            Dictionary containing submitted bids from generators with bid prices and capacities
        max_advance : int, optional
            Maximum time to advance in hours. Defaults to 1.

        Returns
        -------
        int
            Next simulation time step in hours, calculated as current time plus time_step_size
        """
        input_data = self.unpack_inputs(inputs)  # make input data easily accessible

        if isinstance(input_data['bids'], dict): # if only one bid is submitted
            bids = [pd.DataFrame(input_data['bids'])]
        else:
            bids = [pd.DataFrame(bid) for bid in input_data['bids']]

        results = self.calculate_balance(bids)
        all_bids_sorted = results['all_bids_sorted']
        market_clearing_price = results['market_clearing_price']

        # save the all_bids_sorted dataframe to a csv file
        # Create results directory if it doesn't exist
        if not path.exists(self.results_dir):
            makedirs(self.results_dir)
        all_bids_sorted.to_csv(path.join(self.results_dir, f'all_bids_sorted_{time}.csv'), index=False)

        #create merit order curve
        #self.create_merit_order_curve(all_bids_sorted, self.demand, market_clearing_price)

        self.set_states({'market_clearing_price': float(market_clearing_price)})  # json serialize needs to be a normal datatype, not a numpy data type
        #self.set_states(market_clearing_price=market_clearing_price)

        # return the time of the next step (time untill current information is valid)
        return time + self._model.time_step_size


    def calculate_balance(self, bids):
        """
        Calculates market clearing price and generates results based on submitted bids.

        The function processes all bids to determine the market clearing price based on
        the merit order, calculates accepted capacities, and computes financial results
        for each company including revenue, costs, and profits. It also triggers the
        creation of a merit order curve visualization.

        Parameters
        ----------
        bids : list
            List of DataFrames containing bid information from each company

        Returns
        -------
        dict
            Dictionary containing:
            - market_clearing_price: float representing the cleared market price
            - results: DataFrame with company-wise financial and operational results
        """
        # in this function the clearing price is calculated based on all submitted bids.
        # Additionally, a Merit Order graph is created (see external function create_merit_order_curve)
        all_bids = pd.concat(bids, ignore_index=True)
        #all_bids = bids

        all_bids_sorted = all_bids.sort_values(by='Bid Price (€/MWh)', ascending=True, ignore_index=True)

        total_supplied = 0
        market_clearing_price = 0

        # dataframe that only includes accepted bids for easier calculation of results
        accepted_bids = pd.DataFrame(columns=all_bids_sorted.columns)
        supplied_cap = []
        # Calculation Market Clearing Price
        for i in range(0, len(all_bids_sorted)):
            if total_supplied < self.demand:
                if total_supplied + all_bids_sorted.iloc[i]['Bid Capacity (MW)'] <= self.demand:
                    total_supplied = total_supplied + all_bids_sorted.iloc[i]['Bid Capacity (MW)']
                    bid_to_add = all_bids_sorted.loc[[i]]
                    accepted_bids = pd.concat([accepted_bids, bid_to_add])
                else:
                    remaining_capacity = self.demand - total_supplied
                    total_supplied += remaining_capacity
                    market_clearing_price = all_bids_sorted.iloc[i]['Bid Price (€/MWh)']
                    bid_to_add = all_bids_sorted.loc[[i]]
                    bid_to_add['Bid Capacity (MW)'] = remaining_capacity
                    accepted_bids = pd.concat([accepted_bids, bid_to_add])
                    break

        #print(accepted_bids)

        results_df = pd.DataFrame(
            columns=['Company', 'Supplied Capacity (MW)', 'Revenue (€)', 'Total Costs (€)', 'Profit (€)'])

        for bid in bids:
            company = bid['Company'].iloc[0]
            df_company = all_bids[all_bids['Company'] == company]
            df_company_sorted = df_company.sort_values(by='Bid Price (€/MWh)', ascending=True, ignore_index=True)
            df_company_accepted = accepted_bids[accepted_bids['Company'] == company]
            df_company_extra = df_company_sorted[~df_company_sorted['Technology'].isin(df_company_accepted['Technology'])]
            bid_capacity = df_company_accepted['Bid Capacity (MW)'].sum()
            supplied_capacity = 0
            # for each MWh a company overbids, a penalty must be paid to acquire the missing capacity on the Balancing Market
            #overbid = max(0, bid_capacity - supplied_capacity)
            #penalty = overbid * self.overbid_penalty
            # the companies get paid based on the capacity they bid and the market price
            revenue = market_clearing_price * df_company_accepted['Bid Capacity (MW)'].sum()
            costs = 0
            for i in range(0, len(df_company_accepted)):
                supplied_per_plant = min(df_company_accepted.iloc[i]['Available Capacity (MW)'],
                                         df_company_accepted.iloc[i]['Bid Capacity (MW)'])
                cost_per_plant = supplied_per_plant * df_company_accepted.iloc[i]['Cost (€/MWh)']
                costs += cost_per_plant
                supplied_capacity += supplied_per_plant

            if supplied_capacity < bid_capacity:
                for i in range(0, len(df_company_extra)):
                    extra_supply = bid_capacity - supplied_capacity
                    if extra_supply > 0:
                        added_supply = min(extra_supply, df_company_extra.iloc[i]['Available Capacity (MW)'])
                        supplied_capacity =+ added_supply
                        costs += added_supply * df_company_extra.iloc[i]['Cost (€/MWh)']


            new_row = pd.DataFrame({'Company': [company], 'Supplied Capacity (MW)': [supplied_capacity],
                                    'Revenue (€)': [revenue], 'Total Costs (€)': [costs]
                                    ,'Profit (€)': [revenue - costs]}) # to add later'Costs for Overbidding (€)': [penalty]
            results_df = pd.concat([results_df, new_row])

        # Show Market Clearing Results
        print(f"Market Clearing Price: {market_clearing_price} €/MWh")

        print(results_df)

        
        return {'market_clearing_price' : market_clearing_price, 'all_bids_sorted' : all_bids_sorted}


    def create_merit_order_curve(self, all_bids_sorted, demand, market_clearing_price):
        """
        Creates a merit order curve plot based on sorted bids and market clearing results.

        The function visualizes the merit order by plotting each bid as a bar segment,
        showing the cumulative generation capacity against bid prices. The plot includes
        annotations for technologies, market clearing price lines, and company legend.

        Parameters
        ----------
        all_bids_sorted : pandas.DataFrame
            Sorted DataFrame containing bid information including capacity and prices
        demand : float
            Total market demand in MW
        market_clearing_price : float
            Cleared market price in €/MWh

        Returns
        -------
        None
            Displays the merit order curve plot
        """
        # Calculate cumulative capacity
        all_bids_sorted['Cumulative Capacity (MW)'] = all_bids_sorted['Bid Capacity (MW)'].cumsum()

        companies = all_bids_sorted['Company'].unique().tolist()
        # colors = sns.color_palette("Set1", len(companies))
        colors = plt.cm.Set1(linspace(0, 1, len(companies)))
        company_colors = {company: color for company, color in zip(companies, colors)}

        # Prepare data for plotting
        capacity = all_bids_sorted['Cumulative Capacity (MW)']
        bids = all_bids_sorted['Bid Price (€/MWh)']

        # Create the merit order curve
        fig, ax = plt.subplots(figsize=(10, 6))

        # Initialize previous capacity and cost
        previous_capacity = 0

        # Plot the stair-step curve
        for index, row in all_bids_sorted.iterrows():
            current_capacity = previous_capacity + row['Available Capacity (MW)']
            current_cost = row['Bid Price (€/MWh)']

            ax.bar(x=previous_capacity, height=current_cost, width=row['Available Capacity (MW)'], align='edge',
                   color=company_colors[row['Company']])
            # ax.bar(x=previous_capacity, height=current_cost, width=row['Available Capacity (MW)'], align='edge')

            # Annotate with technology name
            ax.text((previous_capacity + current_capacity) / 2, current_cost + 2,
                    row['Technology'], ha='center', color='black')

            # Update previous capacity
            previous_capacity = current_capacity

        # Final horizontal line to close the curve
        ax.step([previous_capacity, previous_capacity], [0, 0], where='post', color='gray', linewidth=2)

        ax.set_title('Merit Order Curve')
        ax.set_xlabel('Cumulative Generation (MWh)')
        ax.set_ylabel('Bid Price (€/MWh)')
        ax.grid()
        plt.xlim(0, all_bids_sorted['Cumulative Capacity (MW)'].max() * 1.1)
        plt.ylim(40, all_bids_sorted['Bid Price (€/MWh)'].max() * 1.1)
        ax.plot([0, demand], [market_clearing_price, market_clearing_price], color='red', linestyle='--',
                label='Market Clearing')
        ax.plot([demand, demand], [0, market_clearing_price], color='red', linestyle='--')
        ax.axhline(0, color='black', linewidth=0.5, ls='--')
        ax.axvline(0, color='black', linewidth=0.5, ls='--')

        ax.legend(title='Companies',
                  handles=[plt.Line2D([0], [0], color=color, lw=4) for color in company_colors.values()],
                  labels=company_colors.keys())
        # ax.legend(title='Companies')
        plt.tight_layout()
        plt.show()
        # plt.show(block=False)

        return