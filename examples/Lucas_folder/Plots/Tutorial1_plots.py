import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

output_path = 'out_Tutorial1.csv'
dump_col = 'H2_controller-0.time-based_0-dump'
# This runs the Illuminator for the defined scenario
# command = ['illuminator', 'scenario', 'run', scenario]
# subprocess.run(command, check=True)

# Reading the output CSV
df = pd.read_csv(output_path)
# df2 = pd.read_csv('examples/h2_system_example/thermolyzer_replacement_generated.csv', header=1)

soc = df['Battery1-0.time-based_0-soc']

demand = df['Load1-0.time-based_0-load_dem']
pv = df['PV1-0.time-based_0-pv_gen']
wind = df['Wind1-0.time-based_0-wind_gen']
dump = df['Controller1-0.time-based_0-dump']
battery_power = df['Controller1-0.time-based_0-flow2b']

xticks = list(range(0, len(df)+4, 4))  # one tick every hour
xlabels = [str(h) for h in range(len(xticks))]  
plt.xticks(ticks=xticks, labels=xlabels)
plt.xlabel('Hour')
plt.ylabel('Power [kW]')

battery_power[battery_power > 0] = 0
battery_power = -battery_power
plt.figure(1)

plt.plot(battery_power, label='Battery power')
plt.gca().set_xlim(left=0)
plt.ylim([0, 2])
# plt.gca().set_ylim(bottom=0)
# plt.plot(pv, label='pv')
# plt.plot(wind, label='wind')

plt.plot(pv+wind, label='RES generation')
plt.plot(demand, label='Demand')
# plt.plot(dump, label='dump')
plt.legend()
plt.figure(2)
plt.gca().set_xlim(left=0)
plt.ylim([40, 100])
plt.xticks(ticks=xticks, labels=xlabels)
plt.xlabel('Hour')
plt.ylabel('SoC [%]')
plt.plot(soc, label='Battery SoC')
plt.show()