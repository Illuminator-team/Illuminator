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

# with open(scenario, 'r') as file:
#     data = yaml.load(file, Loader=yaml.FullLoader)
# model = next ((m for m in data['models'] if m['name'] == 'H2Buffer1'), None)
# print(model['parameters']['max_h2'])



### First optimization test (iterative with the max_h2)
# for i in range(max_iterations):
#     print(f'ITERATION {i}. Running scenario {scenario}')
#     command = ['illuminator', 'scenario', 'run', scenario]
#     process = subprocess.Popen(command)
#     index = 0
#     while True:
#         time.sleep(3)
        
#         # Reading the output CSV
#         while True:
#             try:
#                 df = pd.read_csv(output_path)
#                 break  # Break out of loop if file is successfully read
#             except pd.errors.EmptyDataError:
#                 print("Waiting for output file to be available...")
#                 time.sleep(1)  # Wait for 1 seconds before trying again
        
#         demand_met = True
#         output_length = len(df)-1
#         for l in range(index, output_length):
#             # with open(scenario, 'r') as file:
#             #     debug_data = yaml.load(file, Loader=yaml.FullLoader)
#             #     debug_model = next ((m for m in debug_data['models'] if m['name'] == 'H2Buffer1'), None)
#             # h2_max = debug_model['parameters']['max_h2']
#             print(f'row={l} demand={tot_demand[l]}') # , h2max={h2_max}')
#             if tot_demand[l] != round(df['H2Buffer1-0.time-based_0-h2_out'].iloc[l], 3):
#                 print(f"DEMAND NOT MET at row {l} namely tot_demand[{l}]={ tot_demand[l]} while h2_out ={df['H2Buffer1-0.time-based_0-h2_out'].iloc[l+1]}")
#                 demand_met = False
#                 break
#         index = output_length
#         if not demand_met:
#             process.terminate()
#             process.wait()
#             print('process terminated')
#             break
#     with open(scenario, 'r') as file:
#         data = yaml.load(file, Loader=yaml.FullLoader)
#         model = next ((m for m in data['models'] if m['name'] == 'H2Buffer1'), None)
#         model['parameters']['max_h2'] += 10

#     with open('examples/h2_system_example/h2_system_4_dynamic.yaml', 'w') as file:
#         yaml.dump(data, file)  # Write the modified YAML data back to the file

#     # time.sleep(1)   # This is to prevent reading the cached yaml
#     scenario = 'examples/h2_system_example/h2_system_4_dynamic.yaml'
    


### Trying actual optimization

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
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')

    # Scatter all solutions (gray)
    ax.scatter(F[:, 0], F[:, 1], F[:, 2], color='gray', alpha=0.5, label="All Solutions")

    # Extract Pareto front
    pareto_front = result.opt.get("F")
    
    # Scatter Pareto front solutions (red)
    ax.scatter(pareto_front[:, 0], pareto_front[:, 1], pareto_front[:, 2], 
               color='red', edgecolors='black', linewidth=1.2, label="Pareto Front")

    # Labels
    ax.set_xlabel("Total H2 Dump")
    ax.set_ylabel("SoC Violations")
    ax.set_zlabel("Buffer Size")
    ax.set_title("3D Pareto Front (NSGA-II)")
    ax.legend()
    
    plt.show()



# Defining the problem
class BufferProblem(Problem):
    def __init__(self):
        super().__init__(
            n_var=1,
            n_obj=3,
            n_const=0,
            xl=np.array([500]),
            xu=np.array([20000])
        )

    def _evaluate(self, X, out, *args, **kwargs):
        results = []
        algorithm = kwargs.get('algorithm', None)  # Get algorithm if available
        generation = algorithm.n_gen if algorithm else -1  # Get current generation or use -1 if missing
        iter_data_list = []

        for i, x in enumerate (X):
            dump_tot, soc_violations, buffer_size = run_sim(x[0])
            results.append([dump_tot, soc_violations, buffer_size])

            print(f"Iter {i}: buffer={buffer_size}, dump={dump_tot}, violations={soc_violations}")
            iter_data_list.append([generation, i, buffer_size, dump_tot, soc_violations])
        iter_data = pd.DataFrame(iter_data_list, columns=["Generation", "Population index", "Buffer seze", "Total dump", "SoC Violations"])
        iter_data.to_csv("examples/Lucas_folder/Optimization2/optimization_iter_results.csv", mode='a', index=False)

        results = np.array(results)
        out["F"] = np.column_stack([results[:, 0], results[:, 1], results[:, 2]])  # Objectives to minimize

algorithm = NSGA2(pop_size=5,
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

result = minimize(BufferProblem(), 
                  algorithm,
                    termination=("n_gen", 3),  # Stop after x generations
                    seed=1,
                    verbose=True
                )



save_pareto_solutions(result)
plot_pareto(result)

print(f'Optmial buffer size is: {result.X[0]}')