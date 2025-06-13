# plot_out_csv.py

import pandas as pd
import matplotlib.pyplot as plt

# Load CSV
df_latest5 = pd.read_csv('./out_CSV.csv')

# Parse the datetime column
df_latest5['datetime'] = pd.to_datetime(df_latest5['date'], errors='coerce')

# Drop rows with unparseable datetime
df_latest5 = df_latest5.dropna(subset=['datetime'])

# Set datetime as index
df_latest5.set_index('datetime', inplace=True)

# Select columns of interest
plot_columns_latest5 = {
    'Household Demand (kW)': 'Load1-0.time-based_0-load_dem',
    'PV Generation (kW)': 'PV1-0.time-based_0-pv_gen',
    'Battery SOC (%)': 'Battery1-0.time-based_0-soc',
    'Battery Power Out (kW)': 'Battery1-0.time-based_0-p_out',
    'EV Demand (kW)': 'EV1-0.time-based_0-demand',
    'Residual Load': 'Controller1-0.time-based_0-res_load'
}

# Prepare dataframe for plotting
df_plot_latest5 = df_latest5[list(plot_columns_latest5.values())].rename(columns=plot_columns_latest5)

# Plot
plt.figure(figsize=(15, 10))

for i, (label, col) in enumerate(plot_columns_latest5.items(), 1):
    plt.subplot(len(plot_columns_latest5), 1, i)

    if label == 'Residual Load':
        # Residual Demand = - Residual Load
        residual_load = -df_plot_latest5[col] # Column is actually residual demand, so we negate it

        # Plot line in yellow/orange
        plt.plot(df_plot_latest5.index, residual_load, color='orange', linewidth=2, label='Residual Load')

        # Fill above zero
        plt.fill_between(df_plot_latest5.index, residual_load, 0,
                         where=(residual_load > 0),
                         facecolor='green', alpha=0.5, interpolate=True, label='Excess Energy')

        # Fill below zero
        plt.fill_between(df_plot_latest5.index, residual_load, 0,
                         where=(residual_load <= 0),
                         facecolor='red', alpha=0.5, interpolate=True, label='Energy from Grid')
    else:
        # All other lines: yellowish/orange
        plt.plot(df_plot_latest5.index, df_plot_latest5[col], color='orange', linewidth=2, label=label)

    plt.ylabel(label)
    plt.legend()
    plt.grid(True)


plt.tight_layout()
plt.show()
