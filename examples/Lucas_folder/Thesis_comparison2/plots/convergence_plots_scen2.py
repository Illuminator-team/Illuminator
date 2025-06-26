import pandas as pd
import matplotlib.pyplot as plt
import itertools
from mpl_toolkits.mplot3d import Axes3D  # Enables 3D plotting
import numpy as np
import ast 
import os
import glob
# Load the CSV file into a DataFrame

PSO_file_name = './examples/Lucas_folder/Thesis_comparison2/data/PSO_live_log_1w01_01_n9g100_seed42.csv'
GA_file_name = './examples/Lucas_folder/Thesis_comparison2/data/GA_live_log_1w01_01_n9g100_seed1.csv'
LBFGSB_file_name = './examples/Lucas_folder/Thesis_comparison2/data/LBFGSB_live_log_1w01_01_n9_g10.csv'
# LBFGSB2_folder = './examples/Lucas_folder/Thesis_comparison2/data/LBFGS2_1w01_01_eps_1e1'
LBFGSB2_folder = './examples/Lucas_folder/Thesis_comparison2/data/LBFGSB_p_1w_n9_g100_seed_no'
plot_saving_dir = 'C:/Users/31633/Dropbox/My PC (DESKTOP-84P3QQD)/Documents/Master_thesis/Thesis_figures/Results/Scenario2'
figs = []

label_font_size = 18
tick_font_size = 14
linewidth = 2
marker_size = 30

## PSO plots ##
df_pso = pd.read_csv(PSO_file_name)
df_pso['fitness'] = df_pso['fitness'].apply(lambda x: ast.literal_eval(x)[0])  # still a float
df_pso['solution'] = df_pso['solution'].apply(lambda x: ast.literal_eval(x))   # now a list like (x1, x2)


# -- Convergence Data --
best_fitness_per_gen = df_pso.groupby('generation')['fitness'].min()
global_best_fitness = best_fitness_per_gen.cummin()

pop_size = 9
num_gens = int(len(df_pso) / pop_size)

# Create 3D trajectory matrix: (particles, generations, variables)
particle_traject_matrix = np.zeros((pop_size, num_gens, 2))

for row_ix in range(pop_size):
    indices = np.arange(row_ix, len(df_pso), pop_size)
    for j, idx in enumerate(indices):
        particle_traject_matrix[row_ix, j, :] = df_pso['solution'].iloc[idx]

# --- Plot 1: Search Space colored by fitness ---
df_pso['x1'] = df_pso['solution'].apply(lambda x: x[0])
df_pso['x2'] = df_pso['solution'].apply(lambda x: x[1])
print(df_pso.loc[df_pso["fitness"].idxmin()])
# df_pso['fitness_log'] = np.log10(df_pso['fitness'] + 1e-8)
fig1_1a = plt.figure(figsize=(8, 6))
sc = plt.scatter(df_pso['x1'], df_pso['x2'], c=df_pso['fitness'], cmap='viridis', alpha=0.7, s=marker_size)
cbar = plt.colorbar(sc)
cbar.set_label('Fitness', fontsize=label_font_size)
plt.xlabel('Upper threshold [€/kWh]', fontsize=label_font_size)
plt.ylabel('Lower threshold [€/kWh]', fontsize=label_font_size)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xlim(-2, 2)
plt.ylim(-2, 2)
# plt.title('PSO: Search Space Exploration')
plt.grid(True)
plt.tight_layout()
figs.append((fig1_1a, 'PSO_scenario2_SearchSpace_x1x2.png'))

# --- Plot 1b: Search Space in 3d ---
fig1_1b = plt.figure(figsize=(8, 5))
ax = fig1_1b.add_subplot(111, projection='3d')

# Plot 3D scatter
sc = ax.scatter(df_pso['x1'], df_pso['x2'], df_pso['fitness'], c=df_pso['fitness'], cmap='viridis', alpha=0.7, s=marker_size)

# Label axes
ax.set_xlabel('Upper threshold [€/kWh]', fontsize=label_font_size)
ax.set_ylabel('Lower threshold [€/kWh]', fontsize=label_font_size)
ax.set_zlabel('Fitness', fontsize=label_font_size)
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
# ax.set_title('PSO: Search Space Exploration in 3D')
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
# Add colorbar
cbar = plt.colorbar(sc)
cbar.set_label('Fitness', fontsize=label_font_size)
plt.tight_layout()
figs.append((fig1_1b, 'PSO_scenario2_SearchSpace_3d.png'))

# --- Plot 1c: Search Space x1 ---
df_pso['x1'] = df_pso['solution'].apply(lambda x: x[0])
fig1_1c = plt.figure(figsize=(8, 6))
sc = plt.scatter(df_pso['x1'], df_pso['fitness'], alpha=0.7, s=marker_size) #, c=df_pso['fitness'], cmap='viridis')
# cbar = plt.colorbar(sc)
# cbar.set_label('Fitness', fontsize=label_font_size)
plt.xlabel('Upper threshold [€/kWh]', fontsize=label_font_size)
plt.ylabel('Fitness' , fontsize=label_font_size)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
# plt.title('PSO: Search Space Exploration x2')
plt.xlim(-2, 2)
plt.grid(True)
plt.tight_layout()
figs.append((fig1_1c, 'PSO_scenario2_SearchSpace_x1.png'))

