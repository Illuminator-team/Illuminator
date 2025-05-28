import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import ast 
# Load the CSV file into a DataFrame
file_name = './examples/Lucas_folder/Thesis_comparison1/data/PSO_live_log_try_3.csv'

df = pd.read_csv(file_name)

# Convert strings to floats
df['fitness'] = df['fitness'].apply(lambda x: ast.literal_eval(x)[0])
df['solution'] = df['solution'].apply(lambda x: ast.literal_eval(x)[0])

# -- Convergence Data --
best_fitness_per_gen = df.groupby('generation')['fitness'].min()
global_best_fitness = best_fitness_per_gen.cummin()

pop_size = 30

particle_traject_matrix = np.zeros((pop_size, int(len(df['fitness'])/pop_size)))
print(particle_traject_matrix)

for row_ix in range(pop_size):
    indices = np.arange(row_ix, len(df['fitness']), pop_size)
    particle_traject_matrix[row_ix] = indices
    # print(indices)

print(particle_traject_matrix)
for i in range(particle_traject_matrix.shape[0]):
    for j in range(particle_traject_matrix.shape[1]):
        particle_traject_matrix[i,j] = df['fitness'][int(particle_traject_matrix[i,j])]

# --- Plot 1: Fitness vs Solution (Search Space) ---
df['fitness_log'] = np.log10(df['fitness'] + 1e-8)
plt.figure(figsize=(8, 5))
plt.scatter(df['solution'], df['fitness_log'], alpha=0.6, s=20, color='purple')
plt.title('Search Space (Log-Scaled Fitness)')
plt.xlabel('Solution')
plt.ylabel('Log(Fitness)')
plt.grid(True)
plt.tight_layout()


# --- Plot 2: Best Fitness per Generation ---
plt.figure(figsize=(8, 5))
plt.plot(best_fitness_per_gen.index, best_fitness_per_gen.values, label='Best per generation', color='orange', linewidth=2)
plt.plot(global_best_fitness.index, global_best_fitness.values, label='Global best so far', color='blue', linestyle='--', linewidth=2)
plt.title('PSO Convergence Plot')
plt.xlabel('Generation')
plt.ylabel('Fitness')
plt.legend()
plt.grid(True)
plt.tight_layout()


# --- Plot 3: Particle trajectory ---
plt.figure(figsize=(8, 5))
for particle in range(pop_size):
    plt.plot((particle_traject_matrix[particle][:]), label=f'particle {particle+1}')
num_generations = particle_traject_matrix.shape[1]
plt.xticks(ticks=np.arange(num_generations), labels=np.arange(1, num_generations + 1))
plt.title('Particle Trajectory Plot')
plt.xlabel('Generation')
plt.ylabel('Solution')
# plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()