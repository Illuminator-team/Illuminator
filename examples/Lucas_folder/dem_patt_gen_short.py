# Demand pattern generator for two tube trailers (1000kg @500bar)
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)
days = 7         # Simulation duration in days
resolution = 15  # Time resolution in minutes
min_h2_per_truck = 200
max_h2_per_truck = 800  # kg
h2_per_timestep = 100    # kg
max_gen_per_step = 100   # kg
fac_of_max_gen = 1       # Factor reducing max generation capacity

timesteps_tot = int(days * 24 * (60 / resolution))  # Total timesteps

# Ensure at least one overproduction and one shortage event
shortage_timestep = np.random.randint(timesteps_tot // 4, 3 * timesteps_tot // 4)
overproduction_timestep = np.random.randint(timesteps_tot // 4, 3 * timesteps_tot // 4)
while abs(shortage_timestep - overproduction_timestep) < (timesteps_tot // 6):  # Avoid them being too close
    overproduction_timestep = np.random.randint(timesteps_tot // 4, 3 * timesteps_tot // 4)

def generate_variable_generation(seed):
    """ Creates a hydrogen generation pattern with a guaranteed overproduction event. """
    np.random.seed(seed)
    generation = np.zeros(timesteps_tot)
    
    for t in range(timesteps_tot):
        if fac_of_max_gen == 1:
            generation[t] = np.random.randint(low=max_gen_per_step * 0.8, high=max_gen_per_step)  # Slight variability
        else:
            generation[t] = np.random.randint(low=(fac_of_max_gen * max_gen_per_step), high=max_gen_per_step)
    
    # Force an overproduction event
    overproduction_duration = int(3 * (60 / resolution))  # Lasts 3 hours
    generation[overproduction_timestep : overproduction_timestep + overproduction_duration] = max_gen_per_step * 1.5  # 150% production
    
    return generation

def generate_variable_demand(seed):
    """ Creates a hydrogen demand pattern with a guaranteed shortage event. """
    np.random.seed(seed)
    demand = np.zeros(timesteps_tot)
    index = 0
    
    while index < timesteps_tot:
        pause_time = np.random.randint(1, 4)  # Random idle time
        index += pause_time
        if index >= timesteps_tot:
            break
            
        h2_demand_load = np.random.randint(low=min_h2_per_truck, high=max_h2_per_truck)
        load_time = int(h2_demand_load / np.random.uniform(h2_per_timestep * 0.9, h2_per_timestep * 1.1))  # Slight variability
        new_index = min(index + load_time, timesteps_tot)
        
        demand[index:new_index] = h2_demand_load / (new_index - index)
        index = new_index
    
    # Force a shortage event
    shortage_duration = int(3 * (60 / resolution))  # Lasts 3 hours
    demand[shortage_timestep : shortage_timestep + shortage_duration] = max_gen_per_step * 1.5  # 150% demand
    
    return demand

# Generate data
generation = generate_variable_generation(41)
demand1 = generate_variable_demand(42)
demand2 = generate_variable_demand(43)

# Store in CSVs
start_datetime = datetime(2012, 1, 1, 0, 0, 0)  

time_series = [start_datetime + timedelta(minutes=15 * i) for i in range(timesteps_tot)]

# Demand 1
df1 = pd.DataFrame({ 
    'date': [dt.strftime('%Y-%m-%d %H:%M:%S') for dt in time_series],
    'demand': demand1
})
with open('./examples/h2_system_example/demand1_generated.csv', 'w', newline='') as f:
    f.write('H2demand_data1\n')
    df1.to_csv(f, index=False)

# Demand 2
df2 = pd.DataFrame({ 
    'date': [dt.strftime('%Y-%m-%d %H:%M:%S') for dt in time_series],
    'demand': demand2
})
with open('./examples/h2_system_example/demand2_generated.csv', 'w', newline='') as f:
    f.write('H2demand_data2\n')
    df2.to_csv(f, index=False)

# Thermolyzer Generation
df3 = pd.DataFrame({
    'date': [dt.strftime('%Y-%m-%d %H:%M:%S') for dt in time_series],
    'h2_gen': generation
})
with open('./examples/h2_system_example/thermolyzer_replacement_generated.csv', 'w', newline='') as f:
    f.write('Thermolyzer_data\n')
    df3.to_csv(f, index=False)

    import pandas as pd
import matplotlib.pyplot as plt

# Load CSVs
df_gen = pd.read_csv('./examples/h2_system_example/thermolyzer_replacement_generated.csv', skiprows=1)
df_demand1 = pd.read_csv('./examples/h2_system_example/demand1_generated.csv', skiprows=1)
df_demand2 = pd.read_csv('./examples/h2_system_example/demand2_generated.csv', skiprows=1)

# Convert date column to datetime
df_gen['date'] = pd.to_datetime(df_gen['date'])
df_demand1['date'] = pd.to_datetime(df_demand1['date'])
df_demand2['date'] = pd.to_datetime(df_demand2['date'])

# Plot
plt.figure(figsize=(12, 6))
plt.plot(df_gen['date'], df_gen['h2_gen'], label="Generation", color='green')
plt.plot(df_demand1['date'], df_demand1['demand'], label="Demand 1", linestyle='dashed', color='blue')
plt.plot(df_demand2['date'], df_demand2['demand'], label="Demand 2", linestyle='dashed', color='red')

# Formatting
plt.xlabel("Time")
plt.ylabel("Hydrogen (kg)")
plt.title("Hydrogen Generation and Demand Over Time")
plt.legend()
plt.xticks(rotation=45)
plt.grid()

# Show plot
plt.tight_layout()
plt.show()