import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os 
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset
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
ax1.plot(df['date'], df['H2demand-0.time-based_0-tot_dem'], label='Demand [kg]', color='blue', linewidth=linewidth)
ax1.plot(df['date'], df['CSVprod-0.time-based_0-production'], label='Production [kg]', color='orange', linewidth=linewidth)

ax1.set_ylabel("Hydrogen [kg]", fontsize=label_font_size)
ax1.tick_params(axis='y', labelsize=tick_font_size)
# ax1.set_title("Hydrogen Demand and Production")
ax1.legend(loc='upper left')
ax1.grid(True)

# --- Subplot 2: SoC only ---
ax2.plot(df['date'], df['H2Buffer1-0.time-based_0-soc'], label='Buffer SOC [%]', color='black', linewidth=linewidth)
ax2.set_ylabel("Buffer SOC [%]", fontsize=label_font_size)
ax2.set_ylim(0, 100)  # Set y-axis limits for SOC
# ax2.set_title("Buffer State of Charge (SoC)")
# ax2.legend(loc='upper left')
start = pd.to_datetime("2025-04-01")
end = pd.to_datetime("2025-04-30")
ax2.set_xlim(left=pd.to_datetime("2025-04-01"), right=pd.to_datetime("2025-05-01"))
ax2.set_xlabel("Date", fontsize=label_font_size)
tick_dates = pd.date_range(start, end, freq="5D")
ax2.set_xticks(tick_dates, tick_dates.strftime('%Y-%m-%d'), rotation=45, ha='right', fontsize=tick_font_size)
ax2.tick_params(axis='x', rotation=45, labelsize=tick_font_size)
ax2.tick_params(axis='y', labelsize=tick_font_size)
ax2.grid(True)
# Final layout
plt.tight_layout()
figs.append((fig1, 'unoptimized_h.png'))


fig_unop_single = plt.figure(figsize=(10, 5))
plt.plot(df['date'], df['H2Buffer1-0.time-based_0-soc'], label='Buffer SOC [%]', color='black', linewidth=linewidth)
plt.ylabel("Buffer SOC [%]", fontsize=label_font_size)
plt.ylim(0, 100)  # Set y-axis limits for SOC
start = pd.to_datetime("2025-04-01")
end = pd.to_datetime("2025-04-30")
plt.xlim(left=pd.to_datetime("2025-04-01"), right=pd.to_datetime("2025-05-01"))
# Extend limits by 0.5 day on each side


# Define tick locations (e.g. every 5 days) and labels
tick_dates = pd.date_range(start, end, freq="5D")
plt.xticks(tick_dates, tick_dates.strftime('%Y-%m-%d'), rotation=45, ha='right', fontsize=tick_font_size)

plt.xlabel("Date", fontsize=label_font_size)
plt.tick_params(axis='x', rotation=45, labelsize=tick_font_size)
plt.tick_params(axis='y', labelsize=tick_font_size)
plt.grid(True)
# Final layout
plt.tight_layout()
figs.append((fig_unop_single, 'unoptimized_h_single.png'))

file_name = './examples/Lucas_folder/Thesis_comparison1/ouput_CSV_opt.csv'
df_o = pd.read_csv(file_name)

# Convert the 'date' column to datetime
df_o['date'] = pd.to_datetime(df['date'], errors='coerce')

# Warn if any dates could not be parsed
if df_o['date'].isnull().any():
    print("Warning: Some 'date' entries could not be parsed.")

temp = df['CSVprod-0.time-based_0-production'] - df['H2demand-0.time-based_0-tot_dem']

# Create the figure with two subplots
# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

# --- Subplot 1: Demand and Production ---
ax1.plot(df_o['date'], df_o['H2demand-0.time-based_0-tot_dem'], label='Demand [kg]', color='blue', linewidth=linewidth)
ax1.plot(df_o['date'], df_o['CSVprod-0.time-based_0-production'], label='Production [kg]', color='orange', linewidth=linewidth)

