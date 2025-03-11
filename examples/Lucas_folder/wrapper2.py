import pandas as pd
import subprocess
import time
import yaml
import os


scenario = 'examples\h2_system_example\h2_system_4.yaml'
output_path = 'examples\h2_system_example\h2_system_example3.csv.'
dump_col = 'Controller-0.time-based_0-dump'
max_iterations = 3

demand1 = pd.read_csv('./examples/h2_system_example/demand1_generated.csv', header=1)['demand']
demand2 = pd.read_csv('./examples/h2_system_example/demand2_generated.csv', header=1)['demand']
tot_demand = (demand1+demand2).round(3)

# print(demand1)


# with open(scenario, 'r') as file:
#     data = yaml.load(file, Loader=yaml.FullLoader)
# model = next ((m for m in data['models'] if m['name'] == 'H2Buffer1'), None)
# model['parameters']['h2_capacity_tot'] = 
# print(model)
# This runs the Illuminator for the defined scenario
command = ['illuminator', 'scenario', 'run', scenario]


for i in range(max_iterations):
    process = subprocess.Popen(command)
    index = 0
    while True:
        time.sleep(3)
        
        # Reading the output CSV
        while True:
            try:
                df = pd.read_csv(output_path)
                break  # Break out of loop if file is successfully read
            except pd.errors.EmptyDataError:
                print("Waiting for output file to be available...")
                time.sleep(1)  # Wait for 1 second before trying again
        # df = pd.read_csv(output_path)
        demand_met = True
        output_length = len(df)-1
        for l in range(index, output_length):
            print(l)
            if tot_demand[l] != round(df['H2Buffer1-0.time-based_0-h2_out'].iloc[l+1], 3):
                print(f"DEMAND NOT MET at row {l}\n namely tot_demand[{l}]={ tot_demand[l]} while h2_out ={df['H2Buffer1-0.time-based_0-h2_out'].iloc[l+1]}")
                demand_met = False
                break
        index = output_length
        if not demand_met:
            process.terminate()
            process.wait()
            print('process terminated')
            break
    with open(scenario, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
        model = next ((m for m in data['models'] if m['name'] == 'H2Buffer1'), None)
        model['parameters']['max_h2'] += 10

    # THIS CHANGES THE YAML, MUST SPECIFY OTHER FILE
    with open(scenario, 'w') as file:
        yaml.dump(data, file)  # Write the modified YAML data back to the file

    





# print(df['H2_controller-0.time-based_0-dump'].head)

# print(h2_deficit)
# print(h2_surplus)

# for i in range(max(max_iterations)):
#     for 
