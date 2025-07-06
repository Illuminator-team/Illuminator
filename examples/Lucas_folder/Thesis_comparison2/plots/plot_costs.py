import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

plot_saving_dir = 'C:/Users/31633/Dropbox/My PC (DESKTOP-84P3QQD)/Documents/Master_thesis/Thesis_figures/Results/Scenario2'
figs = []
label_font_size = 18
tick_font_size = 14
linewidth = 2
marker_size = 30

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


df_sim_out = pd.read_csv('C:/Users/31633/Python_projects/Illuminator/examples/Lucas_folder/Thesis_comparison2/out_CSV.csv')
soc = df_sim_out['Battery1-0.time-based_0-soc']
load1 = df_sim_out['Load1-0.time-based_0-load_dem'] 
load2 = df_sim_out['Load1-0.time-based_0-load_dem'] 
load3 = df_sim_out['Load1-0.time-based_0-load_dem'] 
load4 = df_sim_out['Load1-0.time-based_0-load_dem'] 
load5 = df_sim_out['Load1-0.time-based_0-load_dem'] 
pv1 = df_sim_out['PV1-0.time-based_0-pv_gen']
pv2 = df_sim_out['PV2-0.time-based_0-pv_gen']
pv3 = df_sim_out['PV3-0.time-based_0-pv_gen']
pv4 = df_sim_out['PV4-0.time-based_0-pv_gen']
pv5 = df_sim_out['PV5-0.time-based_0-pv_gen']
load_dem_tot = load1 + load2+ load3 + load4 + load5
pv_tot = pv1 + pv2 + pv3 + pv4 + pv5
grid_use = df_sim_out['Controller1-0.time-based_0-dump']
price_df = pd.read_csv('examples/Lucas_folder/Thesis_comparison2/data/settlement_prices_2023_TenneT_DTS.csv', skiprows=1)
price_short = pd.to_numeric(price_df['Price_Shortage'])[:len(grid_use)]
price_surplus = pd.to_numeric(price_df['Price_Surplus'])[:len(grid_use)]
cost = pd.Series(np.where(grid_use > 0, (grid_use * -price_surplus)*0.25, (-grid_use*price_short)*0.25))
print(cost.sum())

fig1, axs = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

# 1. Grid usage and PV generation
axs[0].plot(load_dem_tot, label='Total Household Demand', color='blue')
axs[0].plot(pv_tot, label='PV Generation', color='orange')
axs[0].plot(grid_use, label='Grid Usage', color='red')
axs[0].set_ylabel('Power [kW]', fontsize=label_font_size)
axs[0].legend(loc='upper left')
axs[0].grid(True)
axs[0].tick_params(axis='y', labelsize=tick_font_size)
axs[0].set_title('Power Flows')

# 2. State of Charge
axs[1].plot(soc, label='Battery SoC', color='black')
axs[1].set_ylabel('SoC [%]', fontsize=label_font_size)
# axs[1].legend(loc='upper left')
axs[1].grid(True)
axs[1].tick_params(axis='y', labelsize=tick_font_size)
axs[1].set_title('Battery State of Charge')

# 3. Cost
axs[2].plot(cost, label='Cost', color='green')
axs[2].set_ylabel('Cost [€]', fontsize=label_font_size)
axs[2].set_xlabel('Timestep', fontsize=label_font_size)
# axs[2].legend(loc='upper left')
axs[2].grid(True)
axs[2].tick_params(axis='y', labelsize=tick_font_size)
axs[2].tick_params(axis='x', labelsize=tick_font_size)
axs[2].set_title('Energy Cost Over Time')
fig1.tight_layout()
figs.append((fig1, 'unoptimized_NH.png'))

