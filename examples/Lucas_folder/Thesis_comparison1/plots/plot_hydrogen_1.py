import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# Load the CSV file into a DataFrame
file_name = './examples/Lucas_folder/Thesis_comparison1/ouput_CSV.csv'
df = pd.read_csv(file_name)

# Convert the 'date' column to datetime
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Warn if any dates could not be parsed
if df['date'].isnull().any():
    print("Warning: Some 'date' entries could not be parsed.")

temp = df['CSVprod-0.time-based_0-production'] - df['H2demand-0.time-based_0-tot_dem']

# Create the figure with two subplots
# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

# --- Subplot 1: Demand and Production ---
ax1.plot(df['date'], df['H2demand-0.time-based_0-tot_dem'], label='Demand (kg)', color='blue', linewidth=2)
ax1.plot(df['date'], df['CSVprod-0.time-based_0-production'], label='Production (kg)', color='orange', linewidth=2)

ax1.set_ylabel("Hydrogen (kg)")
ax1.set_title("Hydrogen Demand and Production")
ax1.legend(loc='upper left')
ax1.grid(True)

# --- Subplot 2: SoC only ---
ax2.plot(df['date'], df['H2Buffer1-0.time-based_0-soc'], label='Buffer SOC (%)', color='red', linewidth=2, linestyle='--')
ax2.set_ylabel("Buffer SOC (%)")
ax2.set_title("Buffer State of Charge (SoC)")
ax2.legend(loc='upper left')
ax2.set_xlabel("Date")
ax2.tick_params(axis='x', rotation=45)
ax2.grid(True)

ax3.plot(df['date'], np.clip(temp, a_min= None, a_max=0))
ax3.set_xlabel("Date")
ax3.tick_params(axis='x', rotation=45)
ax3.grid(True)

# Final layout
plt.tight_layout()
plt.show()
