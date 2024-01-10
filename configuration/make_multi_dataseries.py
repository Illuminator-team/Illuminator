import random
from datetime import datetime, timedelta

# specify the file path and name
file_name = '../Scenarios/hp_data.txt'

# specify the initial date, step (in minutes), and final date
initial_date = datetime(2012, 1, 1, 0, 0, 0)
step = timedelta(minutes=15)
final_date = datetime(2012, 12, 31, 23, 45, 0)     # 2012-12-31 23:45:00

# attributes that have to be shared (name second column)
attrs = ['Q_Demand', 'heat_source_T', 'cond_in_T','cons_T','T_amb']

# specify the range for each attribute
min_vals = {'Q_Demand': 5000, 'heat_source_T': 4, 'cond_in_T': 30,'cons_T':36,'T_amb':10}
max_vals = {'Q_Demand': 8000, 'heat_source_T': 20, 'cond_in_T': 55,'cons_T':80,'T_amb':20}
max_vars = {'Q_Demand': 100, 'heat_source_T': 1, 'cond_in_T': 1,'cons_T':1,'T_amb':1}

# Electrolyser data flow2e positive [kW]
# Fuelcell data h2_consume positive
# H2storage data flow2h2s

# generate the list of dates and corresponding load values using random walk
dates = []
loads = {attr: [] for attr in attrs}
current_date = initial_date
current_load = {attr: random.uniform(min_vals[attr], max_vals[attr]) for attr in attrs}
while current_date <= final_date:
    dates.append(current_date.strftime('%Y-%m-%d %H:%M:%S'))
    for attr in attrs:
        loads[attr].append(current_load[attr])
        current_load[attr] += random.uniform(-max_vars[attr], max_vars[attr])
        current_load[attr] = max(min_vals[attr], min(max_vals[attr], current_load[attr])) # limit load values within [min_val, max_val]
    current_date += step

# write the header to the file
with open(file_name, 'w') as file:
    file.write(file_name.split('/')[-1].split('.')[0].capitalize() + '\n')
    file.write("time," + ','.join(attrs) + '\n')

    # write each date and load value to the file
    for i in range(len(dates)):
        line = "{},{}\n".format(dates[i], ','.join(str(loads[attr][i]) for attr in attrs))
        file.write(line)
