import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
import numpy as np

# Function to plot Load profile of a specific day to visualize results
def plot_load_profile(load_df, day_of_year, number_houses, outputtype = 'power'):

    electricity_mix_nl = {'coal': 0.1431, 'Oil': 0.0126, 'Nuclear': 0.0342,
                          'Biofuels':0.0612, 'Waste': 0.0346, 'Hydro': 0.0004,'Natural Gas': 0.3934, 'Solar': 0.1384,
                          'Wind': 0.1778, 'Other': 0.0043}
    # source elec mix: https://www.iea.org/countries/the-netherlands/energy-mix

    #scaling of load data
    if outputtype == 'power':
        load_houses = load_df * number_houses * 15/60 #assume resolution 15 minutes
    else:
        load_houses = load_df * number_houses
    #definition of time interval
    start_time = datetime.strptime(day_of_year, "%Y-%m-%d")
    
    end_time = start_time.replace(hour=23, minute=45, second=00)

    load_doy = load_houses.loc[start_time : end_time]
    #layered plot to display different generation
    layers = []
    remaining_load = load_doy['load'].copy()
    for source_name, source_value in electricity_mix_nl.items():
        max_gen_source = source_value * load_doy['load']
        # The generation for the current source is either the source's value or the remaining load (whichever is smaller)
        source_generation = np.minimum(remaining_load, max_gen_source)
        layers.append(source_generation)

        # Subtract the current source's contribution from the remaining load
        remaining_load -= source_generation

    labels = list(electricity_mix_nl.keys())
    colors = ['brown', 'black', 'yellow', 'darkgreen', 'tomato', 'blue', 'lightgrey', 'limegreen', 'skyblue', 'bisque']

    #plt.plot(load_doy.index, load_doy['load'])
    plt.plot(load_doy.index, load_doy['load'], color='dimgrey', label='Total Load', linewidth=1)
    plt.stackplot(load_doy.index, layers, labels=labels, colors=colors)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.title(f'Load Profile for {day_of_year}')
    plt.xlabel('Time')
    plt.ylabel('Load [kW]')
    plt.grid(True)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
    return

def summarize_results(outputfile, battery_active):
    # residual load plot
    result_pd_df = pd.read_csv(outputfile, index_col=0)
    result_pd_df.index = pd.to_datetime(result_pd_df.index)
    day_of_year = result_pd_df.index[0].day
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(result_pd_df.index, result_pd_df['Controller1-0.time-based_0-res_load'],
            color='blue', linestyle='-', marker='o', markersize=4, linewidth=2, label='Residual Load (kW) ')
    ax.plot(result_pd_df.index, result_pd_df['Load1-0.time-based_0-load_dem'],
            color='red', linestyle='-', marker='o', markersize=4, linewidth=2, label='Load Demand (kW)')
    if battery_active == True:
        ax.plot(result_pd_df.index, -result_pd_df['Controller1-0.time-based_0-dump'],
                color='green', linestyle='-', marker='o', markersize=4, linewidth=2, label='Power to Grid (kW)')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))  # Show every hour
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=15))  # Minor ticks every 15 minutes
    ax.set_title(f'Residual Load {day_of_year}', fontsize=16)
    ax.set_xlabel('Time', fontsize=14)
    ax.set_ylabel('Load (kW)', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.xlim(min(result_pd_df.index), max(result_pd_df.index))
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend(loc='upper right', fontsize=12)
    plt.tight_layout()
    #plt.savefig("T1_Results_csv/load_resload.pdf", format='pdf')
    plt.show()

    # table with averages and sums for each hour
    # SOC is value after every hour, rest is sum

    results_hourly = result_pd_df.resample('H').sum()

    results_hourly = results_hourly.rename(columns={'Controller1-0.time-based_0-res_load': 'Residual Load (kW)',
                                                    'Controller1-0.time-based_0-dump': 'Power to Grid (kW)',
                                                    'PV1-0.time-based_0-pv_gen': 'PV Generation (kW)',
                                                    'Wind1-0.time-based_0-wind_gen': 'Wind Generation (kW)',
                                                    'Load1-0.time-based_0-load_dem': 'Load Demand (kW)'})

    results_hourly['Date'] = results_hourly.index.date
    results_hourly['Time'] = results_hourly.index.time

    if battery_active == True:
        results_hourly = results_hourly.rename(columns={'Controller1-0.time-based_0-flow2b': 'Power to Battery (kW)',
                                                        'Battery1-0.time-based_0-p_out': 'Output Power Battery (kW)',
                                                        'Battery1-0.time-based_0-soc': 'Battery SOC (%)', })
        hourly_soc = result_pd_df['Battery1-0.time-based_0-soc'].iloc[::4]
        results_hourly['Battery SOC (%)'] = hourly_soc
        results_hourly.drop(columns={'Output Power Battery (kW)'}, inplace=True)

        # reorder columns
        new_order_col = ['Date', 'Time', 'Load Demand (kW)', 'PV Generation (kW)', 'Wind Generation (kW)',
                         'Residual Load (kW)', 'Battery SOC (%)', 'Power to Battery (kW)', 'Power to Grid (kW)']

    else:
        # reorder columns
        new_order_col = ['Date', 'Time', 'Load Demand (kW)', 'PV Generation (kW)', 'Wind Generation (kW)',
                         'Residual Load (kW)']

    results_hourly = results_hourly[new_order_col]
    results_hourly = results_hourly.round(2)
    results_hourly = results_hourly.reset_index(drop=True)
    pd.options.display.float_format = '{:.2f}'.format

    styled_df = (results_hourly.style.set_properties(**{
        'background-color': '#f9f9f9',
        'border-color': 'black',
        'border-width': '1px',
        'border-style': 'solid',
        'color': 'black',
        'font-family': 'Arial',
        'text-align': 'center'
    })
                 .format(lambda x: f'{x:g}' if isinstance(x, float) else x)
                 .set_caption("Hourly Simulation results"))
    display(styled_df)

    return

