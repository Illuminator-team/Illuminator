import pandas as pd
import numpy as np
import ast
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import os

plot_saving_dir = 'C:/Users/31633/Dropbox/My PC (DESKTOP-84P3QQD)/Documents/Master_thesis/Thesis_figures/Results/Scenario3'
figs = []
label_font_size = 18
tick_font_size = 14
linewidth = 2
marker_size = 30
second_linewidth=.5
# Load and process data
# data = pd.read_csv('examples\Lucas_folder\Optimization_project\PSO_live_log.csv')

# # Convert 'solution' column to list of ceiled integers
# data['solution'] = data['solution'].apply(lambda x: [int(np.ceil(val)) for val in ast.literal_eval(x)])

# data['solution_tuple'] = data['solution'].apply(tuple)
# data = data.drop_duplicates(subset='solution_tuple')
# data = data.drop(columns='solution_tuple')


# # Extract fitness numeric values for sorting and coloring
# data['fitness_sort'] = data['fitness'].apply(lambda x: ast.literal_eval(x)[0])
# data = data.sort_values(by='fitness_sort').drop(columns=['fitness_sort'])
# data['fitness_numeric'] = data['fitness'].apply(lambda x: ast.literal_eval(x)[0])

# print(data)

# # Normalize fitness values for colormap
# min_c = data['fitness_numeric'].min()
# max_c = data['fitness_numeric'].max()
# norm = mcolors.Normalize(vmin=min_c, vmax=max_c)
# cmap = cm.plasma  # You can also try 'plasma', 'inferno', 'coolwarm', etc.

# # Plot
# plt.figure(figsize=(8, 5))
# x_vals = range(5)

# for i, (_, row) in enumerate(data.iterrows()):
#     # if i>300:
#     #     continue
#     # if i % 10 != 0:
#     #     continue  # skip lines except every 10th
#     y_vals = row['solution']
#     c_val = row['fitness_numeric']
#     color = cmap(norm(c_val))
#     plt.plot(x_vals, y_vals, marker='o', color=color, linewidth=2)

# # Add colorbar
# sm = cm.ScalarMappable(cmap=cmap, norm=norm)
# sm.set_array([])  # Required for colorbar
# cbar = plt.colorbar(sm)
# cbar.set_label("Fitness Value")

# # Labels and layout
# plt.xlabel('Index in List (Position in B)')
# plt.ylabel('Ceiled Values from B')
# plt.title('Solutions Colored by Fitness (Lower = Better)')
# plt.grid(True)
# plt.tight_layout()
# # plt.show()

output_file = 'examples/Lucas_folder/Optimization_project/EV_single_day/out.csv'

# Load your data
output_data = pd.read_csv(output_file)

# Create main figure and first axis (left y-axis for powers)

fig, ax1 = plt.subplots(figsize=(8, 5))


ax1.plot(output_data['CSV_EV_presence-0.time-based_0-ev1'], alpha=0.2, label='EV Presence 1', color='blue')
ax1.plot(output_data['CSV_EV_presence-0.time-based_0-ev2'], alpha=0.2, label='EV Presence 2', color='orange')
ax1.plot(output_data['CSV_EV_presence-0.time-based_0-ev3'], alpha=0.2, label='EV Presence 3', color='green')
ax1.plot(output_data['CSV_EV_presence-0.time-based_0-ev4'], alpha=0.2, label='EV Presence 4', color='purple')
ax1.plot(output_data['CSV_EV_presence-0.time-based_0-ev5'], alpha=0.2, label='EV Presence 5', color='brown')
ax1.plot(output_data['EV1-0.time-based_0-demand'], alpha=1, label='EV demand 1', color='blue')
ax1.plot(output_data['EV2-0.time-based_0-demand'], alpha=1, label='EV demand 2', color='orange')
ax1.plot(output_data['EV3-0.time-based_0-demand'], alpha=1, label='EV demand 3', color='green')
ax1.plot(output_data['EV4-0.time-based_0-demand'], alpha=1, label='EV demand 4', color='purple')
ax1.plot(output_data['EV5-0.time-based_0-demand'], alpha=1, label='EV demand 5', color='brown')


# ax1.plot(output_data['PV1-0.time-based_0-pv_gen'] + output_data['Wind1-0.time-based_0-wind_gen'], alpha=1, label='PV + Wind Generation', color='orange')
ax1.plot(output_data['Controller1-0.time-based_0-dump'], label='Controller Dump', color='red')

ax1.set_ylabel('Power-related values')
ax1.set_xlabel('Time')

# x_positions = [48.92174852751861, 52.032833756555796, 72.99887388913602, 10.91090839417826, 33.54807648485447]
# for x in x_positions:
#     ax1.axvline(x=x, color='gray', linestyle='--', alpha=0.5)
# Create second y-axis (right side) for SOC
ax2 = ax1.twinx()
# ax2.plot(output_data['Battery1-0.time-based_0-soc'], label='Battery1 SOC', color='green')
ax2.set_ylabel('SOC')

ax2.plot(output_data['EV1-0.time-based_0-soc'], alpha=0.2, label='EV soc 1')
ax2.plot(output_data['EV2-0.time-based_0-soc'], alpha=0.2, label='EV soc 2')
ax2.plot(output_data['EV3-0.time-based_0-soc'], alpha=0.2, label='EV soc 3')
ax2.plot(output_data['EV4-0.time-based_0-soc'], alpha=0.2, label='EV soc 4')
ax2.plot(output_data['EV5-0.time-based_0-soc'], alpha=0.2, label='EV soc 5')
# Combine legends from both axes
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
plt.tight_layout()



fig_presence, ax = plt.subplots(figsize=(10, 5))  # Larger height for visibility

evs = [1, 2, 3, 4, 5]
colors = plt.cm.tab10(range(len(evs)))  # Distinct color for each EV

for i, ev in enumerate(evs):
    col = f'CSV_EV_presence-0.time-based_0-ev{ev}'
    # Shift each presence series by index `i` to separate vertically
    y_vals = output_data[col] + i*4
    ax.step(output_data.index, y_vals, where='post',
            label=f'EV{ev}', color=colors[i], linewidth=linewidth)

# Set custom y-ticks to show "Present"/"Absent" per EV

yticks = []
ylabels = []

for i in range(len(evs)):
    base = i * 4
    yticks.extend([base, base + 1])          # Absent at base, Present at base+1
    ylabels.extend(['Absent', 'Present'])

ax.set_yticks(yticks)
ax.set_yticklabels(ylabels, fontsize=tick_font_size)
# ax.set_yticks(np.arange(len(evs)*2), labels=ylabels, fontsize=tick_font_size)   
# ax.set_yticklabels([f'EV{i}: Absent / Present' for i in evs], fontsize=tick_font_size)

ax.set_xlabel('Time step index', fontsize=label_font_size)
# ax.set_xlim(0, len(output_data))
# ax.set_ylim(-0.5, len(evs) + 0.5)

ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.0))
ax.grid(axis='x', linestyle=':', alpha=0.5)

plt.xticks(fontsize=tick_font_size)
plt.tight_layout()

figs.append((fig_presence, 'presence_plot_scen3.png'))
plt.show()

save_all = input(f"Save all plots to {plot_saving_dir}? (y/n)").strip().lower() == 'y'
if save_all:
    os.makedirs(plot_saving_dir, exist_ok=True)

    for fig, ffilename in figs:
        path = os.path.join(plot_saving_dir, ffilename)
        fig.savefig(path, dpi=300)
        print(f"Saved {fig} as {ffilename}")