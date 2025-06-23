import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

label_font_size = 18
tick_font_size = 14
linewidth = 2
marker_size = 30

# Generate timestamps: every 15 minutes for one month
start_time = datetime(2025, 4, 1)
end_time = datetime(2025, 5, 1)  # One full month
timestamps = pd.date_range(start=start_time, end=end_time, freq='15min')[:-1]

#Plotting params
linewidth = 2
label_font_size = 18
tick_font_size = 14
# Generate synthetic hydrogen demand (kg) for each 15-minute interval
demand = []
for ts in timestamps:
    hour = ts.hour + ts.minute / 60
    weekday = ts.weekday()
    
    if weekday < 5:
        if 6 <= hour <= 9:
            val = np.random.normal(1.0, 0.3)
        elif 10 <= hour <= 16:
            val = np.random.normal(1.5, 0.4)
        elif 17 <= hour <= 20:
            val = np.random.normal(2.0, 0.5)
        elif 21 <= hour <= 23 or 0 <= hour <= 5:
            val = np.random.normal(0.05, 0.05)
        else:
            val = np.random.normal(0.5, 0.2)
    else:
        if 8 <= hour <= 10 or 17 <= hour <= 19:
            val = np.random.normal(0.6, 0.2)
        elif 11 <= hour <= 16:
            val = np.random.normal(0.8, 0.3)
        else:
            val = np.random.normal(0.05, 0.05)

    demand.append(max(val, 0))

# Electrolyzer production (more stable, less fluctuation)
production = []
base_production_rate = 2.0  # Base steady production rate in kg

for ts in timestamps:
    hour = ts.hour + ts.minute / 60
    weekday = ts.weekday()

    if weekday < 5:
        if 6 <= hour <= 9:
            val = base_production_rate + np.random.normal(0.1, 0.05)
        elif 10 <= hour <= 16:
            val = base_production_rate + np.random.normal(0.2, 0.05)
        elif 17 <= hour <= 20:
            val = base_production_rate + np.random.normal(0.1, 0.05)
        elif 21 <= hour <= 23 or 0 <= hour <= 5:
            val = base_production_rate - np.random.normal(0.1, 0.05)
        else:
            val = base_production_rate - np.random.normal(0.05, 0.02)
    else:
        if 8 <= hour <= 10 or 17 <= hour <= 19:
            val = base_production_rate + np.random.normal(0.05, 0.02)
        elif 11 <= hour <= 16:
            val = base_production_rate + np.random.normal(0.1, 0.03)
        else:
            val = base_production_rate - np.random.normal(0.05, 0.02)

    production.append(max(val, 0))

# Scale production to meet 108% of demand
total_demand = np.sum(demand)
total_production = np.sum(production)
scaling_factor = (total_demand * 1.08) / total_production
print(scaling_factor)
production_scaled = [p * scaling_factor for p in production]

# Create DataFrames
df_demand = pd.DataFrame({'Time': timestamps, 'demand': np.round(demand, 2)})
df_production = pd.DataFrame({'Time': timestamps, 'production': np.round(production_scaled, 2)})

# Save to CSV
demand_file_name = "./examples/Lucas_folder/Illuminator_presentation/h2_gas_station_monthly_demand.csv"
production_file_name = "./examples/Lucas_folder/Illuminator_presentation/h2_production_monthly.csv"

with open(demand_file_name, "w", newline='') as f:
    f.write("Demand_data\n")
    df_demand.to_csv(f, index=False)

with open(production_file_name, "w", newline='') as f:
    f.write("Production_data\n")
    df_production.to_csv(f, index=False)

print(f"Demand saved to {demand_file_name}")
print(f"Production saved to {production_file_name}")

# Plotting
df_demand = pd.read_csv(demand_file_name, header=1, names=["Time", "demand"], parse_dates=["Time"])
df_production = pd.read_csv(production_file_name, header=1, names=["Time", "production"], parse_dates=["Time"])

plt.figure(figsize=(8, 5))
plt.plot(df_demand['Time'], df_demand['demand'], label='Demand', color='blue', linewidth=linewidth)
plt.plot(df_production['Time'], df_production['production'], label='Production', color='orange', linewidth=linewidth)
# plt.title("Hydrogen Demand and Electrolyzer Production (15-min Intervals Over 1 Month)")
plt.xlabel("Time", fontsize=label_font_size)
plt.ylabel("Hydrogen [kg]", fontsize=label_font_size)
plt.xlim(df_demand['Time'].min(), df_demand['Time'].max())
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.grid(True)
plt.legend(fontsize=tick_font_size)
plt.tight_layout()
plt.show()