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
PSO_file_name = './examples/Lucas_folder/Thesis_comparison1/data/PSO_live_log_n9g30.csv'
GA_file_name =  './examples/Lucas_folder/Thesis_comparison1/data/GA_live_log_n9g30.csv'
LBFGSB_file_name = './examples/Lucas_folder/Thesis_comparison2/data/LBFGSB_live_log_1w01_01_n9_g10.csv'
# LBFGSB2_folder = './examples/Lucas_folder/Thesis_comparison2/data/LBFGS2_1w01_01_eps_1e1'
LBFGSB2_folder = './examples/Lucas_folder/Thesis_comparison1/data/LBFGSB2_pop9'

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
best_fitness_per_gen = df.groupby('generation')['fitness'].min()
global_best_fitness = best_fitness_per_gen.cummin()

pop_size = 9

particle_traject_matrix = np.zeros((pop_size, int(len(df['fitness'])/pop_size)))
particle_fitness_matrix = np.zeros((pop_size, int(len(df['fitness'])/pop_size)))


for row_ix in range(pop_size):
    indices = np.arange(row_ix, len(df['fitness']), pop_size)
    particle_traject_matrix[row_ix] = indices
    particle_fitness_matrix[row_ix] = indices
    # print(indices)
print(particle_traject_matrix)
print(particle_fitness_matrix)
# print(particle_traject_matrix)
for i in range(particle_traject_matrix.shape[0]):
    for j in range(particle_traject_matrix.shape[1]):
        particle_traject_matrix[i,j] = df['solution'][int(particle_traject_matrix[i,j])]
        particle_fitness_matrix[i,j] = df['fitness_log'][int(particle_fitness_matrix[i,j])]
num_generations = particle_traject_matrix.shape[1]


# --- 1: Fitness per Solution (Search Space) ---

plt.figure(figsize=(8, 5))
plt.scatter(df['solution'], df['fitness_log'], alpha=0.6, s=marker_size, color='purple')
# plt.title('Search Space (Log-Scaled Fitness)')
plt.xlabel('Solution', fontsize=label_font_size)
plt.ylabel(r'$\log_{10}$(Fitness)', fontsize=label_font_size)
plt.xlim(100, 600)
plt.ylim(2.5, 5.6)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.grid(True)
plt.tight_layout()


# --- 2: Global best fitness per Generation ---
plt.figure(figsize=(8, 5))
plt.plot(best_fitness_per_gen.index, best_fitness_per_gen.values, label='Best per generation', color='orange', linewidth=linewidth)
# plt.title('PSO Convergence Plot')
plt.xlim(1, num_generations +0.5)
plt.ylim(410, 460)
plt.xlabel('Generation', fontsize=label_font_size)
plt.ylabel('Global best fitness', fontsize=label_font_size)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.grid(True)
plt.tight_layout()


# --- 3: Particle trajectory ---
plt.figure(figsize=(8, 5))
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

print(particle_fitness_matrix)

# 4: Fitness per iteration
plt.figure(figsize=(8, 5))
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




## GA plots ##

df = pd.read_csv(GA_file_name)
# print(df['solution'].head())
df['fitness'] = df['fitness'].apply(lambda x: ast.literal_eval(x)[0])  # still a float
df['solution'] = df['solution'].apply(lambda x: ast.literal_eval(x)[0])   # now a list like (x1, x2)
# print(df['solution'].head())

# -- Convergence Data --
best_fitness_per_gen = df.groupby('generation')['fitness'].min()
global_best_fitness = best_fitness_per_gen.cummin()

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
print('num generations =', num_generations)

# --- 1: Fitness per Solution (Search Space) ---
df['fitness_log'] = np.log10(df['fitness'] + 1e-8)
plt.figure(figsize=(8, 5))
plt.scatter(df['solution'], df['fitness_log'], alpha=0.6, s=marker_size, color='purple')
# plt.title('Search Space (Log-Scaled Fitness)')
plt.xlabel('Solution', fontsize=label_font_size)
plt.ylabel(r'$\log_{10}$(Fitness)', fontsize=label_font_size)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xlim(100, 600)
plt.ylim(2.5, 5.6)
plt.grid(True)
plt.tight_layout()


# --- 2: Global best fitness per Generation ---
plt.figure(figsize=(8, 5))
plt.plot(best_fitness_per_gen.index, best_fitness_per_gen.values, label='Best per generation', color='orange', linewidth=linewidth)


