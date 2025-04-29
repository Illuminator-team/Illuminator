import pandas as pd
import matplotlib.pyplot as plt
import ast


data = pd.read_csv('.\examples\Lucas_folder\Optimization_project\PSO_live_log.csv')
n_pop = 3  # number of population members
fitness_lists = [[] for _ in range(n_pop)]  # initialize empty lists

for idx, val in enumerate(data['fitness']):
    fitness_val = ast.literal_eval(val)[0]
    fitness_lists[idx % n_pop].append(fitness_val)

generations = list(range(1, len(fitness_lists[0]) + 1))  # x-axis: generations starting from 1

for i, fitness in enumerate(fitness_lists):
    plt.plot(generations, fitness, label=f"p{i+1}")

plt.xlabel("Generation")
plt.ylabel("Fitness")
plt.legend()
plt.show()
    