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

