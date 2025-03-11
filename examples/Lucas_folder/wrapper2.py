import pandas as pd
import subprocess
import time
import yaml
# import yaml


scenario = 'examples\h2_system_example\h2_system_4.yaml'
output_path = 'examples\h2_system_example\h2_system_example3.csv.'
dump_col = 'Controller-0.time-based_0-dump'
max_iterations = 5

with open(scenario, 'r') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)
model = next ((m for m in data['models'] if m['name'] == 'H2Buffer1'), None)
print(model)
# This runs the Illuminator for the defined scenario
# command = ['illuminator', 'scenario', 'run', scenario]


# for i in range(max_iterations):
#     process = subprocess.Popen(command)

#     # Wait for setup time
#     time.sleep(3)



# Reading the output CSV
df = pd.read_csv(output_path)




print(df['H2_controller-0.time-based_0-dump'].head)

# print(h2_deficit)
# print(h2_surplus)

# for i in range(max(max_iterations)):
#     for 
