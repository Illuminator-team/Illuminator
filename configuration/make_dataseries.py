import random
from datetime import datetime, timedelta

# specify the file path and name
file_name = '../Scenarios/eboiler_data.txt'

# specify the initial date, step (in minutes), and final date
initial_date = datetime(2012, 1, 1, 0, 0, 0)
step = timedelta(minutes=15)
final_date = datetime(2012, 12, 31, 23, 45, 0)     # 2012-12-31 23:45:00

# specify the range for the last column value
min_val = 0
max_val = +400
max_var = 50

# attribute that has to be shared (name second column)
attr = 'eboiler_dem'

# Electrolyser data flow2e positive [kW]
# Fuelcell data h2_consume positive
# H2storage data flow2h2s

# generate the list of dates and corresponding load values using random walk
dates = []
loads = []
current_date = initial_date
current_load = random.uniform(min_val, max_val)
while current_date <= final_date:
    dates.append(current_date.strftime('%Y-%m-%d %H:%M:%S'))
    loads.append(current_load)
    current_load += random.uniform(-max_var, max_var)
    current_load = max(min_val, min(max_val, current_load)) # limit load values within [min_val, max_val]
    current_date += step

# write the header to the file
with open(file_name, 'w') as file:
    file.write(file_name.split('/')[-1].split('.')[0].capitalize() + '\n')
    file.write("time," + attr + '\n')

    # write each date and load value to the file
    for i in range(len(dates)):
        line = "{},{}\n".format(dates[i], loads[i])
        file.write(line)