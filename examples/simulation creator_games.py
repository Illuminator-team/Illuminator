import subprocess
import mosaik.util
import numpy as np
import pandas as pd
import csv
import os
from datetime import datetime, timedelta
import itertools
import Controllers.GPController.gpcontroller_mosaik as gp
import Games.emarket_mosaik as elem
import Games.p2ptrading_mosaik as p2p
import Games.rtprice_mosaik as rt
import Agents.prosumer_mosaik as p
import Models.Elenetwork.electricity_network_mosaik as en
from configuration.buildmodelset import *
from configuration.bids.initial_bids import *

# Error:
# AttributeError: Can only use .dt accessor with datetimelike values. Did you mean: 'at'?

# Error:
# With the combined yml file this now works. So issues are really with the versions of the modules

outputfile='Result/GameCase/results.csv'
outputfolder='Result/GameCase/'
sim_config_file="Cases/GameCase/"
sim_config_ddf=pd.read_xml(sim_config_file+'config.xml')
sim_config={row[1]:{row[2]:row[3]}for row in sim_config_ddf.values}


tosh = sim_config_ddf[sim_config_ddf['method'] == 'connect']
# ! /usr/bin/env python
if not tosh.empty:
    with open('run.sh', 'w') as rsh:
        rsh.write("#! /bin/bash")
        for row in tosh.values:
            rsh.write("\n" + "lxterminal -e ssh illuminator@" + row[3].replace(':5123',
                                                                               ' ') + "'./Desktop/Final_illuminator/configuration/runshfile/run" +
                      row[1] + ".sh'&")

    subprocess.run(['/bin/bash', '/home/illuminator/Desktop/Final_illuminator/configuration/run.sh'])

connection = pd.read_xml(sim_config_file+'connection.xml')

# if RESULTS_SHOW_TYPE['dashboard_show'] == True:
#     # 62f0da4aff384fd9b382b1d8057a128af9d102fe
#     import wandb
#
#     wandb.init(project="illuminator-project")
#     wandb.define_metric("custom_step")

START_DATE = '2012-04-15 00:00:00'
end = 1 * 24 * 3600  # last one interval is not computed
start_date_obj = datetime.strptime(START_DATE, '%Y-%m-%d %H:%M:%S')
delta = timedelta(seconds=end)
end_date_obj = start_date_obj + delta
END_DATE = end_date_obj.strftime('%Y-%m-%d %H:%M:%S')


WIND_DATA = 'Scenarios/winddata_NL.txt'
Pv_DATA = 'Scenarios/pv_data_Rotterdam_NL-15min.txt'
load_DATA = 'Scenarios/load_data.txt'
rtprice_DATA = 'Scenarios/rtprice_data.txt'

# Clean results files
directory = "Result/GameCase"
# Iterate over all files in the directory
for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)

    # Check if the path is a file
    if os.path.isfile(file_path):
        # Open the file in write mode and truncate it to remove contents
        with open(file_path, "w") as file:
            pass  # No need to write anything, just truncate the file

# set up the "world" of the scenario
models = pd.concat([connection["send"], connection["receive"]])
models = models.drop_duplicates(keep='first', inplace=False)
models.reset_index(drop=True, inplace=True)

# Find model to be forecasted
f_models = connection[connection['receive'].str.startswith('forecaster')]['send']


def inremental_attributes():
    global incr_attr_added, row
    connection_list = pd.DataFrame(connection).replace(np.nan, 'NA').values.tolist()
    # find inc. attr. in files
    incr_attr = [gp.incremental_attributes, elem.incremental_attributes,
                 p2p.incremental_attributes, rt.incremental_attributes,
                 p.incremental_attributes, en.incremental_attributes]
    incr_attr_added = [[], [], [], [], [], []]
    for row in range(len(incr_attr)):
        for attr in incr_attr[row]:
            # Get all unique values of the attribute from the connection DataFrame
            columns = ['index', 'send', 'receive', 'messages', 'messager'] + (
                ['more'] if len(connection_list[0]) == 6 else [])
            x = pd.DataFrame(connection_list, columns=columns)
            attr_outputs = x.loc[x['messager'].str.startswith(attr + '['), 'messager'].unique()
            incr_attr_added[row].extend(attr_outputs)
            attr_inputs = x.loc[x['messages'].str.startswith(attr + '['), 'messages'].unique()
            incr_attr_added[row].extend(attr_inputs)
            incr_attr_added[row] = list(set(incr_attr_added[row]))

            # Loop over all attribute values and append them to the corresponding model attributes in the META dictionary
            if row == 0:
                for attr_value in incr_attr_added[row]:
                    gp.META['models']['GPCtrl']['attrs'].append(attr_value)
            elif row == 1:
                for attr_value in incr_attr_added[row]:
                    elem.META['models']['Emarket']['attrs'].append(attr_value)
            elif row == 2:
                for attr_value in incr_attr_added[row]:
                    p2p.META['models']['P2Ptrading']['attrs'].append(attr_value)
            elif row == 3:
                for attr_value in incr_attr_added[row]:
                    rt.META['models']['RTprice']['attrs'].append(attr_value)
            elif row == 4:
                for attr_value in incr_attr_added[row]:
                    p.META['models']['Prosumer']['attrs'].append(attr_value)
            else:
                for attr_value in incr_attr_added[row]:
                    en.META['models']['ElectricityNetwork']['attrs'].append(attr_value)
                    en.META['models']['ElectricityNetwork']['attrs'] = \
                        list(dict.fromkeys(en.META['models']['ElectricityNetwork']['attrs']))
    incr_attr_added = list(itertools.chain(*incr_attr_added))


