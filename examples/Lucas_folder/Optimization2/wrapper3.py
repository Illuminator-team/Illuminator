import pandas as pd
import subprocess
import time
import yaml
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.core.problem import Problem
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM


# 
# Multi objective optimization

# scenario = 'examples/h2_system_example/h2_system_4.yaml'
output_path = 'examples/Lucas_folder/Optimization2/h2_system_example4_3.csv'
dump_col = 'H2_controller-0.time-based_0-dump'
soc_col = 'H2Buffer1-0.time-based_0-soc'
min_soc = 10
max_iterations = 6

demand1 = pd.read_csv('./examples/h2_system_example/demand1_generated.csv', header=1)['demand']
demand2 = pd.read_csv('./examples/h2_system_example/demand2_generated.csv', header=1)['demand']
tot_demand = (demand1+demand2).round(0)

### Trying multiobjective

def run_sim(buffer_size):
    global scenario
    # Update scenario
    with open(scenario, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    for model in data["models"]:
        if model["name"] == "H2Buffer1":
            model["parameters"]["h2_capacity_tot"] = float(buffer_size)

    with open(scenario, 'w') as file:
        yaml.dump(data, file)
    

    print(f'Running scenario {scenario}')
    command = ['illuminator', 'scenario', 'run', scenario]
    process = subprocess.Popen(command)

    while True:
        if process.poll() is not None:
            
            while True:
                try:
                    time.sleep(2)
                    df = pd.read_csv(output_path)
                    break
                except pd.errors.EmptyDataError:
                    time.sleep(1)  # Wait and retry
                    continue
            dump_tot = df[dump_col].sum()
            soc_violations = (df[soc_col] < min_soc).sum()
            break
            
    return dump_tot, soc_violations, buffer_size


def save_pareto_solutions(result):
    F = result.F  # Objective values (Dump, SoC Violations, Buffer Size)
    X = result.X  # Decision variable (Buffer size)
    
    df = pd.DataFrame(np.column_stack([X, F]), columns=['Buffer_Size', 'Dump', 'SoC_Violations', 'Buffer_Size_Obj'])
    df.to_csv("examples/Lucas_folder/Optimization2/pareto_solutions.csv", index=False)
    print("Pareto solutions saved!")

def plot_pareto(result):
    F = result.F  # Objective values (Dump, SoC Violations, Buffer Size)
    print("DEBUG: F =", F)

    # Extract relevant objectives (SoC Violations vs. Buffer Size)
    fig, ax = plt.subplots(figsize=(8, 6))

    # As it seems that all solutions provided by res.F seem to be pareto optimal (4 solutions are printed)
    # while i run 4gens of 5 pop size I now plot solutions found in the iteration csv

    dfx = pd.read_csv('examples/Lucas_folder/Optimization2/optimization_iter_results.csv')


# Plot all solutions
    ax.scatter(dfx["Buffer size"], dfx['SoC Violations'], color='blue', label='All Solutions', zorder=2, alpha=0.5)
    # # Scatter all solutions (gray)
    # ax.scatter(F[:, 2], F[:, 1], color='blue', alpha=0.5, label="All Solutions")  # (Buffer Size, SoC Violations)

    # Extract Pareto front
    pareto_front = result.opt.get("F")
    
    # Scatter Pareto front solutions (red)
    ax.scatter(pareto_front[:, 2], pareto_front[:, 1], color='red', edgecolors='black', linewidth=1.2, label="Pareto Front", zorder=3, alpha=0.5)

    # Labels
    ax.set_xlabel("Buffer Size")
    ax.set_ylabel("SoC Violations")
    ax.set_title("Pareto Front (NSGA-II)")
    ax.legend()
    
    plt.grid()
    plt.show()

def track_generation_results(iter_df):
    csv_file = "examples/Lucas_folder/Optimization2/optimization_iter_results.csv"
    columns=["Generation", "Population index", "Buffer size", "Total dump", "SoC Violations"]
    if  (iter_df.iloc[:, 0] == 0).all():
        iter_df.to_csv(csv_file, header=columns, index=False, mode='w')
    else:
        iter_df.to_csv(csv_file, mode='a', header=False, index=False)
    

# Defining the problem
class BufferProblem(Problem):
    def __init__(self):
        super().__init__(
            n_var=1,
            n_obj=3,
            n_const=0,
            xl=np.array([2000]),
            xu=np.array([40000])
        )

    def _evaluate(self, X, out, *args, **kwargs):
        global generation
        results = []
        iter_data_list = []

        for i, x in enumerate (X):
            dump_tot, soc_violations, buffer_size = run_sim(x[0])
            results.append([dump_tot, soc_violations, buffer_size])

            print(f"Iter {i}: buffer={buffer_size}, dump={dump_tot}, violations={soc_violations}")
            iter_data_list.append([generation, i, buffer_size, dump_tot, soc_violations])
        iter_data = pd.DataFrame(iter_data_list)
        track_generation_results(iter_data)
        results = np.array(results)
        out["F"] = np.column_stack([results[:, 0], results[:, 1], results[:, 2]])  # Objectives to minimize
        generation += 1

algorithm = NSGA2(pop_size=10,
                  sampling=FloatRandomSampling(),
                    crossover=SBX(prob=0.9, eta=15),
                    mutation=PM(eta=20),
                    eliminate_duplicates=True
                  )

original_scenario = 'examples/h2_system_example/h2_system_4.yaml'
scenario = 'examples/Lucas_folder/Optimization2/h2_system_4_3_dynamic.yaml'


os.makedirs(os.path.dirname(scenario), exist_ok=True)
# Read the original YAML file
with open(original_scenario, 'r') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)

# Write the data to the new temporary YAML file
with open(scenario, 'w') as file:
    yaml.dump(data, file)

generation = 0 

result = minimize(BufferProblem(), 
                  algorithm,
                    termination=("n_gen", 10),  # Stop after x generations
                    seed=1,
                    verbose=True
                )


time.sleep(3)
save_pareto_solutions(result)
plot_pareto(result)

print(f'Optmial buffer size is: {result.X[0]}')