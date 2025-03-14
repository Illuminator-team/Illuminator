import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def create_merit_order_curve(all_bids_sorted_csv, demand, market_result_csv, date):
    # Calculate cumulative capacity
    all_bids_sorted = pd.read_csv(all_bids_sorted_csv, header = 0)
    all_bids_sorted['Cumulative Capacity (MW)'] = all_bids_sorted['Bid Capacity (MW)'].cumsum()
    market_result = pd.read_csv(market_result_csv, header = 0, index_col = 0)
    market_clearing_price = market_result.loc[date, 'Operator1-0.time-based_0-market_clearing_price']
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
    #plt.savefig("Graphics_T2/merit_order_curve.pdf", format='pdf')
    plt.show()

    return