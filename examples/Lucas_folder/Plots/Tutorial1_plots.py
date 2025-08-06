import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
plot_saving_dir = 'C:/Users/31633/Dropbox/My PC (DESKTOP-84P3QQD)/Documents/Master_thesis/Thesis_figures/Background'
figs = []
label_font_size = 18
tick_font_size = 14
linewidth = 2
marker_size = 30
second_linewidth=.5

output_path = 'out_Tutorial1.csv'
dump_col = 'H2_controller-0.time-based_0-dump'
# This runs the Illuminator for the defined scenario
# command = ['illuminator', 'scenario', 'run', scenario]
# subprocess.run(command, check=True)

# Reading the output CSV
df = pd.read_csv(output_path)
# df2 = pd.read_csv('examples/h2_system_example/thermolyzer_replacement_generated.csv', header=1)

soc = df['Battery1-0.time-based_0-soc']

demand = df['Load1-0.time-based_0-load_dem']
pv = df['PV1-0.time-based_0-pv_gen']
wind = df['Wind1-0.time-based_0-wind_gen']
dump = df['Controller1-0.time-based_0-dump']
battery_power = df['Controller1-0.time-based_0-flow2b']



battery_power[battery_power > 0] = 0
battery_power = -battery_power
fig_power_flows = plt.figure(figsize=(10, 5))

plt.plot(battery_power, label='Battery power', linewidth=linewidth, color='green')
# xticks = list(range(0, len(df)+4, 4))  # one tick every hour
# xlabels = [str(h) for h in range(len(xticks))]  
xticks = list(range(0, len(df) + 1, 4))
if xticks[-1] > len(df):  # remove overshoot
    xticks = xticks[:-1]
xlabels = [str(i) for i in range(len(xticks))]
plt.xticks(ticks=xticks, labels=xlabels)
plt.xlabel('Hour', fontsize=label_font_size)
plt.tick_params(axis='x', labelsize=tick_font_size)
plt.ylabel('Power [kW]', fontsize=label_font_size)
plt.tick_params(axis='y', labelsize=tick_font_size)
plt.gca().set_xlim(left=0, right=len(df))
plt.ylim([0, 2])
# plt.gca().set_ylim(bottom=0)
# plt.plot(pv, label='pv')
# plt.plot(wind, label='wind')
plt.grid(True)
plt.plot(pv+wind, label='RES generation', linewidth=linewidth, color='orange')	
plt.plot(demand, label='Demand', linewidth=linewidth, color='blue')

# plt.plot(dump, label='dump')
plt.legend()
figs.append((fig_power_flows, 'examplesim_power.png'))


fig_soc_plot = plt.figure(figsize=(10, 5))

plt.gca().set_xlim(left=0, right=len(df))
plt.ylim([40, 100])
plt.xticks(ticks=xticks, labels=xlabels)
plt.xlabel('Hour', fontsize=label_font_size)
plt.tick_params(axis='x', labelsize=tick_font_size)
plt.ylabel('SoC [%]', fontsize=label_font_size)
plt.tick_params(axis='y', labelsize=tick_font_size)
plt.plot(soc, label='Battery SoC', linewidth=linewidth, color='black')
figs.append((fig_soc_plot, 'examplesim_soc.png'))
plt.grid(True)
plt.show()

save_all = input(f"Save all plots to {plot_saving_dir}? (y/n)").strip().lower() == 'y'
if save_all:
    os.makedirs(plot_saving_dir, exist_ok=True)

    for fig, ffilename in figs:
        path = os.path.join(plot_saving_dir, ffilename)
        fig.savefig(path, dpi=300)
        print(f"Saved {fig} as {ffilename}")