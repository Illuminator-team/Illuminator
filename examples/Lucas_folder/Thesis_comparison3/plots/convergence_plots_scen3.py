import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import itertools
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D  # Enables 3D plotting
import numpy as np
import ast 
import os
import glob
# Load the CSV file into a DataFrame
# PSO_file_name = './examples/Lucas_folder/Thesis_comparison2/data/PSO_live_log_1d01_01_n9g10.csv'

PSO_file_name = './examples/Lucas_folder/Thesis_comparison3/data/PSO_live_log_n9g100_seed1b.csv'
GA_file_name =  './examples/Lucas_folder/Thesis_comparison3/data/GA_live_log_n9g100_seed33b.csv'
LBFGSB2_folder = './examples/Lucas_folder/Thesis_comparison3/data/LBFGSB_p_1d_n9_g100_seed_42_b'
plot_saving_dir = 'C:/Users/31633/Dropbox/My PC (DESKTOP-84P3QQD)/Documents/Master_thesis/Thesis_figures/Results/Scenario3'
figs = []


label_font_size = 18
tick_font_size = 14
linewidth = 2
marker_size = 30
second_linewidth=.5


### PSO plots ###
df_pso = pd.read_csv(PSO_file_name)
pop_size = 9
num_gens = int(len(df_pso) / pop_size)

# Convert 'solution' column to list of ceiled integers
df_pso['solution'] = df_pso['solution'].apply(lambda x: [int(np.ceil(val)) for val in ast.literal_eval(x)])
df_pso['fitness'] = df_pso['fitness'].apply(lambda x: ast.literal_eval(x)[0])
best_fitness_per_gen_pso = df_pso.groupby('generation')['fitness'].min()
global_best_fitness_pso = best_fitness_per_gen_pso.cummin()

df_pso['solution_tuple'] = df_pso['solution'].apply(tuple)
df_pso = df_pso.drop_duplicates(subset='solution_tuple')
df_pso = df_pso.drop(columns='solution_tuple')


# Extract fitness numeric values for sorting and coloring
df_pso['fitness_sort'] = df_pso['fitness'] #.apply(lambda x: ast.literal_eval(x)[0])
df_pso_sorted = df_pso.sort_values(by='fitness')
df_pso_desceding = df_pso.sort_values(by='fitness', ascending=False)

# df_pso_sorted = df_pso_sorted.drop(columns=['fitness'])
# df_pso_desceding = df_pso_desceding.drop(columns=['fitness'])

df_pso_sorted['fitness_numeric'] = df_pso['fitness'] # .apply(lambda x: ast.literal_eval(x)[0])
df_pso_desceding['fitness_numeric'] = df_pso_desceding['fitness'] # .apply(lambda x: ast.literal_eval(x)[0])

# print('asceding:\n', df_pso)
# print('desceding:\n', df_pso_desceding)

# Normalize fitness values for colormap
min_c = df_pso_sorted['fitness_numeric'].min()
max_c = df_pso_sorted['fitness_numeric'].max()
norm = mcolors.Normalize(vmin=min_c, vmax=max_c)
cmap = cm.Greens_r  # You can also try 'plasma', 'inferno', 'coolwarm', etc.



# --- 1: Fitness per Solution (Search Space) ---

fig1_1 = plt.figure(figsize=(8, 5))
x_vals = range(5)

for i, (_, row) in enumerate(df_pso_desceding.iterrows()):
    y_vals = row['solution']
    c_val = row['fitness_numeric']
    color = cmap(norm(c_val))
    plt.plot(x_vals, y_vals, marker='o', color=color, linewidth=second_linewidth)

# Add colorbar
sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])  # Required for colorbar
cbar = plt.colorbar(sm)
cbar.set_label("Fitness [kW]", fontsize=label_font_size)