# plt.title('GA Convergence Plot')
plt.xlabel('Generation', fontsize=label_font_size)
plt.ylabel('Global best fitness', fontsize=label_font_size)
plt.xticks(ticks=np.arange(num_generations+1), labels=np.arange(0, num_generations+1), fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xlim(1, num_generations +0.5)
plt.ylim(410, 480)
# plt.legend()
plt.grid(True)
plt.tight_layout()

# --- 3: Particle trajectory (solution per iteration) ---

plt.figure(figsize=(8, 5))

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


# --- 4: Fitness per iteration ---
df['fitness_log'] = np.log10(df['fitness'] + 1e-8)
plt.figure(figsize=(8, 5))
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
    dfs.append(df.rename(columns={'fitness': os.path.basename(file)}))

merged_df = dfs[0]
for df in dfs[1:]:
    merged_df = pd.merge(merged_df, df, on='iter', how='outer')

merged_df['min_fitness'] = merged_df.drop(columns='iter').min(axis=1).cummin()

num_iterations = len(merged_df['iter'])
print(num_iterations)

markers = itertools.cycle(('o', 's', '^', 'v', 'D', 'P', '*', 'X', 'H'))

# --- 1: Search space plot ---
plt.figure(figsize=(8, 5))
for log_file in log_files:
    df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", "buffer_size"])
    
    plt.scatter(df["buffer_size"], np.log10(df["fitness"]) + 1e-8, alpha=0.6,
                label=f'Instance starting point {df["buffer_size"][0]}',s=marker_size,  zorder=5, clip_on=False) # os.path.basename(log_file))

ax = plt.gca()
for spine in ax.spines.values():
    spine.set_zorder(2)

handles, labels = plt.gca().get_legend_handles_labels()
sorted_handles_labels = sorted(zip(labels, handles), key=lambda x: x[0])  # sort by label
sorted_labels, sorted_handles = zip(*sorted_handles_labels)
plt.legend(sorted_handles, sorted_labels, fontsize='x-small', loc='best')

plt.xlabel('Buffer size [kg]', fontsize=label_font_size)
plt.ylabel(r'$\log_{10}$(Fitness)', fontsize=label_font_size)
plt.xlim(100, 600)
plt.ylim(2.5, 5.6)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
# plt.title('L-BFGS-B: Search Space Exploration (Parallel)')
plt.grid(True, zorder=1)
plt.tight_layout()


# --- 3: Particle trajectory (solution per iteration) ---
plt.figure(figsize=(8,5))
for log_file, marker in zip(log_files, markers):
    df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", "buffer_size"])
    
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


# --- 3b: Particle trajectory (solution per iteration) (incl. fitness colorbar) ---
plt.figure(figsize=(8, 5))

all_fitness = []
all_buffer_sizes = []

# First pass: gather all fitness and buffer size values
for log_file in log_files:
    df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", "buffer_size"])
    all_fitness.extend(df["fitness"])
    all_buffer_sizes.extend(df["buffer_size"])

all_fitness = np.array(all_fitness)
all_buffer_sizes = np.array(all_buffer_sizes)
log_fitness_all = np.log10(all_fitness)

# Use actual fitness range
vmin = np.min(log_fitness_all)       # best fitness (lowest value)
# vcenter =  log_fitness_all[all_buffer_sizes.argmax()] # midpoint in log space
vmax = log_fitness_all[all_buffer_sizes.argmax()]
# vmax = np.max(log_fitness_all)       # worst fitness (highest value)
print(vmin)
# print(vcenter)
print(vmax)

norm = mcolors.LogNorm(vmin=vmin, vmax=vmax)
original_cmap = plt.cm.Oranges
new_cmap = mcolors.LinearSegmentedColormap.from_list(
    'subset_Oranges',
    original_cmap(np.linspace(0.4, 1.0, 256))
)

for log_file, marker in zip(log_files, markers):
    dfs.append(df.rename(columns={'fitness': os.path.basename(log_file)}))
    df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", "buffer_size"])
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


# --- 2: Global best fitness per Generation ---
plt.figure(figsize=(8, 5))
plt.plot(merged_df['iter'], merged_df['min_fitness'], label='Best per generation', color='orange', linewidth=linewidth)
plt.xlabel('Iteration', fontsize=label_font_size)
plt.ylabel('Global best fitness', fontsize=label_font_size)
ticks = np.arange(num_iterations + 1)
label_interval = 5 
tick_labels = [str(i) if i % label_interval == 0 else '' for i in ticks]
plt.xticks(ticks=ticks, labels=tick_labels, fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xlim(1, num_iterations +0.5)
plt.ylim(410, 480)
# plt.legend()
plt.grid(True)
plt.tight_layout()


# 4: Fitness per iteration
plt.figure(figsize=(8, 5))

for log_file in log_files:
    df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", "buffer_size"])

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
plt.show()

