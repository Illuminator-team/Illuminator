import pandas as pd
import subprocess

scenario = 'examples\h2_system_example\h2_system_1.yaml'
output_path = 'examples\h2_system_example\h2_system_example.csv.'
dump_col = 'Controller-0.time-based_0-dump'

# This runs the Illuminator for the defined scenario
command = ['illuminator', 'scenario', 'run', scenario]
subprocess.run(command, check=True)
 
# Reading the output CSV
df = pd.read_csv(output_path)

# Calulation of the hydrogen surplus and deficit
h2_deficit = df[df[dump_col] < 0][dump_col].sum()
h2_surplus = df[df[dump_col] > 0][dump_col].sum()



print(df['Controller-0.time-based_0-dump'])
print(h2_deficit)
print(h2_surplus)