# --- Plot 1d: Search Space x2 ---
df_pso['x2'] = df_pso['solution'].apply(lambda x: x[1])
fig1_1d = plt.figure(figsize=(8, 6))
sc = plt.scatter(df_pso['x2'], df_pso['fitness'], alpha=0.7, s=marker_size) #, c=df_pso['fitness'], cmap='viridis')
# cbar = plt.colorbar(sc)
# cbar.set_label('Fitness', fontsize=label_font_size)
plt.xlabel('Lower threshold [€/kWh]', fontsize=label_font_size)
plt.ylabel('Fitness' , fontsize=label_font_size)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
# plt.title('PSO: Search Space Exploration x2')
plt.xlim(-2, 2)
plt.grid(True)
plt.tight_layout()
figs.append((fig1_1d, 'PSO_scenario2_SearchSpace_x2.png'))

# --- Plot 2: Convergence over generations ---
fig1_2 = plt.figure(figsize=(8, 5))
plt.plot(best_fitness_per_gen.index, best_fitness_per_gen.values, label='Best per generation', color='orange', linewidth=2)
# plt.plot(global_best_fitness.index, global_best_fitness.values, label='Global best so far', color='blue', linestyle='--', linewidth=2)
# plt.title('PSO Convergence Plot')
plt.xlabel('Generation', fontsize=label_font_size)
plt.ylabel('Fitness', fontsize=label_font_size)
# plt.legend()
plt.xticks(ticks=np.arange(num_gens +1), labels=np.arange(0, num_gens+1), fontsize=tick_font_size)
plt.xlim(1, num_gens + 0.5)

plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.ylim(bottom=-65)
plt.grid(True)
plt.tight_layout()
figs.append((fig1_2, 'PSO_scenario2_global_fitness_per_gen.png'))

# --- Plot 3a: Particle trajectories x1 ---
fig1_3a = plt.figure(figsize=(8, 5))
for i in range(pop_size):
    plt.plot(particle_traject_matrix[i, :, 0], label=f'Particle {i+1}', linewidth=linewidth)
plt.xlabel('Generation', fontsize=label_font_size)
plt.ylabel('Upper threshold [€/kWh]', fontsize=label_font_size)
plt.xticks(ticks=np.arange(num_gens), labels=np.arange(1, num_gens+1), fontsize=tick_font_size)
plt.xlim(0, num_gens - 0.5)
plt.yticks(fontsize=tick_font_size)
plt.grid(True)
plt.legend()
figs.append((fig1_3a, 'PSO_scenario2_particle_trajcectory_solutionx1.png'))

# --- Plot 3b: Particle trajectories x2 ---
fig1_3b = plt.figure(figsize=(8, 5))
for i in range(pop_size):
    plt.plot(particle_traject_matrix[i, :, 1], label=f'Particle {i+1}', linewidth=linewidth)
