import pandas as pd
import matplotlib.pyplot as plt

df_loads = pd.read_csv('C:/Users/31633/Python_projects/Illuminator/examples/Lucas_folder/Thesis_comparison2/data/household_power_consumption_15min_complete.csv', header=1)
# Convert 'date' column to datetime (ensure correct day/month ordering)

# Convert date column to datetime
df_loads['date'] = pd.to_datetime(df_loads['date'], dayfirst=True)

# Convert power values to numeric
df_loads['load1'] = pd.to_numeric(df_loads['load1'], errors='coerce')
df_loads['load2'] = pd.to_numeric(df_loads['load2'], errors='coerce')
df_loads['load3'] = pd.to_numeric(df_loads['load3'], errors='coerce')
df_loads['load4'] = pd.to_numeric(df_loads['load4'], errors='coerce')
df_loads['load5'] = pd.to_numeric(df_loads['load5'], errors='coerce')


# Plot the first 24 points
# plt.figure(figsize=(10, 5))
# plt.plot(df_loads['date'][24*4*7:24*4*14], df_loads['load1'][24*4*7:24*4*14], label='load1')
# plt.plot(df_loads['date'][24*4*7:24*4*14], df_loads['load2'][24*4*7:24*4*14], label='load2')
# plt.plot(df_loads['date'][24*4*7:24*4*14], df_loads['load3'][24*4*7:24*4*14], label='load3')
# plt.plot(df_loads['date'][24*4*7:24*4*14], df_loads['load4'][24*4*7:24*4*14], label='load4')
# plt.plot(df_loads['date'][24*4*7:24*4*14], df_loads['load5'][24*4*7:24*4*14], label='load5')
# plt.xlabel('Time')
# plt.ylabel('Power (kW)')
# plt.legend()
# plt.xticks(rotation=45)
# plt.grid(True)
# plt.tight_layout()
# plt.show()


df_sim_out = pd.read_csv('C:/Users/31633/Python_projects/Illuminator/examples/Lucas_folder/Thesis_comparison2/out_CSV.csv')

soc = df_sim_out['Battery1-0.time-based_0-soc']

load1 = df_sim_out['Load1-0.time-based_0-load_dem'] 
load2 = df_sim_out['Load1-0.time-based_0-load_dem'] 
load3 = df_sim_out['Load1-0.time-based_0-load_dem'] 
load4 = df_sim_out['Load1-0.time-based_0-load_dem'] 
load5 = df_sim_out['Load1-0.time-based_0-load_dem'] 
ev1 = df_sim_out['EV1-0.time-based_0-demand']
ev2 = df_sim_out['EV2-0.time-based_0-demand']
ev3 = df_sim_out['EV3-0.time-based_0-demand']
ev4 = df_sim_out['EV4-0.time-based_0-demand']
ev5 = df_sim_out['EV5-0.time-based_0-demand']
ev1_p = df_sim_out['CSV_EV_presence-0.time-based_0-ev1']
ev2_p = df_sim_out['CSV_EV_presence-0.time-based_0-ev2']
ev3_p = df_sim_out['CSV_EV_presence-0.time-based_0-ev3']
ev4_p = df_sim_out['CSV_EV_presence-0.time-based_0-ev4']
ev5_p = df_sim_out['CSV_EV_presence-0.time-based_0-ev5']
pv1 = df_sim_out['PV1-0.time-based_0-pv_gen']
pv2 = df_sim_out['PV2-0.time-based_0-pv_gen']
pv3 = df_sim_out['PV3-0.time-based_0-pv_gen']
pv4 = df_sim_out['PV4-0.time-based_0-pv_gen']
pv5 = df_sim_out['PV5-0.time-based_0-pv_gen']

load_dem_tot = load1 + load2+ load3 + load4 + load5
ev_dem_tot = ev1 + ev2 + ev3 + ev4 + ev5
ev_pres_tot = ev1_p + ev2_p + ev3_p + ev4_p + ev5_p
pv_tot = pv1 + pv2 + pv3 + pv4 + pv5

# plt.figure(figsize=(10, 5))
# plt.plot(ev_dem_tot)
# plt.plot(ev_pres_tot)
grid_use = -df_sim_out['Controller1-0.time-based_0-dump'].clip(upper=0)

fig, ax1 = plt.subplots(figsize=(10, 5))
# First y-axis: power data
ax1.plot(load_dem_tot, label='Total Household Demand', color='b')
ax1.plot(ev_dem_tot, label='EV Demand', color='g')
ax1.plot(pv_tot, label='PV generation', color='y')
ax1.plot(grid_use, label='Grid usage', color='r')
ax1.set_xlabel('Time')
ax1.set_ylabel('Power [kW]', color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax1.legend(loc='upper left')

# Second y-axis: SoC
ax2 = ax1.twinx()
ax2.plot(soc, label='SoC', color='k')
ax2.set_ylabel('SoC [%]', color='tab:green')
ax2.tick_params(axis='y', labelcolor='tab:green')

# Optional enhancements
fig.autofmt_xdate()  # rotates x-axis labels if they're datetime
ax1.grid(True)
fig.tight_layout()

plt.show()


# error_data = pd.read_csv("C:/Users/31633/Downloads/individual+household+electric+power+consumption/household_power_consumption - Copy.csv")
# list_of_wrong_dates = []
# for i in range(len(error_data['Global_active_power'])):
#     if error_data['Global_active_power'][i] == '?':
#         # print(error_data['Date'][i])
#         list_of_wrong_dates.append(error_data['Date'][i])
# list_of_unique_dates = list(set(list_of_wrong_dates))
# print(len(list_of_unique_dates))
# print(list_of_unique_dates)