df_sim_out_opt = pd.read_csv('C:/Users/31633/Python_projects/Illuminator/examples/Lucas_folder/Thesis_comparison2/out_CSV_opt.csv')
soc = df_sim_out_opt['Battery1-0.time-based_0-soc']
load1 = df_sim_out_opt['Load1-0.time-based_0-load_dem'] 
load2 = df_sim_out_opt['Load1-0.time-based_0-load_dem'] 
load3 = df_sim_out_opt['Load1-0.time-based_0-load_dem'] 
load4 = df_sim_out_opt['Load1-0.time-based_0-load_dem'] 
load5 = df_sim_out_opt['Load1-0.time-based_0-load_dem'] 
pv1 = df_sim_out_opt['PV1-0.time-based_0-pv_gen']
pv2 = df_sim_out_opt['PV2-0.time-based_0-pv_gen']
pv3 = df_sim_out_opt['PV3-0.time-based_0-pv_gen']
pv4 = df_sim_out_opt['PV4-0.time-based_0-pv_gen']
pv5 = df_sim_out_opt['PV5-0.time-based_0-pv_gen']
load_dem_tot = load1 + load2+ load3 + load4 + load5
pv_tot = pv1 + pv2 + pv3 + pv4 + pv5
grid_use = df_sim_out_opt['Controller1-0.time-based_0-dump']
price_df = pd.read_csv('examples/Lucas_folder/Thesis_comparison2/data/settlement_prices_2023_TenneT_DTS.csv', skiprows=1)
price_short = pd.to_numeric(price_df['Price_Shortage'])[:len(grid_use)]
price_surplus = pd.to_numeric(price_df['Price_Surplus'])[:len(grid_use)]
cost = pd.Series(np.where(grid_use > 0, (grid_use * -price_surplus)*0.25, (-grid_use*price_short)*0.25))
print(cost.sum())


fig2, axs = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

# 1. Grid usage and PV generation
axs[0].plot(load_dem_tot, label='Total Household Demand', color='blue')
axs[0].plot(pv_tot, label='PV Generation', color='orange')
axs[0].plot(grid_use, label='Grid Usage', color='red')
axs[0].set_ylabel('Power [kW]', fontsize=label_font_size)
axs[0].legend(loc='upper left')
axs[0].grid(True)
axs[0].tick_params(axis='y', labelsize=tick_font_size)
axs[0].set_title('Power Flows')

# 2. State of Charge
axs[1].plot(soc, label='Battery SoC', color='black')
axs[1].set_ylabel('SoC [%]', fontsize=label_font_size)
# axs[1].legend(loc='upper left')
axs[1].grid(True)
axs[1].tick_params(axis='y', labelsize=tick_font_size)
axs[1].set_title('Battery State of Charge')

# 3. Cost
axs[2].plot(cost, label='Cost', color='green')
axs[2].set_ylabel('Cost [€]', fontsize=label_font_size)
axs[2].set_xlabel('Timestep', fontsize=label_font_size)
# axs[2].legend(loc='upper left')
axs[2].grid(True)
axs[2].tick_params(axis='y', labelsize=tick_font_size)
axs[2].tick_params(axis='x', labelsize=tick_font_size)
axs[2].set_title('Energy Cost Over Time')
fig2.tight_layout()
figs.append((fig2, 'optimized_NH.png'))
plt.show()

save_all = input(f"Save all plots to {plot_saving_dir}? (y/n)").strip().lower() == 'y'
if save_all:
    os.makedirs(plot_saving_dir, exist_ok=True)

    for fig, ffilename in figs:
        path = os.path.join(plot_saving_dir, ffilename)
        fig.savefig(path, dpi=300)
        print(f"Saved {fig} as {ffilename}")
# plt.figure(figsize=(8, 5))
# plt.plot(price_short, label='Shortage Price', color='orange')
# plt.plot(price_surplus, label='Surplus Price', color='blue')
# plt.plot(grid_use, label='Grid Usage', color='red')
# plt.legend()
# plt.grid(True)
# plt.show()


# error_data = pd.read_csv("C:/Users/31633/Downloads/individual+household+electric+power+consumption/household_power_consumption - Copy.csv")
# list_of_wrong_dates = []
# for i in range(len(error_data['Global_active_power'])):
#     if error_data['Global_active_power'][i] == '?':
#         # print(error_data['Date'][i])
#         list_of_wrong_dates.append(error_data['Date'][i])
# list_of_unique_dates = list(set(list_of_wrong_dates))
# print(len(list_of_unique_dates))
# print(list_of_unique_dates)



