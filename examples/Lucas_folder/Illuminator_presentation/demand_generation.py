import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Generate timestamps: every 15 minutes for one week
start_time = datetime(2025, 4, 21)
end_time = start_time + timedelta(days=7)
timestamps = pd.date_range(start=start_time, end=end_time, freq='15min')[:-1]

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

    # Electrolyzer production varies only slightly over the day, with smooth ramps
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

    production.append(max(val, 0))  # Ensure non-negative production

# Calculate the total demand and production for scaling
total_demand = np.sum(demand)
total_production = np.sum(production)

# Calculate scaling factor to match total demand
scaling_factor = (total_demand * 1.08) / total_production

# Apply scaling to production values
production_scaled = [p * scaling_factor for p in production]

# Create DataFrame for demand and scaled production
df_demand = pd.DataFrame({
    'Time': timestamps,
    'demand': np.round(demand, 2)
})

df_production = pd.DataFrame({
    'Time': timestamps,
    'production': np.round(production_scaled, 2)
})


# Save Demand to CSV
demand_file_name = "./examples/Lucas_folder/Illuminator_presentation/h2_gas_station_weekly_demand.csv"
with open(demand_file_name, "w", newline='') as f:
    f.write("Demand_data\n")           # Custom header
    df_demand.to_csv(f, index=False)   # Writes "Time,demand" and the data

print(f"Demand saved to {demand_file_name}")

# Save Production to CSV
production_file_name = "./examples/Lucas_folder/Illuminator_presentation/h2_production.csv"
with open(production_file_name, "w", newline='') as f:
    f.write("Production_data\n")       # Custom header
    df_production.to_csv(f, index=False)  # Writes "Time,production" and the data

print(f"Production saved to {production_file_name}")

# Optionally, plot the data
df_demand = pd.read_csv(demand_file_name, header=1, names=["Time", "demand"], parse_dates=["Time"])
df_production = pd.read_csv(production_file_name, header=1, names=["Time", "production"], parse_dates=["Time"])

# Plot
plt.figure(figsize=(12, 5))
plt.plot(df_demand['Time'], df_demand['demand'], label='Demand (kg)', color='blue', linewidth=1.5)
plt.plot(df_production['Time'], df_production['production'], label='Electrolyzer Production (kg)', color='orange', linewidth=1.5)
plt.title("Hydrogen Demand and Electrolyzer Production (15-min Intervals Over 1 Week)")
plt.xlabel("Time")
plt.ylabel("Hydrogen (kg)")
plt.grid(True)
plt.tight_layout()
plt.legend()
plt.show()

