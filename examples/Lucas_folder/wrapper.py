import pandas as pd
import subprocess
import matplotlib.pyplot as plt
# import yaml


scenario = 'examples/Tutorial3/Tutorial_physical_congestion_RES.yaml'
output_path = './out_Tutorial_RES.csv'
dump_col = 'Controller1-0.time-based_0-dump'

# This runs the Illuminator for the defined scenario
# command = ['illuminator', 'scenario', 'run', scenario]
# subprocess.run(command, check=True)
 
# Reading the output CSV
df = pd.read_csv(output_path)
df2 = pd.read_csv('examples/h2_system_example/thermolyzer_replacement_generated.csv', header=1)
generation = df2['h2_gen']


# Calulation of the hydrogen surplus and deficit
h2_deficit = df[df[dump_col] < 0][dump_col].sum()
h2_surplus = df[df[dump_col] > 0][dump_col].sum()


# plt.plot(df['H2Buffer1-0.time-based_0-soc'], label='soc')
# plt.plot(df['H2demand1-0.time-based_0-tot_dem'] + df['H2demand2-0.time-based_0-tot_dem'], label='total demand')
# plt.plot(generation, label='generation')
# plt.legend()
# plt.show()

# print(h2_deficit)
# print(h2_surplus)


plt.plot(-df[dump_col])
plt.ylim([-15, 15])
plt.show()

# fig, ax1 = plt.subplots(figsize=(10, 5))

# # First Y-axis (SoC)
# ax1.set_xlabel("Time step")
# ax1.set_ylabel("SoC (%)", color="tab:blue")
# ax1.set_ylim(5, 85)
# # ax1.set_xlim(0, 50)
# ax1.plot(df.index, df['H2Buffer1-0.time-based_0-soc'], label="SoC", color="tab:blue")
# ax1.tick_params(axis="y")

# # Second Y-axis (Demand & Generation)
# ax2 = ax1.twinx()
# ax2.set_ylabel("Power (kW)", color="tab:red")
# ax2.plot(df.index, df['H2demand1-0.time-based_0-tot_dem'] + df['H2demand2-0.time-based_0-tot_dem'], label="Total Demand", color="tab:orange")
# ax2.plot(df2.index, generation, label="Total Generation", color="tab:green")
# ax2.tick_params(axis="y")

# # Legends
# ax1.legend(loc="upper left")
# ax2.legend(loc="upper right")

# plt.title("SoC vs. Demand & Generation Over Time")
# plt.show()

