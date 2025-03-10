# Demand pattern generator for two tube trailers (1000kg @500bar)
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)
days = 30       # days
resolution = 15 # min
min_h2_per_truck = 200
max_h2_per_truck = 800   #kg
h2_per_timestep = 80 # kg

# truck_arivals_day = 3
# truck_arrivals_month = truck_arivals_day * days


# h2_per_timestep = m_h2_per_truck / (4 * refuel_time)
timesteps_tot = int(30 * 24 * (60/15))

# demand1 = np.zeros(timesteps_tot)
# demand2 = np.zeros(timesteps_tot)

def random_demand(seed):
    np.random.seed(seed)
    demand = np.zeros(timesteps_tot)
    index = 0
    for timestep in range(timesteps_tot):
        if timestep == index:
        
        # if index >- timesteps_tot:
        #     break
            pause_time = np.random.randint(0, 4)
            index += pause_time
            h2_demand_load = np.random.randint(low=min_h2_per_truck, high=max_h2_per_truck)
            load_time = int(h2_demand_load / 80)
            new_index = index + load_time
            demand[index:new_index] = h2_demand_load / load_time
            index = new_index
    return demand

demand1 = random_demand(42)
demand2 = random_demand(43)
# Store in CSV

start_datetime = datetime(2012, 1, 1, 0, 0, 0)  # Start from March 10, 2025, 00:00

time_series = [start_datetime + timedelta(minutes=15 * i) for i in range(timesteps_tot)]
df1 = pd.DataFrame({ 
    'date': [dt.strftime('%Y-%m-%d %H:%M:%S') for dt in time_series],
    'demand': demand1
})
df1.to_csv('.\examples\h2_system_example\demand1_generated_month.csv', index=False)
df2 = pd.DataFrame({ 
    'date': [dt.strftime('%Y-%m-%d %H:%M:%S') for dt in time_series],
    'demand': demand2
})
df2.to_csv('.\examples\h2_system_example\demand2_generated_month.csv', index=False)