# Labels and layout
# plt.xlabel('EV Index', fontsize=label_font_size)
ev_labels = [f'EV{i+1}' for i in range(len(x_vals))]
plt.xticks(ticks=x_vals, labels=ev_labels, fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.ylabel(r'$\tau^0$', fontsize=label_font_size)
plt.grid(True)
plt.tight_layout()
figs.append((fig1_1, 'PSO_scenario3_SearchSpace.png'))

# --- 2: Global best fitness per Generation ---
fig1_2 = plt.figure(figsize=(8, 5))
plt.plot(best_fitness_per_gen_pso.index, best_fitness_per_gen_pso.values, label='Best per generation', color='orange', linewidth=linewidth)
# plt.plot(global_best_fitness.index, global_best_fitness.values, label='Global best so far', color='blue', linestyle='--', linewidth=2)
# plt.title('PSO Convergence Plot')
plt.xlabel('Generation', fontsize=label_font_size)
plt.ylabel('Fitness [kW]', fontsize=label_font_size)
# plt.legend()
plt.xticks(ticks=np.arange(num_gens +1), labels=np.arange(0, num_gens+1), fontsize=tick_font_size)
plt.xlim(1, num_gens + 0.5)

plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
# plt.ylim(bottom=-65)
plt.grid(True)
plt.tight_layout()
figs.append((fig1_2, 'PSO_scenario3_global_fitness_per_gen.png'))
# plt.show()

### GA plots ###

df_ga = pd.read_csv(GA_file_name)
pop_size = 9
num_gens = int(len(df_ga) / pop_size)

# Convert 'solution' column to list of ceiled integers
df_ga['solution'] = df_ga['solution'].apply(lambda x: [int(np.ceil(val)) for val in ast.literal_eval(x)])
df_ga['fitness'] = df_ga['fitness'].apply(lambda x: ast.literal_eval(x)[0])
best_fitness_per_gen_ga = df_ga.groupby('generation')['fitness'].min()
global_best_fitness_ga = best_fitness_per_gen_ga.cummin()

df_ga['solution_tuple'] = df_ga['solution'].apply(tuple)
df_ga = df_ga.drop_duplicates(subset='solution_tuple')
df_ga = df_ga.drop(columns='solution_tuple')


# Extract fitness numeric values for sorting and coloring
df_ga['fitness_sort'] = df_ga['fitness'] #.apply(lambda x: ast.literal_eval(x)[0])
df_ga_sorted = df_ga.sort_values(by='fitness')
df_ga_desceding = df_ga.sort_values(by='fitness', ascending=False)

# df_ga_sorted = df_ga_sorted.drop(columns=['fitness'])
# df_ga_desceding = df_ga_desceding.drop(columns=['fitness'])

df_ga_sorted['fitness_numeric'] = df_ga['fitness'] # .apply(lambda x: ast.literal_eval(x)[0])
df_ga_desceding['fitness_numeric'] = df_ga_desceding['fitness'] # .apply(lambda x: ast.literal_eval(x)[0])

# print('asceding:\n', df_ga)
# print('desceding:\n', df_ga_desceding)

# Normalize fitness values for colormap
min_c = df_ga_sorted['fitness_numeric'].min()
max_c = df_ga_sorted['fitness_numeric'].max()
norm = mcolors.Normalize(vmin=min_c, vmax=max_c)
cmap = cm.Greens_r  # You can also try 'plasma', 'inferno', 'coolwarm', etc.



# --- 1: Fitness per Solution (Search Space) ---

fig1_1 = plt.figure(figsize=(8, 5))
x_vals = range(5)

for i, (_, row) in enumerate(df_ga_desceding.iterrows()):
    y_vals = row['solution']
    c_val = row['fitness_numeric']
    color = cmap(norm(c_val))
    plt.plot(x_vals, y_vals, marker='o', color=color, linewidth=second_linewidth)

# Add colorbar
sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])  # Required for colorbar
cbar = plt.colorbar(sm)
cbar.set_label("Fitness [kW]", fontsize=label_font_size)