plt.xlabel('Generation', fontsize=label_font_size)
plt.ylabel('Lower threshold [€/kWh]', fontsize=label_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xticks(ticks=np.arange(num_gens), labels=np.arange(1, num_gens+1), fontsize=tick_font_size)
plt.xlim(0, num_gens - 0.5)
plt.grid(True)
plt.legend()
figs.append((fig1_3b, 'PSO_scenario2_particle_trajcectory_solutionx2.png'))
# plt.show()

# --- Plot 3: Particle trajectory for x1 and x2 ---
# fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# # Plot x1
# for i in range(pop_size):
#     axes[0].plot(particle_traject_matrix[i, :, 0], label=f'Particle {i+1}')
# axes[0].set_title('PSO: Particle Trajectories: x1')
# axes[0].set_ylabel('x1 Value')
# axes[0].grid(True)
# axes[0].legend()

# # Plot x2
# for i in range(pop_size):
#     axes[1].plot(particle_traject_matrix[i, :, 1], label=f'Particle {i+1}', linestyle='--')
# axes[1].set_title('PSO: Particle Trajectories: x2')
# axes[1].set_xlabel('Generation')
# axes[1].set_ylabel('x2 Value')
# axes[1].grid(True)
# axes[1].legend()

# plt.tight_layout()





## GA plots ##

df_ga = pd.read_csv(GA_file_name)
df_ga['fitness'] = df_ga['fitness'].apply(lambda x: ast.literal_eval(x)[0])  # still a float
df_ga['solution'] = df_ga['solution'].apply(lambda x: ast.literal_eval(x))   # now a list like (x1, x2)


# -- Convergence Data --
best_fitness_per_gen = df_ga.groupby('generation')['fitness'].min()
global_best_fitness = best_fitness_per_gen.cummin()

pop_size = 9
num_gens = int(len(df_ga) / pop_size)

# Create 3D trajectory matrix: (particles, generations, variables)
particle_traject_matrix = np.zeros((pop_size, num_gens, 2))

for row_ix in range(pop_size):
    indices = np.arange(row_ix, len(df_ga), pop_size)
    for j, idx in enumerate(indices):
        particle_traject_matrix[row_ix, j, :] = df_ga['solution'].iloc[idx]

# --- Plot 1: Search Space colored by fitness ---
df_ga['x1'] = df_ga['solution'].apply(lambda x: x[0])
df_ga['x2'] = df_ga['solution'].apply(lambda x: x[1])
# df_ga['fitness_log'] = np.log10(df_ga['fitness'] + 1e-8)
fig2_1a = plt.figure(figsize=(8, 6))
sc = plt.scatter(df_ga['x1'], df_ga['x2'], c=df_ga['fitness'], cmap='viridis', alpha=0.7, s=marker_size)
cbar = plt.colorbar(sc)
cbar.set_label('Fitness', fontsize=label_font_size)
plt.xlabel('Upper threshold [€/kWh]', fontsize=label_font_size)
plt.ylabel('Lower threshold [€/kWh]', fontsize=label_font_size)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xlim(-2, 2)
plt.ylim(-2, 2)
# plt.title('GA: Search Space Exploration')
plt.grid(True)
plt.tight_layout()
figs.append((fig2_1a, 'GA_scenario2_SearchSpace_x1x2.png'))

# --- Plot 1: Search Space colored by fitness ---
df_pso['x1'] = df_pso['solution'].apply(lambda x: x[0])
df_pso['x2'] = df_pso['solution'].apply(lambda x: x[1])
print(df_pso.loc[df_pso["fitness"].idxmin()])
# df_pso['fitness_log'] = np.log10(df_pso['fitness'] + 1e-8)
fig1_1a = plt.figure(figsize=(8, 6))
sc = plt.scatter(df_pso['x1'], df_pso['x2'], c=df_pso['fitness'], cmap='viridis', alpha=0.7, s=marker_size)
cbar = plt.colorbar(sc)
cbar.set_label('Fitness', fontsize=label_font_size)
plt.xlabel('Upper threshold [€/kWh]', fontsize=label_font_size)
plt.ylabel('Lower threshold [€/kWh]', fontsize=label_font_size)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xlim(-2, 2)
plt.ylim(-2, 2)
# plt.title('PSO: Search Space Exploration')
plt.grid(True)
plt.tight_layout()

# --- Plot 1b: Search Space in 3d ---
fig2_1b = plt.figure(figsize=(8, 5))
ax = fig2_1b.add_subplot(111, projection='3d')

# Plot 3D scatter
sc = ax.scatter(df_ga['x1'], df_ga['x2'], df_ga['fitness'], c=df_ga['fitness'], cmap='viridis', alpha=0.7, s=marker_size)

# Label axesv
ax.set_xlabel('Upper threshold [€/kWh]', fontsize=label_font_size)
ax.set_ylabel('Lower threshold [€/kWh]', fontsize=label_font_size)
ax.set_zlabel('Fitness', fontsize=label_font_size)
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
# ax.set_title('PSO: Search Space Exploration in 3D')
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
# Add colorbar
cbar = plt.colorbar(sc)
cbar.set_label('Fitness', fontsize=label_font_size)
plt.tight_layout()
figs.append((fig2_1b, 'GA_scenario2_SearchSpace_3d.png'))

# --- Plot 1c: Search Space x1 ---
df_ga['x1'] = df_ga['solution'].apply(lambda x: x[0])
fig2_1c = plt.figure(figsize=(8, 6))
sc = plt.scatter(df_ga['x1'], df_ga['fitness'], alpha=0.7, s=marker_size) #, c=df_ga['fitness'], cmap='viridis')
# cbar = plt.colorbar(sc)
# cbar.set_label('Fitness', fontsize=label_font_size)
plt.xlabel('Upper threshold [€/kWh]', fontsize=label_font_size)
plt.ylabel('Fitness' , fontsize=label_font_size)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
# plt.title('PSO: Search Space Exploration x2')
plt.xlim(-2, 2)
plt.grid(True)
plt.tight_layout()
figs.append((fig2_1c, 'GA_scenario2_SearchSpace_x1.png'))

# --- Plot 1d: Search Space x2 ---
df_ga['x2'] = df_ga['solution'].apply(lambda x: x[1])
fig2_1d = plt.figure(figsize=(8, 6))
sc = plt.scatter(df_ga['x1'], df_ga['fitness'], alpha=0.7, s=marker_size) #, c=df_ga['fitness'], cmap='viridis')
# cbar = plt.colorbar(sc)
# cbar.set_label('Fitness', fontsize=label_font_size)
plt.xlabel('Lower threshold [€/kWh]', fontsize=label_font_size)
plt.ylabel('Fitness' , fontsize=label_font_size)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
# plt.title('PSO: Search Space Exploration x2')
plt.xlim(-2, 2)
plt.grid(True)
plt.tight_layout()
figs.append((fig2_1d, 'GA_scenario2_SearchSpace_x2.png'))

# --- Plot 2: Convergence over generations ---
fig2_2 = plt.figure(figsize=(8, 5))
plt.plot(best_fitness_per_gen.index, best_fitness_per_gen.values, label='Best per generation', color='orange', linewidth=linewidth)
# plt.plot(global_best_fitness.index, global_best_fitness.values, label='Global best so far', color='blue', linestyle='--', linewidth=linewidth)
# plt.title('GA Convergence Plot')
plt.xlabel('Generation', fontsize=label_font_size)
plt.ylabel('Fitness', fontsize=label_font_size)
# plt.legend()
num_gens_ga = int(len(df_ga) / pop_size)
ticks = np.arange(num_gens_ga + 1)
label_interval=1
tick_labels = [str(i) if i % label_interval == 0 else '' for i in ticks]
plt.xticks(ticks=ticks, labels=tick_labels, fontsize=tick_font_size)
plt.ylim(bottom=-65)
plt.yticks(fontsize=tick_font_size)
plt.xlim(1, num_gens + 0.5)
plt.grid(True)
plt.tight_layout()
figs.append((fig2_2, 'GA_scenario2_global_fitness_per_gen.png'))

# # --- Plot 3: Particle trajectory for x1 and x2 ---
# # Plot x1
# fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# # Scatter plot for x1
# for i in range(pop_size):
#     generations = range(particle_traject_matrix.shape[1])
#     x1_vals = particle_traject_matrix[i, :, 0]
#     axes[0].scatter(generations, x1_vals, s=10, color='red')  # s=10 controls marker size
# # axes[0].set_title('GA: Particle Trajectories: x1')
# axes[0].set_ylabel('x1 Value')
# axes[0].grid(True)

# # Scatter plot for x2
# for i in range(pop_size):
#     generations = range(particle_traject_matrix.shape[1])
#     x2_vals = particle_traject_matrix[i, :, 1]
#     axes[1].scatter(generations, x2_vals, s=10, marker='x', color='blue')
# # axes[1].set_title('GA: Particle Trajectories: x2')
# axes[1].set_xlabel('Generation')
# axes[1].set_ylabel('x2 Value')
# axes[1].grid(True)
# --- Plot 3a: Particle trajectories x1 ---
fig2_3a = plt.figure(figsize=(8, 5))
for i in range(pop_size):
    generations = range(particle_traject_matrix.shape[1])
    x1_vals = particle_traject_matrix[i, :, 0]
    plt.scatter(generations, x1_vals, s=marker_size, color='blue', alpha=0.7, zorder=5, clip_on=False)
ax = plt.gca()
for spine in ax.spines.values():
    spine.set_zorder(2)
plt.xlabel('Generation', fontsize=label_font_size)
plt.ylabel('Upper threshold [€/kWh]', fontsize=label_font_size)
plt.xticks(ticks=np.arange(num_gens), labels=np.arange(1, num_gens+1), fontsize=tick_font_size)
plt.xlim(0, num_gens - 0.5)
plt.yticks(fontsize=tick_font_size)
plt.grid(True, zorder=1)
figs.append((fig2_3a, 'GA_scenario2_particle_trajcectory_solutionx1.png'))

# --- Plot 3b: Particle trajectories x2 ---
fig2_3b = plt.figure(figsize=(8, 5))
for i in range(pop_size):
    generations = range(particle_traject_matrix.shape[1])
    x2_vals = particle_traject_matrix[i, :, 1]
    plt.scatter(generations, x2_vals, s=marker_size, color='blue', alpha=0.7, zorder=5, clip_on=False)
ax = plt.gca()
for spine in ax.spines.values():
    spine.set_zorder(2)
plt.xlabel('Generation', fontsize=label_font_size)
plt.ylabel('Lower threshold [€/kWh]', fontsize=label_font_size)
plt.xticks(ticks=np.arange(num_gens), labels=np.arange(1, num_gens+1), fontsize=tick_font_size)
plt.xlim(0, num_gens - 0.5)
plt.yticks(fontsize=tick_font_size)
plt.grid(True, zorder=1)
figs.append((fig2_3b, 'GA_scenario2_particle_trajcectory_solutionx2.png'))


# # --- Plot 3b: Particle trajectories x2 ---
# plt.figure(figsize=(8, 5))
# for i in range(pop_size):
#     plt.scatter(particle_traject_matrix[i, :, 1])
# plt.xlabel('Generation', fontsize=label_font_size)
# plt.ylabel('Upper threshold [€/kWh]', fontsize=label_font_size)
# plt.yticks(fontsize=tick_font_size)
# plt.xticks(ticks=np.arange(num_gens), labels=np.arange(1, num_gens+1), fontsize=tick_font_size)
# plt.xlim(0, num_gens - 0.5)
# plt.grid(True)
# plt.legend()

# plt.tight_layout()
# plt.show()

## LBFGSB plots ##

# df_ga = pd.read_csv(LBFGSB_file_name)

# # print(df_ga['solution'].head())

# df_ga['fitness'] = df_ga['fitness'].apply(lambda x: ast.literal_eval(x)[0])  # still a float
# df_ga['solution'] = df_ga['solution'].apply(lambda x: ast.literal_eval(x))   # now a list like (x1, x2)

# df_ga['x1'] = df_ga['solution'].apply(lambda x: x[0])
# df_ga['x2'] = df_ga['solution'].apply(lambda x: x[1])

# # --- Plot 1: Fitness vs Solution (Search Space) ---
# # df_ga['fitness_log'] = np.log10(df_ga['fitness'] + 1e-8)
# plt.figure(figsize=(8, 5))

# sc = plt.scatter(df_ga['x1'], df_ga['x2'], c=df_ga['fitness'], cmap='viridis', alpha=0.7)
# plt.colorbar(sc, label='Fitness')
# plt.xlabel('x1')
# plt.ylabel('x2')
# plt.title('L-BFGS-B: Search Space Exploration')
# plt.grid(True)
# plt.tight_layout()


# # --- Plot 2: Convergence ---
# plt.figure(figsize=(8, 5))

# num_iter = len(df_ga['fitness'])
# plt.plot(df_ga['fitness'])
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
from matplotlib.colors import Normalize

log_files = glob.glob(os.path.join(LBFGSB2_folder, "LBFGSB_live_log_*.csv"))


dfs = []

for file in log_files:
    df = pd.read_csv(file, skiprows=1, names=['iter', 'fitness', 'timestep', 'x1', 'x2'], usecols=['iter', 'fitness'])

    run_label = os.path.basename(file)
    df = df.rename(columns={'fitness': run_label})
    
    dfs.append(df)


merged_df = dfs[0]
for df in dfs[1:]:
    merged_df = pd.merge(merged_df, df, on='iter', how='outer')
df_lbfgsb = merged_df.copy()
merged_df['min_fitness'] = merged_df.drop(columns='iter').min(axis=1).cummin()


print(df_lbfgsb.head())
num_iterations = len(merged_df['iter'])


markers = itertools.cycle(('o', 's', '^', 'v', 'D', 'P', '*', 'X', 'H'))
all_fitness = []

for log_file in log_files:
    df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", 'timestep', "x1", "x2"])
    all_fitness.extend(df["fitness"].values)

vmin = np.min(all_fitness)
vmax = np.max(all_fitness)
norm = Normalize(vmin=vmin, vmax=vmax)

# --- Plot 1: Search Space Plot ---
fig3_1a = plt.figure(figsize=(8, 5))

for log_file, marker in zip(log_files, markers):
    df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", 'timestep', "x1", "x2"])
    
    plt.scatter(df["x1"], df["x2"], c=df["fitness"], cmap='viridis', norm=norm, alpha=0.7,
                s=marker_size, label=os.path.basename(log_file)) #, marker=marker,)

cbar = plt.colorbar()
cbar.set_label('Fitness', fontsize=label_font_size)
cbar.ax.yaxis.offsetText.set_visible(False)
# cbar.ax.tick_params(labelsize=tick_font_size)
plt.xlabel('Upper threshold [€/kWh]', fontsize=label_font_size)
plt.ylabel('Lower threshold [€/kWh]', fontsize=label_font_size)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xlim(-2, 2.5)
plt.ylim(-2, 2.5)
# plt.title('L-BFGS-B: Search Space Exploration (Parallel)')
plt.grid(True)
# plt.legend(fontsize='x-small', loc='best')
plt.tight_layout()
figs.append((fig3_1a, 'LBFGSB2_scenario2_SearchSpace_x1x2.png'))
# plt.figure(figsize=(8, 5))

# # sc = plt.scatter(df['x1'], df['x2'], c=df['fitness'], cmap='viridis', alpha=0.7, s=marker_size)
# cbar = plt.colorbar()
# cbar.set_label('Fitness', fontsize=label_font_size)
# plt.xlabel('Upper threshold [€/kWh]', fontsize=label_font_size)
# plt.ylabel('Lower threshold [€/kWh]', fontsize=label_font_size)
# plt.xticks(fontsize=tick_font_size)
# plt.yticks(fontsize=tick_font_size)
# plt.xlim(-2, 2)
# plt.ylim(-2, 2)
# plt.grid(True)
# plt.tight_layout()

# --- Plot 1b: 3d search space


# Plotting
fig3_1b = plt.figure(figsize=(8, 5))
ax = fig3_1b.add_subplot(111, projection='3d')

for log_file, marker in zip(log_files, markers):
    df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness",'timestep', "x1", "x2"])

    sc = ax.scatter(
        df["x1"], df["x2"], df['fitness'],
        c=df["fitness"], cmap='viridis', norm=norm,
        alpha=0.7, s=marker_size, label=os.path.basename(log_file)
    )

# Axis labels
ax.set_xlabel('Upper threshold [€/kWh]', fontsize=label_font_size)
ax.set_ylabel('Lower threshold [€/kWh]', fontsize=label_font_size)
ax.set_zlabel('Fitness', fontsize=label_font_size)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)

