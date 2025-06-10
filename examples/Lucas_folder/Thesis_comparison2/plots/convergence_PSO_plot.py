import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Enables 3D plotting
import numpy as np
import ast 
# Load the CSV file into a DataFrame
# PSO_file_name = './examples/Lucas_folder/Thesis_comparison2/data/PSO_live_log_1d01_01_n9g10.csv'
PSO_file_name = './examples/Lucas_folder/Thesis_comparison2/data/PSO_live_log_1w01_01_n9g10.csv'
GA_file_name = './examples/Lucas_folder/Thesis_comparison2/data/GA_live_log_1w01_01_n9_g10.csv'
LBFGSB_file_name = './examples/Lucas_folder/Thesis_comparison2/data/LBFGSB_live_log1.csv'

df = pd.read_csv(PSO_file_name)
df['fitness'] = df['fitness'].apply(lambda x: ast.literal_eval(x)[0])  # still a float
df['solution'] = df['solution'].apply(lambda x: ast.literal_eval(x))   # now a list like (x1, x2)


# -- Convergence Data --
best_fitness_per_gen = df.groupby('generation')['fitness'].min()
global_best_fitness = best_fitness_per_gen.cummin()

pop_size = 9
num_gens = int(len(df) / pop_size)

# Create 3D trajectory matrix: (particles, generations, variables)
particle_traject_matrix = np.zeros((pop_size, num_gens, 2))

for row_ix in range(pop_size):
    indices = np.arange(row_ix, len(df), pop_size)
    for j, idx in enumerate(indices):
        particle_traject_matrix[row_ix, j, :] = df['solution'].iloc[idx]

# --- Plot 1: Search Space colored by fitness ---
df['x1'] = df['solution'].apply(lambda x: x[0])
df['x2'] = df['solution'].apply(lambda x: x[1])
# df['fitness_log'] = np.log10(df['fitness'] + 1e-8)
plt.figure(figsize=(8, 6))
sc = plt.scatter(df['x1'], df['x2'], c=df['fitness'], cmap='viridis', alpha=0.7)
plt.colorbar(sc, label='Fitness')
plt.xlabel('x1')
plt.ylabel('x2')
plt.title('PSO: Search Space Exploration')
plt.grid(True)
plt.tight_layout()

# --- Plot 1b: Search Space in 3d ---
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

# Plot 3D scatter
sc = ax.scatter(df['x1'], df['x2'], df['fitness'], c=df['fitness'], cmap='viridis', alpha=0.7)

# Label axes
ax.set_xlabel('x1')
ax.set_ylabel('x2')
ax.set_zlabel('Fitness')
ax.set_title('PSO: Search Space Exploration in 3D')

# Add colorbar
fig.colorbar(sc, ax=ax, label='Fitness')

plt.tight_layout()

# --- Plot 2: Convergence over generations ---
plt.figure(figsize=(8, 5))
plt.plot(best_fitness_per_gen.index, best_fitness_per_gen.values, label='Best per generation', color='orange', linewidth=2)
plt.plot(global_best_fitness.index, global_best_fitness.values, label='Global best so far', color='blue', linestyle='--', linewidth=2)
plt.title('PSO Convergence Plot')
plt.xlabel('Generation')
plt.ylabel('Fitness')
plt.legend()
plt.grid(True)
plt.tight_layout()

# --- Plot 3: Particle trajectory for x1 and x2 ---
fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Plot x1
for i in range(pop_size):
    axes[0].plot(particle_traject_matrix[i, :, 0], label=f'Particle {i+1}')
axes[0].set_title('PSO: Particle Trajectories: x1')
axes[0].set_ylabel('x1 Value')
axes[0].grid(True)
axes[0].legend()

# Plot x2
for i in range(pop_size):
    axes[1].plot(particle_traject_matrix[i, :, 1], label=f'Particle {i+1}', linestyle='--')
axes[1].set_title('PSO: Particle Trajectories: x2')
axes[1].set_xlabel('Generation')
axes[1].set_ylabel('x2 Value')
axes[1].grid(True)
axes[1].legend()

plt.tight_layout()
# plt.show()

## GA plots ##

df = pd.read_csv(GA_file_name)
df['fitness'] = df['fitness'].apply(lambda x: ast.literal_eval(x)[0])  # still a float
df['solution'] = df['solution'].apply(lambda x: ast.literal_eval(x))   # now a list like (x1, x2)