# Labels and layout
# plt.xlabel('EV Index', fontsize=label_font_size)
ev_labels = [f'EV{i+1}' for i in range(len(x_vals))]
plt.xticks(ticks=x_vals, labels=ev_labels, fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.ylabel(r'$\tau^0$', fontsize=label_font_size)
plt.grid(True)
plt.tight_layout()
figs.append((fig1_1, 'GA_scenario3_SearchSpace.png'))

# --- 2: Global best fitness per Generation ---
fig1_2 = plt.figure(figsize=(8, 5))
plt.plot(best_fitness_per_gen_ga.index, best_fitness_per_gen_ga.values, label='Best per generation', color='orange', linewidth=linewidth)
# plt.plot(global_best_fitness.index, global_best_fitness.values, label='Global best so far', color='blue', linestyle='--', linewidth=2)
# plt.title('PSO Convergence Plot')
plt.xlabel('Generation', fontsize=label_font_size)
plt.ylabel('Fitness [kW]', fontsize=label_font_size)
# plt.legend()
plt.xticks(ticks=np.arange(num_gens +1), labels=np.arange(0, num_gens+1), fontsize=tick_font_size)
plt.xlim(1, num_gens + 0.5)

plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
# plt.ylim(bottom=-65)
plt.grid(True)
plt.tight_layout()
figs.append((fig1_2, 'GA_scenario3_global_fitness_per_gen.png'))
# plt.show()




# save_all = input(f"Save all plots to {plot_saving_dir}? (y/n)").strip().lower() == 'y'
# if save_all:
#     os.makedirs(plot_saving_dir, exist_ok=True)

#     for fig, ffilename in figs:
#         path = os.path.join(plot_saving_dir, ffilename)
#         fig.savefig(path, dpi=300)
#         print(f"Saved {fig} as {ffilename}")



# ## LBFGSB2 plots ##

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

log_files = glob.glob(os.path.join(LBFGSB2_folder, "LBFGSB_live_log_*.csv"))


dfs = []

for file in log_files:
    df = pd.read_csv(file, skiprows=1, names=['iter', 'fitness', 'timestep', 'ev1', 'ev2', 'ev3', 'ev4', 'ev5']) #, usecols=['iter', 'fitness'])

    run_label = os.path.basename(file)
    df = df.rename(columns={'fitness': run_label})
    
    dfs.append(df)


merged_df = dfs[0]
# print('dfs:\n', dfs)

for df in dfs[1:]:
    merged_df = pd.merge(merged_df, df, on='iter', how='outer')
# print('merged:\n', merged_df)
df_lbfgsb = merged_df.copy()
merged_df['min_fitness'] = merged_df.drop(columns='iter').min(axis=1).cummin()

# print(df_lbfgsb.head())
# print(merged_df)
num_iterations = len(merged_df['iter'])
# print(merged_df.columns)
fitness_columns = [col for col in merged_df.columns if col not in ['iter', 'timestep_x', 'ev1_x', 'ev2_x', 'ev3_x', 'ev4_x', 'ev5_x', 'iter', 'timestep', 'ev1', 'ev2', 'ev3', 'ev4', 'ev5', 'timestep_y', 'ev1_y', 'ev2_y', 'ev3_y', 'ev4_y', 'ev5_y', 'min_fitness']]
print('fitness_columns:', fitness_columns)
min_fitness = merged_df[fitness_columns].min().min()
max_fitness = merged_df[fitness_columns].max().max()
# print(min_fitness, max_fitness)
# print(merged_df[fitness_columns])
best_fitness_per_gen_lbfgs = merged_df[fitness_columns].min(axis=1).cummin()


# all_fitness = []


# for log_file in log_files:
#     df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", 'timestep', "x1", "x2"])
#     all_fitness.extend(df["fitness"].values)

# # print(all_fitness)
vmin = np.min(min_fitness)
vmax = np.max(max_fitness)
# print(vmin, vmax)
norm = Normalize(vmin=vmin, vmax=vmax)

# --- Plot 1: Search Space Plot ---
fig3_1 = plt.figure(figsize=(8, 5))

for log_file in log_files:
    df = pd.read_csv(log_file, skiprows=1, names=['iter', 'fitness', 'timestep', 'ev1', 'ev2', 'ev3', 'ev4', 'ev5'])
    
    y_vals = df[['ev1', 'ev2', 'ev3', 'ev4', 'ev5']].values
    fitness_vals = df['fitness'].values

    for i in range(len(df)):
        evs = y_vals[i]
        fitness = fitness_vals[i]
        color = cmap(norm(fitness))

        plt.plot(range(len(evs)), evs, color=color, marker='o', linewidth=second_linewidth)
# Add colorbar
sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])  # Required for colorbar
cbar = plt.colorbar(sm)
cbar.set_label("Fitness [kW]", fontsize=label_font_size)

