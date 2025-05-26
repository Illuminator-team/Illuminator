import numpy as np
import pandas as pd
import csv
import math
from scipy import integrate

presence_matrix = pd.read_csv('./examples/Lucas_folder/data_generation/ev_presence.csv', sep=',', skiprows=1)
soc_at_arrival = [0, 0, 0, 0, 0]
desired_soc = [100, 100, 100, 100, 100]
capacity = 60       # kWh
max_power = 11      # kW
end_initial_phase = 2
end_mid_phase = 80
min_power = 2


def detect_final_timestep_index(column):
    for i in range(len(column)-1, -1, -1):
        if column [i] == 1:
            if column[i-1] == 1:
                return i
            else:
                raise Exception("There is an error in the data")

def detect_first_timestep_index(column):
    for i in range(len(column)):
        if column[i] == 1:
            if column[i+1] == 1:
                return i
            else:
                raise Exception("There is an error in the data")


# def latest_timestep_index(last_timstep, soc, desired_soc):

#     detect_final_timestep_index()




# upper_lim = []



# print(upper_lim)

            
def P1(current_soc, target_soc):
    target_soc = min(target_soc, end_initial_phase)
    def P(soc): return max(max_power/(end_initial_phase - 0) * soc, min_power)
    time = integrate.quad(lambda s: (capacity/100)/P(s), current_soc, target_soc)[0]
    print('calculate2 time_to_local_target_soc [h]:', time)
    timesteps = math.ceil(time * 4) # time in timesteps (15min res)
    new_soc = target_soc
    print('calculate1 soc:', new_soc)
    return timesteps, new_soc

def P2(current_soc, target_soc):
    target_soc = min(target_soc, end_mid_phase)
    print(target_soc)
    b = max_power - ((0.9-1)*max_power*end_initial_phase)/(end_mid_phase-end_initial_phase)
    def P(soc): return max_power*(0.9 -1)/(end_mid_phase-end_initial_phase) * soc + b
    print("power at 2%:", P(2)) 
    print("power at 80%:", P(80))  
    time = integrate.quad(lambda s: (capacity/100)/P(s), current_soc, target_soc)[0]
    print('calculate2 time_to_local_target_soc [h]:', time)
    timesteps = math.ceil(time * 4) # time in timesteps (15min res)
    print("calculate2 timesteps:", timesteps)
    new_soc = target_soc
    print('calculate2 soc:', new_soc)
    return timesteps, new_soc

def P3(current_soc, target_soc):
    target_soc = min(target_soc, 100)
    b = 0.9*max_power - ((0-0.9*max_power)*end_mid_phase)/(100-end_mid_phase)
    print("P3 b:", b)
    def P(soc): return max((0 - max_power*0.9)/(100-end_mid_phase) * soc + b, min_power)
    print("power at 80%:", P(80)) 
    print("power at 90%:", P(90))  
    time = integrate.quad(lambda s: (capacity/100)/P(s), current_soc, target_soc)[0]
    print('calculate3 time_to_local_target_soc [h]:', time)
    timesteps = math.ceil(time * 4) # time in timesteps (15min res)
    print("calculate3 timesteps:", timesteps)
    new_soc = target_soc
    print('calculate3 soc:', new_soc)
    return timesteps, new_soc
    

def calculate_time_to_soc_fast(current_soc, target_soc):
    time = 0
    if current_soc == target_soc:
        return 0
    if 0 <= current_soc < end_initial_phase:
        timesteps, new_soc = P1(current_soc, target_soc)
    elif end_initial_phase <= current_soc < end_mid_phase:
        timesteps, new_soc = P2(current_soc, target_soc) 
    else:
        timesteps, new_soc = P3(current_soc, target_soc)
    return timesteps + calculate_time_to_soc_fast(new_soc, target_soc)



def calculate_time_to_soc(current_soc, target_soc):
    time = 0
    E = (target_soc - current_soc)/100 * capacity
    timesteps = math.ceil(E/max_power * 4)
    return timesteps


upper_lim = []
lower_lim = []

## THIS IS FORSTANDARD HOSEHOLD CHARGER

print(presence_matrix)
for i, column in enumerate(presence_matrix.iloc[:, 1:]):
    last_timestep = detect_final_timestep_index(presence_matrix[column])
    first_timestep = detect_first_timestep_index(presence_matrix[column])
    latest_timestep = last_timestep- calculate_time_to_soc(soc_at_arrival[i], desired_soc[i])
    upper_lim.append(latest_timestep)
    lower_lim.append(first_timestep)



## THIS IS FOR FAST CHARGER
# upper_lim = []
# lower_lim = []
# for i, column in enumerate(presence_matrix.iloc[:, 1:]):
#     latest_timestep = last_timestep - calculate_time_to_soc_fast(soc_at_arrival[i], desired_soc[i])
#     if latest_timestep < first_timestep:
#         raise Exception("Can't charge to target in time")
#     upper_lim.append(latest_timestep)
#     lower_lim.append(first_timestep)




print("upper_lim:", upper_lim)
print("lower_lim:", lower_lim)
print("Final:", calculate_time_to_soc(0,100))