# Colorbar with global scale
cbar = plt.colorbar(sc)
cbar.set_label('Fitness', fontsize=label_font_size)

plt.tight_layout()
figs.append((fig3_1b, 'LBFGSB2_scenario2_SearchSpace_3d.png'))

# --- Plot 1c: Search space plot x1 ---
fig3_1c = plt.figure(figsize=(8, 5))
for log_file, marker in zip(log_files, markers):
    df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", 'timestep', "x1", "x2"])
    
    plt.scatter(df["x1"], df["fitness"], alpha=0.7,
                label=os.path.basename(log_file), s=marker_size, color='#1f77b4') #,c=df["fitness"], cmap='viridis', marker=marker, 

# plt.colorbar(label='Fitness')
plt.xlabel('Upper threshold [€/kWh]', fontsize=label_font_size)
plt.ylabel('Fitness', fontsize=label_font_size)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xlim(-2, 2.5)

# plt.title('L-BFGS-B: Search Space Exploration x2 (Parallel)')
plt.grid(True)
# plt.legend(fontsize='x-small', loc='best')
plt.tight_layout()
figs.append((fig3_1c, 'LBFGSB2_scenario2_SearchSpace_x1.png'))

# --- Plot 1d: Search space plot x2 ---
fig3_1d = plt.figure(figsize=(8, 5))
for log_file, marker in zip(log_files, markers):
    df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", 'timestep', "x1", "x2"])
    
    plt.scatter(df["x2"], df["fitness"], alpha=0.7,
                label=os.path.basename(log_file), s=marker_size, color='#1f77b4') #,c=df["fitness"], cmap='viridis', marker=marker, 