ax1.set_ylabel("Hydrogen [kg]", fontsize=label_font_size)
ax1.tick_params(axis='y', labelsize=tick_font_size)
# ax1.set_title("Hydrogen Demand and Production")
ax1.legend(loc='upper left')
ax1.grid(True)

# --- Subplot 2: SoC only ---
ax2.plot(df_o['date'], df_o['H2Buffer1-0.time-based_0-soc'], label='Buffer SOC [%]', color='black', linewidth=linewidth)
ax2.set_ylabel("Buffer SOC [%]", fontsize=label_font_size)
ax2.set_ylim(0, 100)  # Set y-axis limits for SOC
# ax2.set_title("Buffer State of Charge (SoC)")
# ax2.legend(loc='upper left')
start = pd.to_datetime("2025-04-01")
end = pd.to_datetime("2025-04-30")
ax2.set_xlim(left=pd.to_datetime("2025-04-01"), right=pd.to_datetime("2025-05-01"))
ax2.set_xlabel("Date", fontsize=label_font_size)
tick_dates = pd.date_range(start, end, freq="5D")
ax2.set_xticks(tick_dates, tick_dates.strftime('%Y-%m-%d'), rotation=45, ha='right', fontsize=tick_font_size)
ax2.tick_params(axis='x', rotation=45, labelsize=tick_font_size)
ax2.tick_params(axis='y', labelsize=tick_font_size)
ax2.grid(True)
# Final layout
plt.tight_layout()
figs.append((fig2, 'optimized_h.png'))

from matplotlib.ticker import ScalarFormatter
fig_op_single = plt.figure(figsize=(10, 5))
ax = plt.gca()

# Main plot
ax.plot(df_o['date'], df_o['H2Buffer1-0.time-based_0-soc'], label='Buffer SOC (%)', color='black', linewidth=linewidth)
ax.set_ylabel("Buffer SOC [%]", fontsize=label_font_size)
ax.set_ylim(0, 100)
ax.set_xlim(pd.to_datetime("2025-04-01"), pd.to_datetime("2025-05-01"))

# Define tick locations and labels
tick_dates = pd.date_range(start="2025-04-01", end="2025-04-30", freq="5D")
ax.set_xticks(tick_dates)
ax.set_xticklabels(tick_dates.strftime('%Y-%m-%d'), rotation=45, ha='right', fontsize=tick_font_size)

ax.set_xlabel("Date", fontsize=label_font_size)
ax.tick_params(axis='x', rotation=45, labelsize=tick_font_size)
ax.tick_params(axis='y', labelsize=tick_font_size)
ax.grid(True)

# Zoom in on a specific small date window
zoom_start = pd.to_datetime("2025-04-28 05:30")
zoom_end = pd.to_datetime("2025-04-28 06:00")
zoom_data = df_o[(df_o['date'] >= zoom_start) & (df_o['date'] <= zoom_end)]

# Inset plot
axins = inset_axes(ax, width="30%", height="40%", loc='lower right')
axins.plot(zoom_data['date'], zoom_data['H2Buffer1-0.time-based_0-soc'], color='black', linewidth=linewidth)

axins.set_xlim(zoom_start, zoom_end)
axins.set_ylim(99.98, 100)

# Force plain y-axis labels
axins.yaxis.set_major_formatter(ScalarFormatter(useOffset=False, useMathText=False))
axins.ticklabel_format(style='plain', axis='y')

axins.tick_params(axis='x', rotation=45, labelsize=8)
axins.tick_params(axis='y', labelsize=8)
axins.set_xticklabels([])
mark_inset(ax, axins, loc1=2, loc2=1, fc="none", ec="0.5")

# Final layout
plt.tight_layout()
figs.append((fig_op_single, 'optimized_h_single.png'))


