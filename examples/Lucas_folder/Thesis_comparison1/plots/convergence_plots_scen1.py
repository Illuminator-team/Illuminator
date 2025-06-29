import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import itertools
from mpl_toolkits.mplot3d import Axes3D  # Enables 3D plotting
import numpy as np
import ast 
import os
import glob


# Load the CSV file into a DataFrame
# PSO_file_name = './examples/Lucas_folder/Thesis_comparison2/data/PSO_live_log_1d01_01_n9g10.csv'
PSO_file_name = './examples/Lucas_folder/Thesis_comparison1/data/PSO_live_log_n9g100_seed33.csv'
GA_file_name = './examples/Lucas_folder/Thesis_comparison1/data/GA_live_log_n9g100_seed1.csv'
LBFGSB_file_name = './examples/Lucas_folder/Thesis_comparison1/data/LBFGSB_live_log_1w01_01_n9g10.csv'
# LBFGSB2_folder = './examples/Lucas_folder/Thesis_comparison2/data/LBFGS2_1w01_01_eps_1e1'
LBFGSB2_folder = './examples/Lucas_folder/Thesis_comparison1/data/LBFGSB_live_log_n9g100_seed_42_b'
plot_saving_dir = 'C:/Users/31633/Dropbox/My PC (DESKTOP-84P3QQD)/Documents/Master_thesis/Thesis_figures/Results/Scenario1'
figs = []


label_font_size = 18
tick_font_size = 14
linewidth = 2
marker_size = 30



# ---PSO plots ---
df = pd.read_csv(PSO_file_name)

# Convert strings to floats
df['fitness'] = df['fitness'].apply(lambda x: ast.literal_eval(x)[0])
df['solution'] = df['solution'].apply(lambda x: ast.literal_eval(x)[0])
df['fitness_log'] = np.log10(df['fitness'] + 1e-8)
# -- Convergence Data --
best_fitness_per_gen_pso = df.groupby('generation')['fitness'].min()
global_best_fitness_pso = best_fitness_per_gen_pso.cummin()

pop_size = 9

particle_traject_matrix = np.zeros((pop_size, int(len(df['fitness'])/pop_size)))
particle_fitness_matrix = np.zeros((pop_size, int(len(df['fitness'])/pop_size)))


for row_ix in range(pop_size):
    indices = np.arange(row_ix, len(df['fitness']), pop_size)
    particle_traject_matrix[row_ix] = indices
    particle_fitness_matrix[row_ix] = indices
    # print(indices)
# print(particle_traject_matrix)
# print(particle_fitness_matrix)
# print(particle_traject_matrix)
for i in range(particle_traject_matrix.shape[0]):
    for j in range(particle_traject_matrix.shape[1]):
        particle_traject_matrix[i,j] = df['solution'][int(particle_traject_matrix[i,j])]
        particle_fitness_matrix[i,j] = df['fitness_log'][int(particle_fitness_matrix[i,j])]
num_generations = particle_traject_matrix.shape[1]


# --- 1: Fitness per Solution (Search Space) ---

fig1_1 = plt.figure(figsize=(8, 5))
plt.scatter(df['solution'], df['fitness_log'], alpha=0.6, s=marker_size, color='purple')
# plt.title('Search Space (Log-Scaled Fitness)')
plt.xlabel('Buffer size [kg]', fontsize=label_font_size)
plt.ylabel(r'$\log_{10}$(Fitness)', fontsize=label_font_size)
plt.xlim(100, 600)
plt.ylim(2.5, 5.6)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.grid(True)
plt.tight_layout()
figs.append((fig1_1, 'PSO_scenario1_SearchSpace.png'))

# --- 2: Global best fitness per Generation ---
fig1_2 = plt.figure(figsize=(8, 5))
plt.plot(best_fitness_per_gen_pso.index, best_fitness_per_gen_pso.values, label='Best per generation', color='orange', linewidth=linewidth)
# plt.title('PSO Convergence Plot')
plt.xlim(1, num_generations +0.5)
plt.ylim(415, 445)
plt.xlabel('Generation', fontsize=label_font_size)
plt.ylabel('Global best fitness', fontsize=label_font_size)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.grid(True)
plt.tight_layout()
figs.append((fig1_2, 'PSO_scenario1_global_fitness_per_gen.png'))