# plt.colorbar(label='Fitness')
plt.xlabel('Lower threshold [€/kWh]', fontsize=label_font_size)
plt.ylabel('Fitness', fontsize=label_font_size)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xlim(-2, 2.5)

# plt.title('L-BFGS-B: Search Space Exploration x2 (Parallel)')
plt.grid(True)
# plt.legend(fontsize='x-small', loc='best')
plt.tight_layout()
figs.append((fig3_1d, 'LBFGSB2_scenario2_SearchSpace_x2.png'))

# --- Plot 2: Convergence Plot ---
fig3_2 = plt.figure(figsize=(8, 5))

for log_file in log_files:
    df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", 'timestep', "x1", "x2"])

    if df.empty:
        print(f"Warning: {log_file} is empty or has no data rows.")
        continue  # <-- make sure this is INSIDE the for loop

    plt.plot(df['iter'], df['fitness'], label=f'Instance starting point {round(df["x1"][0], 2)}, {round(df["x1"][0], 2)}', zorder=4, linewidth=linewidth)
    plt.scatter(df['iter'].iloc[0], df['fitness'].iloc[0],
                color='red', edgecolor='black', s=marker_size/2, zorder=5, clip_on=False)
ax = plt.gca()
for spine in ax.spines.values():
    spine.set_zorder(2) 