# Labels and layout
# plt.xlabel('EV Index', fontsize=label_font_size)
ev_labels = [f'EV{i+1}' for i in range(len(x_vals))]
plt.xticks(ticks=x_vals, labels=ev_labels, fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.ylabel(r'$\tau^0$', fontsize=label_font_size)
plt.grid(True)
plt.tight_layout()
figs.append((fig3_1, 'LBFGSB_scenario3_SearchSpace.png'))


# --- 2: Global best fitness per Generation ---
fig3_2 = plt.figure(figsize=(8, 5))
# print(merged_df['min_fitness'])
# print(merged_df)
plt.plot(merged_df['iter'], best_fitness_per_gen_lbfgs, label='Best per generation', color='orange', linewidth=linewidth)
plt.xlabel('Iteration', fontsize=label_font_size)
plt.ylabel('Global best fitness [kW]', fontsize=label_font_size)
ticks = np.arange(num_iterations + 1)
label_interval = 5 
tick_labels = [str(i) if i % label_interval == 0 else '' for i in ticks]
plt.xticks(ticks=ticks, labels=tick_labels, fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xlim(1, num_iterations +0.5)
# plt.ylim(415, 445)
# plt.legend()
plt.grid(True)
plt.tight_layout()
figs.append((fig3_2, 'LBFGSB2_scenario3_global_fitness_per_gen_general.png'))


### Genaral plots ###
largest_n_iterations = max(len(best_fitness_per_gen_pso), len(best_fitness_per_gen_lbfgs), len(best_fitness_per_gen_ga))
# --- 3: Convergence Plot (All Algorithms) ---
fig_all_convergence = plt.figure(figsize=(8, 5))
plt.plot(best_fitness_per_gen_pso, label='Convergence PSO', linewidth=linewidth)
plt.plot(range(1, 1 + len(merged_df['min_fitness'])), 
         best_fitness_per_gen_lbfgs, 
         label='Convergence parallel L-BFGS-B', 
         linewidth=linewidth)
plt.plot(best_fitness_per_gen_ga, label='Convergence GA', linewidth=linewidth, linestyle='dashed', color='red')
plt.xlabel('Iteration', fontsize=label_font_size)
plt.ylabel('Global best fitness [kW]', fontsize=label_font_size)
ticks = np.arange(largest_n_iterations + 1)
label_interval = 5 
tick_labels = [str(i) if i % label_interval == 0 else '' for i in ticks]
plt.xticks(ticks=ticks, labels=tick_labels, fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xlim(1, largest_n_iterations +0.5)
# plt.ylim(415, 465)
plt.legend()
plt.grid(True)
plt.tight_layout()
figs.append((fig_all_convergence, 'global_fitness_per_gen_all_algs_scen3.png'))


plt.show()


save_all = input(f"Save all plots to {plot_saving_dir}? (y/n)").strip().lower() == 'y'
if save_all:
    os.makedirs(plot_saving_dir, exist_ok=True)

    for fig, ffilename in figs:
        path = os.path.join(plot_saving_dir, ffilename)
        fig.savefig(path, dpi=300)
        print(f"Saved {fig} as {ffilename}")