# --- 3: Particle trajectory ---
fig1_3 = plt.figure(figsize=(8, 5))
for particle in range(pop_size):
    plt.plot((particle_traject_matrix[particle][:]), label=f'particle {particle+1}', linewidth=linewidth)
plt.xticks(ticks=np.arange(num_generations), labels=np.arange(1, num_generations + 1), fontsize=tick_font_size)
# plt.title('Particle Trajectory Plot')
plt.xlim(0, num_generations -0.5)
plt.ylim(100, 600)
plt.xlabel('Generation', fontsize=label_font_size)
plt.ylabel('Buffer size [Kg]', fontsize=label_font_size)
plt.legend()
plt.grid(True)
plt.tight_layout()
figs.append((fig1_3, 'PSO_scenario1_particle_trajcectory_solution.png'))
# print(particle_fitness_matrix)

# 4: Fitness per iteration
fig1_4 = plt.figure(figsize=(8, 5))
for particle in range(pop_size):
    plt.plot((particle_fitness_matrix[particle][:]), label=f'particle {particle+1}', linewidth=linewidth)
    plt.scatter(0, df['fitness_log'].iloc[particle], 
                color='red', edgecolor='black', s=marker_size/2, zorder=5, clip_on=False)
ax = plt.gca()
handles, labels = ax.get_legend_handles_labels()
for spine in ax.spines.values():
    spine.set_zorder(2)