inremental_attributes()

############################## start Forecasing

world = mosaik.World(sim_config, debug=True)

forecastable_models = pd.DataFrame()
forecastable_models['model'] = pd.Series(['Wind', 'PV', 'Load', 'Battery', 'GPCtrl'])
number = []
for model in forecastable_models['model']:
    number.append(
        int((models.str.startswith(model.lower()) == True).sum())
    )
forecastable_models['number'] = number
collector = world.start('Collector', start_date=START_DATE,
                        results_show=RESULTS_SHOW_TYPE,output_file=outputfolder+'forecast.csv')
monitor = collector.Monitor()

for model_i in forecastable_models.iterrows():
    if model_i[1]['model'] == 'PV':
        solardata = world.start('CSVB', sim_start=START_DATE, datafile=Pv_DATA)
        pvsim = world.start('PV')
        pv = pvsim.PVset.create(model_i[1]['number'], sim_start=START_DATE, panel_data=pv_panel_set,
                                m_tilt=pv_set['m_tilt'], m_az=pv_set['m_az'], cap=pv_set['cap'],
                                output_type=pv_set['output_type'])
        solarprofile_data = solardata.Solar_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(solarprofile_data[i], pv[i], 'G_Gh', 'G_Dh', 'G_Bn', 'Ta', 'hs', 'FF', 'Az')

    elif model_i[1]['model'] == 'Wind':
        WSdata = world.start('CSVB', sim_start=START_DATE, datafile=WIND_DATA)
        windsim = world.start('Wind')
        wind = windsim.windmodel.create(model_i[1]['number'], sim_start=START_DATE,
                                        p_rated=Wind_set['p_rated'], u_rated=Wind_set['u_rated'],
                                        u_cutin=Wind_set['u_cutin'], u_cutout=Wind_set['u_cutout'],
                                        cp=Wind_set['cp'], diameter=Wind_set['diameter'],
                                        output_type=Wind_set['output_type'])
        windspeed_data = WSdata.WS_datafile.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(windspeed_data[i], wind[i], 'u')

    elif model_i[1]['model'] == 'Load':
        loaddata = world.start('CSVB', sim_start=START_DATE, datafile=load_DATA)
        loadsim = world.start('Load')
        load = loadsim.loadmodel.create(model_i[1]['number'], sim_start=START_DATE,
                                        houses=load_set['houses'], output_type=load_set['output_type'])
        load_data = loaddata.Load_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(load_data[i], load[i], 'load')

    elif model_i[1]['model'] == 'Battery':
        batterysim = world.start('Battery')
        battery = batterysim.Batteryset.create(model_i[1]['number'], sim_start=START_DATE,
                                               initial_set=Battery_initialset, battery_set=Battery_set)

    elif model_i[1]['model'] == 'GPCtrl':
        gpctrldata = world.start('CSVB', sim_start=START_DATE, datafile=rtprice_DATA)
        gpctrlsim = world.start('GPController')
        gpctrl = gpctrlsim.GPCtrl.create(model_i[1]['number'], sim_start=START_DATE, soc_min=Battery_set['soc_min'],
                                         soc_max=Battery_set['soc_max'],
                                         h2_soc_min=h2_set['h2storage_soc_min'], h2_soc_max=h2_set['h2storage_soc_max'],
                                         fc_eff=fuelcell_set['eff'])
        gpctrl_data = gpctrldata.RTprice_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(gpctrl_data[i], gpctrl[i], 'curtail')


