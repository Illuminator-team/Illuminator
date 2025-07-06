import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os 

plot_saving_dir = 'C:/Users/31633/Dropbox/My PC (DESKTOP-84P3QQD)/Documents/Master_thesis/Thesis_figures/Results/Scenario1'
figs = []
label_font_size = 18
tick_font_size = 14
linewidth = 2
marker_size = 30

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
fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

# --- Subplot 1: Demand and Production ---
ax1.plot(df['date'], df['H2demand-0.time-based_0-tot_dem'], label='Demand (kg)', color='blue', linewidth=linewidth)
ax1.plot(df['date'], df['CSVprod-0.time-based_0-production'], label='Production (kg)', color='orange', linewidth=linewidth)

ax1.set_ylabel("Hydrogen (kg)", fontsize=label_font_size)
ax1.tick_params(axis='y', labelsize=tick_font_size)
# ax1.set_title("Hydrogen Demand and Production")
ax1.legend(loc='upper left')
ax1.grid(True)

# --- Subplot 2: SoC only ---
ax2.plot(df['date'], df['H2Buffer1-0.time-based_0-soc'], label='Buffer SOC (%)', color='black', linewidth=linewidth, linestyle='--')
ax2.set_ylabel("Buffer SOC (%)", fontsize=label_font_size)
ax2.set_ylim(0, 100)  # Set y-axis limits for SOC
# ax2.set_title("Buffer State of Charge (SoC)")
# ax2.legend(loc='upper left')
ax2.set_xlabel("Date")
ax2.tick_params(axis='x', rotation=45, labelsize=tick_font_size)
ax2.tick_params(axis='y', labelsize=tick_font_size)
ax2.grid(True)
# Final layout
plt.tight_layout()
figs.append((fig1, 'unoptimized_h.png'))



file_name = './examples/Lucas_folder/Thesis_comparison1/ouput_CSV_opt.csv'
df = pd.read_csv(file_name)

# Convert the 'date' column to datetime
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Warn if any dates could not be parsed
if df['date'].isnull().any():
    print("Warning: Some 'date' entries could not be parsed.")

temp = df['CSVprod-0.time-based_0-production'] - df['H2demand-0.time-based_0-tot_dem']

# Create the figure with two subplots
# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

# --- Subplot 1: Demand and Production ---
ax1.plot(df['date'], df['H2demand-0.time-based_0-tot_dem'], label='Demand (kg)', color='blue', linewidth=linewidth)
ax1.plot(df['date'], df['CSVprod-0.time-based_0-production'], label='Production (kg)', color='orange', linewidth=linewidth)

ax1.set_ylabel("Hydrogen (kg)", fontsize=label_font_size)
ax1.tick_params(axis='y', labelsize=tick_font_size)
# ax1.set_title("Hydrogen Demand and Production")
ax1.legend(loc='upper left')
ax1.grid(True)

# --- Subplot 2: SoC only ---
ax2.plot(df['date'], df['H2Buffer1-0.time-based_0-soc'], label='Buffer SOC (%)', color='black', linewidth=linewidth, linestyle='--')
ax2.set_ylabel("Buffer SOC (%)", fontsize=label_font_size)
ax2.set_ylim(0, 100)  # Set y-axis limits for SOC
# ax2.set_title("Buffer State of Charge (SoC)")
# ax2.legend(loc='upper left')
ax2.set_xlabel("Date")
ax2.tick_params(axis='x', rotation=45, labelsize=tick_font_size)
ax2.tick_params(axis='y', labelsize=tick_font_size)
ax2.grid(True)
# Final layout
plt.tight_layout()
figs.append((fig2, 'optimized_h.png'))



plt.show()


save_all = input(f"Save all plots to {plot_saving_dir}? (y/n)").strip().lower() == 'y'
if save_all:
    os.makedirs(plot_saving_dir, exist_ok=True)

    for fig, ffilename in figs:
        path = os.path.join(plot_saving_dir, ffilename)
        fig.savefig(path, dpi=300)
        print(f"Saved {fig} as {ffilename}")