sorted_handles_labels = sorted(zip(labels, handles), key=lambda x: x[0])  # sort by label
sorted_labels, sorted_handles = zip(*sorted_handles_labels)
plt.legend(sorted_handles, sorted_labels, fontsize='x-small', loc='best')
plt.xticks(ticks=np.arange(num_generations), labels=np.arange(1, num_generations + 1), fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xlabel('Generation', fontsize=label_font_size)
plt.ylabel(r'$\log_{10}$(Fitness)', fontsize=label_font_size)
plt.xlim(0, num_generations -0.5)
plt.ylim(2.5, 5.6)
plt.grid(True, zorder=1)
plt.tight_layout()
figs.append((fig1_4, 'PSO_scenario1_particle_trajcectory_fitness.png'))



## GA plots ##

df = pd.read_csv(GA_file_name)
# print(df['solution'].head())
df['fitness'] = df['fitness'].apply(lambda x: ast.literal_eval(x)[0])  # still a float
df['solution'] = df['solution'].apply(lambda x: ast.literal_eval(x)[0])   # now a list like (x1, x2)
# print(df['solution'].head())

# -- Convergence Data --
best_fitness_per_gen_ga = df.groupby('generation')['fitness'].min()
global_best_fitness_ga = best_fitness_per_gen_ga.cummin()

pop_size = 9

particle_traject_matrix = np.zeros((pop_size, int(len(df['fitness'])/pop_size)))
# print(particle_traject_matrix)

for row_ix in range(pop_size):
    indices = np.arange(row_ix, len(df['fitness']), pop_size)
    particle_traject_matrix[row_ix] = indices
    # print(indices)

# print(particle_traject_matrix)
for i in range(particle_traject_matrix.shape[0]):
    for j in range(particle_traject_matrix.shape[1]):
        # print(df['solution'][int(particle_traject_matrix[i,j])])
        particle_traject_matrix[i,j] = df['solution'][int(particle_traject_matrix[i,j])] # change to 'fitness' to see fitness of each particle over generations
num_generations = particle_traject_matrix.shape[1]
# print('num generations =', num_generations)

# --- 1: Fitness per Solution (Search Space) ---
df['fitness_log'] = np.log10(df['fitness'] + 1e-8)
fig2_1 = plt.figure(figsize=(8, 5))
plt.scatter(df['solution'], df['fitness_log'], alpha=0.6, clip_on=False, s=marker_size, color='purple')
# plt.title('Search Space (Log-Scaled Fitness)')
plt.xlabel('Buffer size [kg]', fontsize=label_font_size)
plt.ylabel(r'$\log_{10}$(Fitness)', fontsize=label_font_size)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xlim(100, 600)
plt.ylim(2.5, 5.6)
plt.grid(True)
plt.tight_layout()
figs.append((fig2_1, 'GA_scenario1_SearchSpace.png'))


# --- 2: Global best fitness per Generation ---
fig2_2 = plt.figure(figsize=(8, 5))
plt.plot(best_fitness_per_gen_ga.index, best_fitness_per_gen_ga.values, label='Best per generation', color='orange', linewidth=linewidth)


# plt.title('GA Convergence Plot')
plt.xlabel('Generation', fontsize=label_font_size)
plt.ylabel('Global best fitness', fontsize=label_font_size)
plt.xticks(ticks=np.arange(num_generations+1), labels=np.arange(0, num_generations+1), fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xlim(1, num_generations +0.5)
plt.ylim(410, 470)
# plt.legend()
plt.grid(True)
plt.tight_layout()
figs.append((fig2_2, 'GA_scenario1_global_fitness_per_gen.png'))
# --- 3: Particle trajectory (solution per iteration) ---

fig2_3 = plt.figure(figsize=(8, 5))

for particle in range(pop_size):
    generations = np.arange(num_generations)
    buffer_sizes = particle_traject_matrix[particle]
    plt.scatter(generations, buffer_sizes, label=f'particle {particle+1}', s=marker_size, c='blue', alpha=0.6, zorder=5, clip_on=False)

ax = plt.gca()
for spine in ax.spines.values():
    spine.set_zorder(2)

plt.xticks(ticks=np.arange(num_generations), labels=np.arange(1, num_generations + 1), fontsize=tick_font_size)
plt.xlim(0, num_generations - 0.5)
plt.ylim(100, 600)
plt.xlabel('Generation', fontsize=label_font_size)
plt.ylabel('Buffer size [Kg]', fontsize=label_font_size)
plt.xticks(fontsize=tick_font_size)
# plt.legend()
plt.grid(True, zorder=1)
plt.tight_layout()
figs.append((fig2_3, 'GA_scenario1_particle_trajcectory_solution.png'))

# --- 4: Fitness per iteration ---
df['fitness_log'] = np.log10(df['fitness'] + 1e-8)
fig2_4 = plt.figure(figsize=(8, 5))
plt.scatter(df['generation'], df['fitness_log'], alpha=0.6, s=marker_size, color='blue', zorder=5, clip_on=False)
ax = plt.gca()
for spine in ax.spines.values():
    spine.set_zorder(2)
# plt.title('Search Space (Log-Scaled Fitness)')
plt.xlabel('Generation', fontsize=label_font_size)
plt.ylabel(r'$\log_{10}$(Fitness)', fontsize=label_font_size)
plt.xticks(ticks=np.arange(num_generations+1), labels=np.arange(0, num_generations +1), fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xlim(1, num_generations + 0.5)
plt.ylim(2.5, 5.6)
plt.grid(True, zorder=1)
plt.tight_layout()
figs.append((fig2_4, 'GA_scenario1_particle_trajcectory_fitness.png'))
# plt.show()

## LBFGSB plots ##

# df = pd.read_csv(LBFGSB_file_name)

# # print(df['solution'].head())

# df['fitness'] = df['fitness'].apply(lambda x: ast.literal_eval(x)[0])  # still a float
# df['solution'] = df['solution'].apply(lambda x: ast.literal_eval(x))   # now a list like (x1, x2)

# df['x1'] = df['solution'].apply(lambda x: x[0])
# df['x2'] = df['solution'].apply(lambda x: x[1])

# # --- Plot 1: Fitness vs Solution (Search Space) ---
# # df['fitness_log'] = np.log10(df['fitness'] + 1e-8)
# plt.figure(figsize=(8, 5))

# sc = plt.scatter(df['x1'], df['x2'], c=df['fitness'], cmap='viridis', alpha=0.7)
# plt.colorbar(sc, label='Fitness')
# plt.xlabel('x1')
# plt.ylabel('x2')
# plt.title('L-BFGS-B: Search Space Exploration')
# plt.grid(True)
# plt.tight_layout()


# # --- Plot 2: Convergence ---
# plt.figure(figsize=(8, 5))

# num_iter = len(df['fitness'])
# plt.plot(df['fitness'])
# plt.xticks(ticks=np.arange(num_iter), labels=np.arange(1, num_iter + 1))
# plt.title('Convergence Plot')
# plt.xlabel('Iteration')
# plt.ylabel('fitness')
# # plt.legend()
# plt.grid(True)
# plt.tight_layout()

# plt.show()





## LBFGSB2 plots ##

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

log_files = glob.glob(os.path.join(LBFGSB2_folder, "LBFGSB_live_log_*.csv"))


dfs = []

for file in log_files:
    df = pd.read_csv(file, usecols=['iter', 'fitness'])
    # print(df)
    dfs.append(df.rename(columns={'fitness': os.path.basename(file)}))
# print(dfs)
merged_df = dfs[0]
for df in dfs[1:]:
    merged_df = pd.merge(merged_df, df, on='iter', how='outer')

merged_df['min_fitness'] = merged_df.drop(columns='iter').min(axis=1).cummin()

num_iterations = len(merged_df['iter'])
# print(num_iterations)

markers = itertools.cycle(('o', 's', '^', 'v', 'D', 'P', '*', 'X', 'H'))

# --- 1: Search space plot ---
fig3_1 = plt.figure(figsize=(8, 5))
for log_file in log_files:
    df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", 'timestep', "buffer_size"])
    # print(df)
    plt.scatter(df["buffer_size"], np.log10(df["fitness"]) + 1e-8, alpha=0.6,
                label=f'Instance starting point {df["buffer_size"][0]}',s=marker_size,  zorder=5, clip_on=False, color='purple') # os.path.basename(log_file))

ax = plt.gca()
for spine in ax.spines.values():
    spine.set_zorder(2)

handles, labels = plt.gca().get_legend_handles_labels()
sorted_handles_labels = sorted(zip(labels, handles), key=lambda x: x[0])  # sort by label
sorted_labels, sorted_handles = zip(*sorted_handles_labels)
# plt.legend(sorted_handles, sorted_labels, fontsize='x-small', loc='best')

plt.xlabel('Buffer size [kg]', fontsize=label_font_size)
plt.ylabel(r'$\log_{10}$(Fitness)', fontsize=label_font_size)
plt.xlim(100, 600)
plt.ylim(2.5, 5.6)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
# plt.title('L-BFGS-B: Search Space Exploration (Parallel)')
plt.grid(True, zorder=1)
plt.tight_layout()
figs.append((fig3_1, 'LBFGSB2_scenario1_SearchSpace.png'))


# --- 3: Particle trajectory (solution per iteration) ---
fig3_3a = plt.figure(figsize=(8,5))
for log_file, marker in zip(log_files, markers):
    df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", 'timestep', "buffer_size"])
    
    plt.plot(df["iter"], df["buffer_size"], label=f'Starting point = {df["buffer_size"][0]}', linewidth=linewidth) # os.path.basename(log_file))
handles, labels = plt.gca().get_legend_handles_labels()
sorted_handles_labels = sorted(zip(labels, handles), key=lambda x: x[0])  # sort by label
sorted_labels, sorted_handles = zip(*sorted_handles_labels)
# plt.legend(sorted_handles, sorted_labels, fontsize='x-small', loc='best')
plt.xlabel('Iteration', fontsize=label_font_size)
plt.ylabel('Buffer size [kg]', fontsize=label_font_size)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xlim(1, num_iterations +0.5)
# plt.ylim(410, 480)
plt.grid(True, zorder=1)
plt.tight_layout()
figs.append((fig3_3a, 'LBFGSB2_scenario1_particle_trajcectory_solution1.png'))


# --- 3b: Particle trajectory (solution per iteration) (incl. fitness colorbar) ---
fig3_3b = plt.figure(figsize=(8, 5))

all_fitness = []
all_buffer_sizes = []

# First pass: gather all fitness and buffer size values
for log_file in log_files:
    df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", 'timestep', "buffer_size"])
    all_fitness.extend(df["fitness"])
    all_buffer_sizes.extend(df["buffer_size"])

all_fitness = np.array(all_fitness)
# print('all fitness:', all_fitness)
all_buffer_sizes = np.array(all_buffer_sizes)
log_fitness_all = np.log10(all_fitness)

# Use actual fitness range
vmin = np.min(log_fitness_all)       # best fitness (lowest value)
# vcenter =  log_fitness_all[all_buffer_sizes.argmax()] # midpoint in log space
vmax = log_fitness_all[all_buffer_sizes.argmax()]
# vmax = np.max(log_fitness_all)       # worst fitness (highest value)
# print(vmin)
# print(vcenter)
# print(vmax)

norm = mcolors.LogNorm(vmin=vmin, vmax=vmax)
original_cmap = plt.cm.Oranges
new_cmap = mcolors.LinearSegmentedColormap.from_list(
    'subset_Oranges',
    original_cmap(np.linspace(0.4, 1.0, 256))
)

for log_file, marker in zip(log_files, markers):
    dfs.append(df.rename(columns={'fitness': os.path.basename(log_file)}))
    df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", 'timestep',"buffer_size"])
    log_fitness = np.log10(df["fitness"])

    plt.scatter(df["iter"], df["buffer_size"], c=log_fitness, cmap=new_cmap, 
                norm=norm, alpha=0.8,marker=marker,clip_on=False, zorder=5,
                label=f'Starting point = {df["buffer_size"][0]}', s=marker_size  # os.path.basename(log_file
)
ax = plt.gca()
for spine in ax.spines.values():
    spine.set_zorder(2)
import matplotlib.ticker as ticker
cbar = plt.colorbar()
cbar.set_label('Log fitness', fontsize=label_font_size)
cbar.ax.yaxis.offsetText.set_visible(False)
cbar.ax.tick_params(labelsize=tick_font_size)

handles, labels = plt.gca().get_legend_handles_labels()
sorted_handles_labels = sorted(zip(labels, handles), key=lambda x: x[0])
sorted_labels, sorted_handles = zip(*sorted_handles_labels)
plt.legend(sorted_handles, sorted_labels, fontsize='x-small', loc='best')

plt.xlabel('Iteration', fontsize=label_font_size)
plt.ylabel('Buffer size [kg]', fontsize=label_font_size)
plt.xlim(1, num_iterations +0.5)
# plt.ylim(410, 480)
# plt.title('L-BFGS-B: Solutions (Parallel)')
plt.grid(True, zorder=1)
plt.tight_layout()
figs.append((fig3_3b, 'LBFGSB2_scenario1_particle_trajcectory_solution2.png'))


# --- 2b: Global best fitness per Generation general ---
fig3_2b = plt.figure(figsize=(8, 5))
plt.plot(merged_df['iter'], merged_df['min_fitness'], label='Best per generation', color='orange', linewidth=linewidth)
plt.xlabel('Iteration', fontsize=label_font_size)
plt.ylabel('Global best fitness', fontsize=label_font_size)
ticks = np.arange(num_iterations + 1)
label_interval = 5 
tick_labels = [str(i) if i % label_interval == 0 else '' for i in ticks]
plt.xticks(ticks=ticks, labels=tick_labels, fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xlim(1, num_iterations +0.5)
plt.ylim(415, 470)
# plt.legend()
plt.grid(True)
plt.tight_layout()
figs.append((fig3_2b, 'LBFGSB2_scenario1_global_fitness_per_gen_general.png'))


# 4: Fitness per iteration
fig3_4 = plt.figure(figsize=(8, 5))

for log_file in log_files:
    df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", 'timestep', "buffer_size"])

    if df.empty:
        print(f"Warning: {log_file} is empty or has no data rows.")
        continue 

    plt.plot(df['iter'], np.log10(df["fitness"])+ 1e-8, label=f'Instance starting point {df["buffer_size"][0]}', linewidth=linewidth) # os.path.basename(log_file))
    plt.scatter(df['iter'].iloc[0], np.log10(df['fitness'].iloc[0])+ 1e-8,
                color='red', edgecolor='black', s=marker_size/2, zorder=5, clip_on=False)
handles, labels = plt.gca().get_legend_handles_labels()
for spine in ax.spines.values():
    spine.set_zorder(2)

sorted_handles_labels = sorted(zip(labels, handles), key=lambda x: x[0])  # sort by label
sorted_labels, sorted_handles = zip(*sorted_handles_labels)
plt.legend(sorted_handles, sorted_labels, fontsize='x-small', loc='best')
plt.xticks(ticks=ticks, labels=tick_labels, fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xlabel('Iteration', fontsize=label_font_size)
plt.ylabel(r'$\log_{10}$(Fitness)', fontsize=label_font_size)
plt.xlim(1, num_iterations + 0.5)
plt.ylim(2.5, 5.6)
# plt.title('L-BFGS-B: Convergence Plot (Parallel)')
plt.grid(True, zorder=1)
plt.tight_layout()
figs.append((fig3_4, 'LBFGSB2_scenario1_particle_trajcectory_fitness.png'))

# fig_all_convergence = plt.figure(figsize=(8, 5))
# plt.plot(best_fitness_per_gen_pso, label='Convergence PSO', linewidth=linewidth)
# plt.plot(range(1, 1 + len(merged_df['min_fitness'])), 
#          merged_df['min_fitness'], 
#          label='Convergence parallel L-BFGS-B', 
#          linewidth=linewidth)
# plt.plot(best_fitness_per_gen_ga, label='Convergence GA', linewidth=linewidth, linestyle='dashed', color='red')
# plt.xlabel('Iteration', fontsize=label_font_size)
# plt.ylabel('Global best fitness', fontsize=label_font_size)
# ticks = np.arange(num_iterations + 1)
# label_interval = 5 
# tick_labels = [str(i) if i % label_interval == 0 else '' for i in ticks]
# plt.xticks(ticks=ticks, labels=tick_labels, fontsize=tick_font_size)
# plt.yticks(fontsize=tick_font_size)
# plt.xlim(1, num_iterations +0.5)
# plt.ylim(415, 465)
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
fig_all_convergence, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(8, 5))
# linewidth = linewidth *1.5
# tick_font_size=tick_font_size*1.5
# label_font_size =label_font_size*1.5
# Plot data on both axes
iters = np.arange(1, num_iterations + 1)
ax1.plot(np.arange(1, len(best_fitness_per_gen_pso) + 1), best_fitness_per_gen_pso, label='Convergence PSO', linewidth=linewidth)
ax1.plot(iters[:len(merged_df['min_fitness'])], merged_df['min_fitness'], 
         label='Convergence parallel L-BFGS-B', 
         linewidth=linewidth)
ax1.plot(np.arange(1, len(best_fitness_per_gen_ga) + 1), best_fitness_per_gen_ga, label='Convergence GA', linewidth=linewidth, linestyle='dashed', color='red')

ax2.plot(best_fitness_per_gen_pso, linewidth=linewidth)
ax2.plot(iters[:len(merged_df['min_fitness'])], merged_df['min_fitness'],
         linewidth=linewidth)
ax2.plot(best_fitness_per_gen_ga, linewidth=linewidth, linestyle='dashed', color='red')
ax1.grid(True)
ax2.grid(True)


# Set consistent labels and ticks
ax1.set_ylabel('Global best fitness', fontsize=label_font_size)
# ax2.set_xlabel('Iteration', fontsize=label_font_size)
# ax1.set_xlabel('Iteration', fontsize=label_font_size)
fig_all_convergence.text(0.535, 0.02, 'Iteration', ha='center', fontsize=label_font_size)
ax1.tick_params(axis='both', labelsize=tick_font_size)
ax2.tick_params(axis='both', labelsize=tick_font_size)

ax1.set_ylim(415, 470)

# Hide spines between plots
ax1.spines['right'].set_visible(False)
ax2.spines['left'].set_visible(False)
ax1.yaxis.tick_left()
ax1.tick_params(labelright=False)
ax2.yaxis.tick_right()
ax2.tick_params(axis='y', right=False)  # turn off right-side ticks
# ax2.yaxis.set_ticks([])  # removes all ticks
# Remove the last x-tick on ax1


# Set x-axis limits for the two axes to create a visual break
ax1.set_xlim(1, 17)
ax2.set_xlim(25, num_iterations + 0.5)
# Remove the first x-tick on ax2
ticks_ax2 = ax2.get_xticks()
ax2.set_xticks(ticks_ax2[1:])   # drop first tick

# Add the diagonal break marks
d = .015
kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)
ax1.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

kwargs.update(transform=ax2.transAxes)
ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)
ax2.plot((-d, +d), (-d, +d), **kwargs)

# Final layout
fig_all_convergence.legend(
    loc='upper right',
    bbox_to_anchor=(0.96, 0.95),   # stick to upper right of axes
    fontsize=label_font_size/2
)
fig_all_convergence.tight_layout()
fig_all_convergence.subplots_adjust(wspace=0.05)  # Reduce space between plots
figs.append((fig_all_convergence, 'global_fitness_per_gen_all_algs.png'))

plt.show()

save_all = input(f"Save all plots to {plot_saving_dir}? (y/n)").strip().lower() == 'y'
if save_all:
    os.makedirs(plot_saving_dir, exist_ok=True)

    for fig, ffilename in figs:
        path = os.path.join(plot_saving_dir, ffilename)
        fig.savefig(path, dpi=300)
        print(f"Saved {fig} as {ffilename}")