f_connection = connection[~((connection['send'].str.contains('prosumer')) |
              ((connection['send'].str.contains('monitor')) & ~(connection['send'].str.contains('gpctrl')))) &
             ~((connection['receive'].str.contains('prosumer')) |
              ((connection['receive'].str.contains('monitor')) & ~(connection['send'].str.contains('gpctrl'))))]

for i, row in f_connection.iterrows():
    try:
        row['more']
    except KeyError:
        world.connect(eval(row['send']), eval(row['receive']), (row['messages'],row['messager']))
    else:
        if row['more']== None:
            world.connect(eval(row['send']), eval(row['receive']), (row['messages'], row['messager']))
            print(f'Connect {row["send"]} to {row["receive"]} output {row["messages"]} input {row["messager"]}')
        else:

            world.connect(eval(row['send']), eval(row['receive']), (row['messages'],row['messager']), time_shifted=True,
                          initial_data={row['messages']: 0})  # time_shifted=True, initial_data={row['message']: 0}
            print(f'Connect {row["send"]} to {row["receive"]} output {row["messages"]} input {row["messager"]} with time_shift')

if realtimefactor == 0:
    world.run(until=end)
else:
    world.run(until=end, rt_factor=realtimefactor)

###### extract forecaster data

# Step 1: Read the data from the CSV file
df = pd.read_csv(outputfolder+'forecast.csv', parse_dates=['date'])

# Step 2: Find controller-prosumer connections
def find_controller_prosumer_connections(connection):
    connections = set()
    for row in connection:
        if row[1].startswith('gpctrl') and row[2].startswith('prosumer'):
            controller = row[1].replace('[', '_').replace(']', '')
            prosumer = row[2].replace('[', '_').replace(']', '')
            connections.add((controller, prosumer))
    return list(connections)


# Get the controller-prosumer connections
controller_prosumer_connections = find_controller_prosumer_connections(connection.values)

# Step 3: Analyze each column and assign data to respective prosumers
forecasted_curves = {}
forecasted_curves['dates'] = df["date"].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()
for column in df.columns[1:]:
    for controller, prosumer in controller_prosumer_connections:
        if controller in column:
            agent = prosumer
            component = column.split('-')[-1]
            if agent not in forecasted_curves:
                forecasted_curves[agent] = {}
            forecasted_curves[agent][component] = df[column].tolist()

############################## start simulation

world = mosaik.World(sim_config, debug=True)

Defined_models = pd.DataFrame()
Defined_models['model'] = pd.Series(['Wind', 'PV', 'Load', 'Electrolyser', 'H2storage',
                                     'Battery', 'Fuelcell', 'GPCtrl', 'Forecaster',
                                     'Prosumer', 'Emarket', 'P2Ptrading', 'RTprice', 'Enetwork'])

number = []
for model in Defined_models['model']:
    number.append(
        int((models.str.startswith(model.lower()) == True).sum())
    )
Defined_models['number'] = number
prosumers_number = {}

for model in models:
    if 'prosumer' in model:
        s_value = model.split('_')[1].split('[')[0]
        if s_value in prosumers_number:
            prosumers_number[s_value] += 1
        else:
            prosumers_number[s_value] = 1


collector = world.start('Collector', start_date=START_DATE,
                        results_show=RESULTS_SHOW_TYPE,output_file=outputfolder+'results.csv')