# -- Convergence Data --
best_fitness_per_gen = df.groupby('generation')['fitness'].min()
global_best_fitness = best_fitness_per_gen.cummin()

pop_size = 9
num_gens = int(len(df) / pop_size)

# Create 3D trajectory matrix: (particles, generations, variables)
particle_traject_matrix = np.zeros((pop_size, num_gens, 2))

for row_ix in range(pop_size):
    indices = np.arange(row_ix, len(df), pop_size)
    for j, idx in enumerate(indices):
        particle_traject_matrix[row_ix, j, :] = df['solution'].iloc[idx]

# --- Plot 1: Search Space colored by fitness ---
df['x1'] = df['solution'].apply(lambda x: x[0])
df['x2'] = df['solution'].apply(lambda x: x[1])
# df['fitness_log'] = np.log10(df['fitness'] + 1e-8)
plt.figure(figsize=(8, 6))
sc = plt.scatter(df['x1'], df['x2'], c=df['fitness'], cmap='viridis', alpha=0.7)
plt.colorbar(sc, label='Fitness')
plt.xlabel('x1')
plt.ylabel('x2')
plt.title('GA: Search Space Exploration')
plt.grid(True)
plt.tight_layout()

# --- Plot 1b: Search Space in 3d ---
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

# Plot 3D scatter
sc = ax.scatter(df['x1'], df['x2'], df['fitness'], c=df['fitness'], cmap='viridis', alpha=0.7)

# Label axes
ax.set_xlabel('x1')
ax.set_ylabel('x2')
ax.set_zlabel('Fitness')
ax.set_title('GA: Search Space Exploration in 3D')

# Add colorbar
fig.colorbar(sc, ax=ax, label='Fitness')

plt.tight_layout()

# --- Plot 2: Convergence over generations ---
plt.figure(figsize=(8, 5))
plt.plot(best_fitness_per_gen.index, best_fitness_per_gen.values, label='Best per generation', color='orange', linewidth=2)
plt.plot(global_best_fitness.index, global_best_fitness.values, label='Global best so far', color='blue', linestyle='--', linewidth=2)
plt.title('GA Convergence Plot')
plt.xlabel('Generation')
plt.ylabel('Fitness')
plt.legend()
plt.grid(True)
plt.tight_layout()

# --- Plot 3: Particle trajectory for x1 and x2 ---
# Plot x1
fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Scatter plot for x1
for i in range(pop_size):
    generations = range(particle_traject_matrix.shape[1])
    x1_vals = particle_traject_matrix[i, :, 0]
    axes[0].scatter(generations, x1_vals, s=10, color='red')  # s=10 controls marker size
axes[0].set_title('GA: Particle Trajectories: x1')
axes[0].set_ylabel('x1 Value')
axes[0].grid(True)

# Scatter plot for x2
for i in range(pop_size):
    generations = range(particle_traject_matrix.shape[1])
    x2_vals = particle_traject_matrix[i, :, 1]
    axes[1].scatter(generations, x2_vals, s=10, marker='x', color='blue')
axes[1].set_title('GA: Particle Trajectories: x2')
axes[1].set_xlabel('Generation')
axes[1].set_ylabel('x2 Value')
axes[1].grid(True)

plt.tight_layout()
plt.show()

# # LBFGSB plots

# df = pd.read_csv(LBFGSB_file_name)
# # --- Plot 1: Fitness vs Solution (Search Space) ---
# df['fitness_log'] = np.log10(df['fitness'] + 1e-8)
# plt.figure(figsize=(8, 5))
# plt.scatter(df['solution'], df['fitness_log'], alpha=0.6, s=20, color='purple')
# plt.title('Search Space (Log-Scaled Fitness)')
# plt.xlabel('Solution')
# plt.ylabel('Log(Fitness)')
# plt.grid(True)
# plt.tight_layout()


# # --- Plot 3: Particle trajectory ---
# plt.figure(figsize=(8, 5))

# num_iter = len(df['solution'])
# plt.plot(df['solution'])
# plt.xticks(ticks=np.arange(num_iter), labels=np.arange(1, num_iter + 1))
# plt.title('Trajectory Plot')
# plt.xlabel('Iteration')
# plt.ylabel('Solution')
# # plt.legend()
# plt.grid(True)
# plt.tight_layout()

# plt.show()