import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

class Operator_Market:
    def __init__(self, demand, companies):
        self.demand = demand
        self.companies = companies #all participating companies
        #self.overbid_penalty = overbid_penalty

    def calculate_balance(self, bids):
        # in this function the clearing price is calculated based on all submitted bids.
        # Additionally, a Merit Order graph is created (see external function create_merit_order_curve)
        all_bids = pd.concat(bids, ignore_index=True)

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

        for company in self.companies:
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

        #create merit order curve
        self.create_merit_order_curve(all_bids_sorted, self.demand, market_clearing_price)
        return {'market_clearing_price' : market_clearing_price, 'results' : results_df}

    def create_merit_order_curve(self, all_bids_sorted, demand, market_clearing_price):

        # Calculate cumulative capacity
        all_bids_sorted['Cumulative Capacity (MW)'] = all_bids_sorted['Bid Capacity (MW)'].cumsum()

        companies = all_bids_sorted['Company'].unique().tolist()
        colors = sns.color_palette("Set1", len(companies))
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
        plt.tight_layout()
        plt.show()

        return