monitor = collector.Monitor()
for model_i in Defined_models.iterrows():
    if model_i[1]['model'] == 'PV':
        solardata = world.start('CSVB', sim_start=START_DATE, datafile=Pv_DATA)
        pvsim = world.start('PV')
        pv = pvsim.PVset.create(model_i[1]['number'], sim_start=START_DATE, panel_data=pv_panel_set,
                                m_tilt=pv_set['m_tilt'], m_az=pv_set['m_az'], cap=pv_set['cap'],
                                output_type=pv_set['output_type'])
        solarprofile_data = solardata.Solar_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(solarprofile_data[i], pv[i], 'G_Gh', 'G_Dh', 'G_Bn', 'Ta', 'hs', 'FF', 'Az')

    elif model_i[1]['model'] == 'Wind':
        WSdata = world.start('CSVB', sim_start=START_DATE, datafile=WIND_DATA)
        windsim = world.start('Wind')
        wind = windsim.windmodel.create(model_i[1]['number'], sim_start=START_DATE,
                                        p_rated=Wind_set['p_rated'], u_rated=Wind_set['u_rated'],
                                        u_cutin=Wind_set['u_cutin'], u_cutout=Wind_set['u_cutout'],
                                        cp=Wind_set['cp'], diameter=Wind_set['diameter'],
                                        output_type=Wind_set['output_type'])
        windspeed_data = WSdata.WS_datafile.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(windspeed_data[i], wind[i], 'u')

    elif model_i[1]['model'] == 'Load':
        loaddata = world.start('CSVB', sim_start=START_DATE, datafile=load_DATA)
        loadsim = world.start('Load')
        load = loadsim.loadmodel.create(model_i[1]['number'], sim_start=START_DATE,
                                        houses=load_set['houses'], output_type=load_set['output_type'])
        load_data = loaddata.Load_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(load_data[i], load[i], 'load')

    elif model_i[1]['model'] == 'Battery':
        batterysim = world.start('Battery')
        battery = batterysim.Batteryset.create(model_i[1]['number'], sim_start=START_DATE,
                                               initial_set=Battery_initialset, battery_set=Battery_set)

    elif model_i[1]['model'] == 'GPCtrl':
        gpctrldata = world.start('CSVB', sim_start=START_DATE, datafile=rtprice_DATA)
        gpctrlsim = world.start('GPController')
        gpctrl = gpctrlsim.GPCtrl.create(model_i[1]['number'], sim_start=START_DATE, soc_min=Battery_set['soc_min'],
                                         soc_max=Battery_set['soc_max'],
                                         h2_soc_min=h2_set['h2storage_soc_min'], h2_soc_max=h2_set['h2storage_soc_max'],
                                         fc_eff=fuelcell_set['eff'])
        gpctrl_data = gpctrldata.RTprice_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(gpctrl_data[i], gpctrl[i], 'curtail')

    elif model_i[1]['model'] == 'Emarket':
        emarketsim = world.start('Emarket')
        emarket = emarketsim.Emarket.create(model_i[1]['number'], sim_start=START_DATE, sim_end=END_DATE,
                                                     initial_supply_bids=initial_supply_bids,
                                                     initial_demand_bids=initial_demand_bids)
    elif model_i[1]['model'] == 'P2Ptrading':
        p2ptradingsim = world.start('P2Ptrading')
        p2ptrading = p2ptradingsim.P2Ptrading.create(model_i[1]['number'], sim_start=START_DATE)

    elif model_i[1]['model'] == 'RTprice':
        rtpricedata = world.start('CSVB', sim_start=START_DATE, datafile=rtprice_DATA)
        rtpricesim = world.start('RTprice')
        rtprice = rtpricesim.RTprice.create(model_i[1]['number'], sim_start=START_DATE)
        rtprice_data = rtpricedata.RTprice_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(rtprice_data[i], rtprice[i], 'buy_price')
            world.connect(rtprice_data[i], rtprice[i], 'sell_price')

    elif model_i[1]['model'] == 'Prosumer':
        prosumersim = world.start('Prosumer')
        for s_value, count in prosumers_number.items():
            if s_value == 's1':
                prosumer_s1 = prosumersim.Prosumer.create(count, strategy=s_value,
                                               sim_start=START_DATE, forecasted_data=forecasted_curves, metrics=metrics)
            if s_value == 's2':
                prosumer_s2 = prosumersim.Prosumer.create(count, strategy=s_value,
                                               sim_start=START_DATE, forecasted_data=forecasted_curves, metrics=metrics)

    elif model_i[1]['model'] == 'Enetwork':
        enetsim = world.start('ElectricityNetwork')
        enetwork = enetsim.ElectricityNetwork.create(model_i[1]['number'], sim_start=START_DATE,
                                                     max_congestion=enetwork_set['max_congestion'],
                                                     p_loss_m=enetwork_set['p_loss_m'],
                                                     length=enetwork_set['length'])

for i, row in connection.iterrows():
    try:
        row['more']
    except KeyError:
        world.connect(eval(row['send']), eval(row['receive']), (row['messages'],row['messager']))
    else:
        if row['more']== None:
            world.connect(eval(row['send']), eval(row['receive']), (row['messages'], row['messager']))
            print(f'Connect {row["send"]} to {row["receive"]} output {row["messages"]} input {row["messager"]}')
        else:

            world.connect(eval(row['send']), eval(row['receive']), (row['messages'],row['messager']), time_shifted=True,
                          initial_data={row['messages']: 0})  # time_shifted=True, initial_data={row['message']: 0}
            print(f'Connect {row["send"]} to {row["receive"]} output {row["messages"]} input {row["messager"]} with time_shift')

if realtimefactor == 0:
    world.run(until=end)
else:
    world.run(until=end, rt_factor=realtimefactor)