plt.xlabel('Iteration', fontsize=label_font_size)
plt.ylabel('Fitness', fontsize=label_font_size)
ticks = np.arange(num_iterations + 1)
label_interval = 5 
tick_labels = [str(i) if i % label_interval == 0 else '' for i in ticks]
plt.xticks(ticks=ticks, labels=tick_labels, fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xlim(1, num_iterations + 0.5)
# plt.title('L-BFGS-B: Convergence Plot (Parallel)')
plt.grid(True, zorder=1)
plt.legend(fontsize='x-small', loc='best')
plt.tight_layout()
figs.append((fig3_2, 'LBFGSB2_scenario2_global_fitness_per_gen.png'))

# --- Plot 3a: Particle trajectory x1 ---
fig3_3a = plt.figure(figsize=(8,5))
for log_file, marker in zip(log_files, markers):
    df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", 'timestep', "x1", "x2"])
    
    plt.plot(df["iter"], df["x1"], label=os.path.basename(log_file), linewidth=linewidth)
    plt.scatter(df['iter'].iloc[0], df['x1'].iloc[0],
                color='red', edgecolor='black', s=marker_size/2, zorder=5, clip_on=False)
ax = plt.gca()
for spine in ax.spines.values():
    spine.set_zorder(2) 
# plt.colorbar(label='Fitness')
plt.xlabel('Iteration', fontsize=label_font_size)
plt.ylabel('Upper threshold [€/kWh]', fontsize=label_font_size)
ticks = np.arange(num_iterations + 1)
label_interval = 5 
tick_labels = [str(i) if i % label_interval == 0 else '' for i in ticks]
plt.xticks(ticks=ticks, labels=tick_labels, fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xlim(1, num_iterations+0.5)
plt.ylim(-2, 2.5)
# plt.title('L-BFGS-B: Solutions x1 (Parallel)')
plt.grid(True, zorder=1)
# plt.legend(fontsize='x-small', loc='best')
plt.tight_layout()
figs.append((fig3_3a, 'LBFGSB2_scenario2_particle_trajcectory_solutionx1.png'))

# --- Plot 3b: Particle trajectory x2 ---
fig3_3b = plt.figure(figsize=(8,5))
for log_file, marker in zip(log_files, markers):
    df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", 'timestep', "x1", "x2"])
    
    plt.plot(df["iter"], df["x2"], label=os.path.basename(log_file), linewidth=linewidth)
    plt.scatter(df['iter'].iloc[0], df['x2'].iloc[0],
                color='red', edgecolor='black', s=marker_size/2, zorder=5, clip_on=False)
ax = plt.gca()
for spine in ax.spines.values():
    spine.set_zorder(2) 
# plt.colorbar(label='Fitness')
plt.xlabel('Iteration', fontsize=label_font_size)
plt.ylabel('Lower threshold [€/kWh]', fontsize=label_font_size)
ticks = np.arange(num_iterations + 1)
label_interval = 5 
tick_labels = [str(i) if i % label_interval == 0 else '' for i in ticks]
plt.xticks(ticks=ticks, labels=tick_labels, fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.xlim(1, num_iterations+0.5)
plt.ylim(-2, 2.5)
# plt.title('L-BFGS-B: Solutions x1 (Parallel)')
plt.grid(True, zorder=1)
# plt.legend(fontsize='x-small', loc='best')
plt.tight_layout()
figs.append((fig3_3b, 'LBFGSB2_scenario2_particle_trajcectory_solutionx2.png'))

# # --- Plot 3a: Particle trajectory x1 ---
# plt.figure(figsize=(8,5))
# for log_file, marker in zip(log_files, markers):
#     df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", "x1", "x2"])
    
#     plt.scatter(df["iter"], df["x1"], c=df["fitness"], cmap='viridis', alpha=0.6,
#                 marker=marker, label=os.path.basename(log_file))
# plt.colorbar(label='Fitness')
# plt.xlabel('Iteration')
# plt.ylabel('Upper threshold [€/kWh]')
# # plt.title('L-BFGS-B: Solutions x1 (Parallel)')
# plt.grid(True)
# plt.legend(fontsize='x-small', loc='best')
# plt.tight_layout()

# # --- Plot 3a: Particle trajectory x2 ---
# plt.figure(figsize=(8,5))
# for log_file, marker in zip(log_files, markers):
#     df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", "x1", "x2"])
    
#     plt.scatter(df["iter"], df["x2"], c=df["fitness"], cmap='viridis', alpha=0.6,
#                 marker=marker, label=os.path.basename(log_file))
# plt.colorbar(label='Fitness')
# plt.xlabel('Iteration')
# plt.ylabel('Upper threshold [€/kWh]')
# # plt.title('L-BFGS-B: Solutions x2 (Parallel)')
# plt.grid(True)
# plt.legend(fontsize='x-small', loc='best')
# plt.tight_layout()


# fig, ax = plt.subplots(figsize=(8, 5))

# for log_file in log_files:
#     df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", "x1", "x2"])

#     if df.empty:
#         print(f"Warning: {log_file} is empty or has no data rows.")
#         continue

#     ax.plot(df['iter'], df['fitness'], label=os.path.basename(log_file), zorder=2)

# # Draw everything else
# ax.set_xlim(left=1)
# ax.set_xlabel('Iteration')
# ax.set_ylabel('Fitness')
# ax.set_title('L-BFGS-B: Convergence Plot (Parallel)')
# ax.grid(True, zorder=1)
# ax.legend(fontsize='x-small', loc='best')
# fig.tight_layout()

# # Redraw marker last to make it topmost
# for log_file in log_files:
#     df = pd.read_csv(log_file, skiprows=1, names=["iter", "fitness", "x1", "x2"])
#     if df.empty:
#         continue
#     ax.scatter(df['iter'].iloc[0], df['fitness'].iloc[0],
#                color='red', edgecolor='black', s=30, zorder=99)

# # Lower spine and background
# for spine in ax.spines.values():
#     spine.set_zorder(1)
# ax.patch.set_zorder(0)

# plt.show()

# save_all = input(f"Save all plots to {plot_saving_dir}? (y/n)").strip().lower() == 'y'
# if save_all:
#     os.makedirs(plot_saving_dir, exist_ok=True)

#     for fig, ffilename in figs:
#         path = os.path.join(plot_saving_dir, ffilename)
#         fig.savefig(path, dpi=300)
#         print(f"Saved {fig} as {ffilename}")

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
import ast


def tidy_population_df(df, algorithm_name):
    df = df.copy()

    # Only evaluate if the value is a string
    def parse_solution(val):
        if isinstance(val, str):
            return ast.literal_eval(val)
        return val  # already a list

    df['solution'] = df['solution'].apply(parse_solution)
    df['fitness'] = df['fitness'].apply(lambda x: x[0] if isinstance(x, list) else x)

    return pd.DataFrame({
        'generation': df['generation'],
        'x0': [sol[0] for sol in df['solution']],
        'x1': [sol[1] for sol in df['solution']],
        'fitness': df['fitness'],
        'algorithm': algorithm_name
    })


### -----------------------------------------
### 3. Convert L-BFGS-B to tidy format
### -----------------------------------------

def load_lbfgsb_folder(log_files):
    all_rows = []
    
    for filename in log_files:
        if not filename.endswith(".csv"):
            continue  # skip non-csv files
        df = pd.read_csv(filename, skiprows=1, names=["iter", "fitness", 'timestep', "x0", "x1"])
        for _, row in df.iterrows():
            all_rows.append({
                'generation': row['iter'],
                'x0': row['x0'],  # first solution value
                'x1': row['x1'],  # second solution value
                'fitness': row['fitness'],
                'algorithm': 'L-BFGS-B'
            })


    return pd.DataFrame(all_rows)

# ---------- Step 3: Sample ~7 Evenly Spaced Generations ----------
def filter_by_iterations(df, selected_iterations):
    """
    Filters the DataFrame for the specified iterations (generations).
    """
    return df[df['generation'].isin(selected_iterations)]

def plot_iterations_grid(df, selected_iterations, n_cols=None, figsize=(16, 10), cmap='viridis'):
    algorithms = df['algorithm'].unique()
    n_rows = len(algorithms)
    n_cols = n_cols if n_cols else len(selected_iterations)

    # Global axis limits
    # x_min, x_max = df['x0'].min(), df['x0'].max()
    # y_min, y_max = df['x1'].min(), df['x1'].max()
    x_min, x_max = -2, 2
    y_min, y_max = -2 ,2

    # Set up the main grid
    fig_matrix, axes = plt.subplots(n_rows, n_cols, figsize=figsize, sharex=True, sharey=True,
                             gridspec_kw={'wspace': 0.1, 'hspace': 0.1})

    # Ensure axes is 2D
    if n_rows == 1:
        axes = np.expand_dims(axes, axis=0)
    if n_cols == 1:
        axes = np.expand_dims(axes, axis=1)

    # Normalize colorbar range globally
    norm = plt.Normalize(df['fitness'].min(), df['fitness'].max())
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    for i, algo in enumerate(algorithms):
        df_algo = df[df['algorithm'] == algo]
        for j, gen in enumerate(selected_iterations):
            ax = axes[i, j]
            df_plot = df_algo[df_algo['generation'] == gen]

            sc = ax.scatter(df_plot['x0'], df_plot['x1'], c=df_plot['fitness'], cmap=cmap, norm=norm)

            ax.set_xlim(x_min, x_max)
            ax.set_ylim(x_min, y_max)
            
            # Titles on top row
            if i == 0:
                ax.set_title(f"Iter {gen}", fontsize=10)

            # Y-axis labels on leftmost column
            if j == 0:
                ax.set_yticks(ticks=np.linspace(y_min, y_max, 3), labels=np.linspace(y_min, y_max, 3).astype(int), fontsize=10)
                # ax.tick_params(axis='y', labelsize=8)
            # else:
            #     ax.set_yticklabels([])
            
            if j == n_cols-1:
                ax.yaxis.set_label_position("right")
                ax.set_ylabel(algo, fontsize=10)

            # X-axis labels on bottom row
            if i == n_rows - 1:
                # ax.set_xlabel("x0", fontsize=10)
                ax.set_xticks(ticks=np.linspace(x_min, x_max, 3), labels=np.linspace(x_min, x_max, 3).astype(int), fontsize=10)
                # ticks=np.arange(num_gens +1), labels=np.arange(0, num_gens+1), fontsize=tick_font_size)
                # ax.tick_params(axis='x', labelsize=8)
            else:
                ax.set_xticklabels([])

    # Add a single colorbar to the right
    cbar_ax = fig_matrix.add_axes([0.92, 0.15, 0.015, 0.7])
    cbar = fig_matrix.colorbar(sm, cax=cbar_ax)
    cbar.set_label("Fitness", fontsize=10)

    # Add common x and y labels for the whole figure
    fig_matrix.text(0.5, 0.04, "Upper threshold [€/kWh]", ha='center', fontsize=label_font_size)
    fig_matrix.text(0.04, 0.5, "Lower threshold [€/kWh]", va='center', rotation='vertical', fontsize=label_font_size)

    plt.tight_layout(rect=[0.05, 0.05, 0.9, 0.95])
    figs.append((fig_matrix, 'matrix_plot_all_algs.png'))
    plt.show()

df_pso_tidy = tidy_population_df(df_pso, 'PSO')
df_ga_tidy = tidy_population_df(df_ga, 'GA')
df_lbfgsb_tidy = load_lbfgsb_folder(log_files)


df_all = pd.concat([df_pso_tidy, df_ga_tidy, df_lbfgsb_tidy], ignore_index=True)

selected_iterations = [1, 5, 10, 15, 19, 20, 45]
df_sampled = filter_by_iterations(df_all, selected_iterations)

plot_iterations_grid(df_sampled, selected_iterations)


save_all = input(f"Save all plots to {plot_saving_dir}? (y/n)").strip().lower() == 'y'
if save_all:
    os.makedirs(plot_saving_dir, exist_ok=True)

    for fig, ffilename in figs:
        path = os.path.join(plot_saving_dir, ffilename)
        fig.savefig(path, dpi=300)
        print(f"Saved {fig} as {ffilename}")
# plt.show()