# Two curves in one figure without zoom
fig_pres1 = plt.figure(figsize=(8, 6))
ax = plt.gca()
ax.plot(df_o['date'], df_o['H2Buffer1-0.time-based_0-soc'], label='Optimized buffer (419.9kg)', color='green', linewidth=linewidth)
ax.plot(df['date'], df['H2Buffer1-0.time-based_0-soc'], label='Unoptimized buffer (500kg)', color='red', linewidth=linewidth)
ax.set_ylabel("Buffer SOC [%]", fontsize=label_font_size)
ax.set_ylim(0, 100)
ax.set_xlim(pd.to_datetime("2025-04-01"), pd.to_datetime("2025-05-01"))

# Define tick locations and labels
tick_dates = pd.date_range(start="2025-04-01", end="2025-04-30", freq="5D")
ax.set_xticks(tick_dates)
ax.set_xticklabels(tick_dates.strftime('%Y-%m-%d'), rotation=45, ha='right', fontsize=tick_font_size)

ax.set_xlabel("Date", fontsize=label_font_size)
ax.tick_params(axis='x', rotation=45, labelsize=tick_font_size)
ax.tick_params(axis='y', labelsize=tick_font_size)
ax.grid(True)


ax.legend()
# Final layout
plt.tight_layout()
figs.append((fig_pres1, 'presentation_figure1.png'))

# Two curves in one figure with zoom:
fig_pres2 = plt.figure(figsize=(8, 6))
ax = plt.gca()
ax.plot(df_o['date'], df_o['H2Buffer1-0.time-based_0-soc'], label='Optimized buffer (419.9kg)', color='green', linewidth=linewidth)
ax.plot(df['date'], df['H2Buffer1-0.time-based_0-soc'], label='Unoptimized buffer (500kg)', color='red', linewidth=linewidth)
ax.set_ylabel("Buffer SOC [%]", fontsize=label_font_size)
ax.set_ylim(0, 100)
ax.set_xlim(pd.to_datetime("2025-04-01"), pd.to_datetime("2025-05-01"))

# Define tick locations and labels
tick_dates = pd.date_range(start="2025-04-01", end="2025-04-30", freq="5D")
ax.set_xticks(tick_dates)
ax.set_xticklabels(tick_dates.strftime('%Y-%m-%d'), rotation=45, ha='right', fontsize=tick_font_size)

ax.set_xlabel("Date", fontsize=label_font_size)
ax.tick_params(axis='x', rotation=45, labelsize=tick_font_size)
ax.tick_params(axis='y', labelsize=tick_font_size)
ax.grid(True)

# Zoom in on a specific small date window
zoom_start = pd.to_datetime("2025-04-28 05:30")
zoom_end = pd.to_datetime("2025-04-28 06:00")
zoom_data = df_o[(df_o['date'] >= zoom_start) & (df_o['date'] <= zoom_end)]

# Inset plot
axins = inset_axes(ax, width="30%", height="40%", loc='lower right')
axins.plot(zoom_data['date'], zoom_data['H2Buffer1-0.time-based_0-soc'], color='green', linewidth=linewidth)

axins.set_xlim(zoom_start, zoom_end)
axins.set_ylim(99.98, 100)

# Force plain y-axis labels
axins.yaxis.set_major_formatter(ScalarFormatter(useOffset=False, useMathText=False))
axins.ticklabel_format(style='plain', axis='y')

axins.tick_params(axis='x', rotation=45, labelsize=8)
axins.tick_params(axis='y', labelsize=8)
axins.set_xticklabels([])
mark_inset(ax, axins, loc1=2, loc2=1, fc="none", ec="0.5")
ax.legend()
# Final layout
plt.tight_layout()
figs.append((fig_pres2, 'presentation_figure2.png'))

plt.show()


save_all = input(f"Save all plots to {plot_saving_dir}? (y/n)").strip().lower() == 'y'
if save_all:
    os.makedirs(plot_saving_dir, exist_ok=True)

    for fig, ffilename in figs:
        path = os.path.join(plot_saving_dir, ffilename)
        fig.savefig(path, dpi=300)
        print(f"Saved {fig} as {ffilename}")