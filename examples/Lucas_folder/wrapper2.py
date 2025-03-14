import pandas as pd
import subprocess
import time
import yaml
import os
from scipy.optimize import minimize


scenario = 'examples/h2_system_example/h2_system_4.yaml'
output_path = 'examples/h2_system_example/h2_system_example4.csv.'
dump_col = 'H2_controller-0.time-based_0-dump'
soc_col = 'H2Buffer1-0.time-based_0-soc'
min_soc = 10
max_iterations = 6

demand1 = pd.read_csv('./examples/h2_system_example/demand1_generated.csv', header=1)['demand']
demand2 = pd.read_csv('./examples/h2_system_example/demand2_generated.csv', header=1)['demand']
tot_demand = (demand1+demand2).round(3)

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

def run_sim():

    print(f'Running scenario {scenario}')
    command = ['illuminator', 'scenario', 'run', scenario]
    process = subprocess.Popen(command)

    index = 0
    while True:
        time.sleep(3)   # check soc every 3sec
        while True:
            try:
                df = pd.read_csv(output_path)
                break
            except pd.errors.EmptyDataError:
                time.sleep(1)  # Wait and retry
                continue 

        output_length = len(df)-1
        for l in range(index, output_length):
            print(f'line {l}, soc={df[soc_col].iloc[l]}')
            if df[soc_col].iloc[l] < min_soc:
                process.terminate()
                process.wait()
                return True
        if process.poll() is not None:
            break
        index = output_length

    return False


def objective(parameter):
    parameter = float(parameter[0])
    global scenario
    print(f'Calculating objective with buffer size {parameter}')
    with open(scenario, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
        model = next((m for m in data['models'] if m['name'] == 'H2Buffer1'), None)
        model['parameters']['h2_capacity_tot'] = parameter
        

    with open('examples/h2_system_example/h2_system_4_dynamic.yaml', 'w') as file:
        yaml.dump(data, file)  # Write the modified YAML data back to the file

    scenario = 'examples/h2_system_example/h2_system_4_dynamic.yaml'
    soc_violation = run_sim()
    
    if soc_violation:
        print('soc violated')
        return 1e8
    
    while True:
        try:
            df = pd.read_csv(output_path)
            break  # Break out of loop if file is successfully read
        except pd.errors.EmptyDataError:
            print("Waiting for output file to be available...")
            time.sleep(1)  # Wait for 1 seconds before trying again
    dump_tot = df[dump_col].sum()
    print(f'for size={parameter}, dump={dump_tot}')
    return dump_tot

scenario = 'examples/h2_system_example/h2_system_4_dynamic.yaml'
result = minimize(objective, x0=[200], bounds=[(10,1500)], method='L-BFGS-B')

print(f'Optmial buffer size is: {result.x[0]}')