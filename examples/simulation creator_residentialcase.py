import subprocess
import pandas as pd
import mosaik
import mosaik.util
import numpy as np
import pandas as pd
from mosaik.util import connect_many_to_one
import time
from configuration.buildmodelset import *

outputfile = 'Result/ResidentialCase/results.csv'
sim_config_file = "Cases/ResidentialCase/"
sim_config_ddf = pd.read_xml(sim_config_file + 'config.xml')
sim_config = {row[1]: {row[2]: row[3]} for row in sim_config_ddf.values}

tosh = sim_config_ddf[sim_config_ddf['method'] == 'connect']
# ! /usr/bin/env python
# ERROR:
# No errors found. Runs fine

if not tosh.empty:
    with open('run.sh', 'w') as rsh:
        rsh.write("#! /bin/bash")
        for row in tosh.values:
            rsh.write("\n" + "lxterminal -e ssh illuminator@" + row[3].replace(':5123', ' ') +
                      "'./Desktop/Illuminator/configuration/runshfile/run" + row[1] + ".sh'&")

    subprocess.run(['/bin/bash', '/home/illuminator/Desktop/Illuminator/configuration/run.sh'])

connection = pd.read_xml(sim_config_file + 'connection.xml')

# if RESULTS_SHOW_TYPE['dashboard_show']==True:
#     #62f0da4aff384fd9b382b1d8057a128af9d102fe
#     import wandb
#     wandb.init(project="illuminator-project")
#     wandb.define_metric("custom_step")


START_DATE = '2012-06-01 00:00:00'
# START_DATE = '2012-06-30 23:45:00'
end = 1 * 24 * 3600  # last one interval is not computed

WIND_DATA = 'Scenarios/winddata_NL.txt'
Pv_DATA = 'Scenarios/pv_data_Rotterdam_NL-15min.txt'  # solar data file ########################
load_DATA = 'Scenarios/load_data.txt'  #######################
# set up the "world" of the scenario
world = mosaik.World(sim_config, debug=True)

models = pd.concat([connection["send"], connection["receive"]])
models = models.drop_duplicates(keep='first', inplace=False)
models.reset_index(drop=True, inplace=True)

##############################start simulator
Defined_models = pd.DataFrame()
Defined_models['model'] = pd.Series(['Wind', 'PV', 'Load',
                                     'Electrolyser', 'H2storage', 'Battery', 'Fuelcell'])
number = []
for model in Defined_models['model']:
    number.append(
        int((models.str.startswith(model.lower()) == True).sum())
    )
Defined_models['number'] = number

ctrlsim = world.start('Controller')
ctrl = ctrlsim.Ctrl(sim_start=START_DATE, soc_min=Battery_set['soc_min'], soc_max=Battery_set['soc_max'],
                    h2_soc_min=h2_set['h2storage_soc_min'], h2_soc_max=h2_set['h2storage_soc_max'],
                    fc_eff=fuelcell_set['eff'])
#### the controller gives us just a basic value of power flow which needs to be there. so -ve or +ve
collector = world.start('Collector', start_date=START_DATE, results_show=RESULTS_SHOW_TYPE, output_file=outputfile)
monitor = collector.Monitor()

for model_i in Defined_models.iterrows():
    if model_i[1]['model'] == 'PV':
        solardata = world.start('CSVB', sim_start=START_DATE, datafile=Pv_DATA)  # loading the data file to mosaik
        pvsim = world.start('PV')  # the name given to mosaik file while importing in scenario sim_config
        # p_data = {'Module_area': 1.26, 'NOCT': 44, 'Module_Efficiency': 0.198, 'Irradiance_at_NOCT': 800,
        #           'Power_output_at_STC': 250}
        ## instantiating the pv model by giving the parameter values.
        pv = pvsim.PVset.create(model_i[1]['number'], sim_start=START_DATE, panel_data=pv_panel_set,
                                m_tilt=pv_set['m_tilt'], m_az=pv_set['m_az'], cap=pv_set['cap'],
                                output_type=pv_set['output_type'])  # cap in W
        solarprofile_data = solardata.Solar_data.create(model_i[1]['number'])  # instantiating an entity of the solar data file
        for i in range(model_i[1]['number']):
            world.connect(solarprofile_data[i], pv[i], 'G_Gh', 'G_Dh', 'G_Bn', 'Ta', 'hs', 'FF', 'Az')
    elif model_i[1]['model'] == 'Wind':
        WSdata = world.start('CSVB', sim_start=START_DATE, datafile=WIND_DATA)  # loading the data file to mosaik
        windsim = world.start('Wind')  # the name you gave to the in sim_config above
        wind = windsim.windmodel.create(model_i[1]['number'], sim_start=START_DATE,
                                        p_rated=Wind_set['p_rated'], u_rated=Wind_set['u_rated'],
                                        u_cutin=Wind_set['u_cutin'], u_cutout=Wind_set['u_cutout'],
                                        cp=Wind_set['cp'], diameter=Wind_set['diameter'],
                                        output_type=Wind_set['output_type'])  # p_rated in kW  #Resolution here is in minutes
        ## print(wind.full_id)
        windspeed_data = WSdata.WS_datafile.create(model_i[1]['number'])  # instantiating an entity of the wind data file
        for i in range(model_i[1]['number']):
            world.connect(windspeed_data[i], wind[i], 'u')

    elif model_i[1]['model'] == 'Load':
        loaddata = world.start('CSVB', sim_start=START_DATE, datafile=load_DATA)  # loading the data file to mosaik
        loadsim = world.start('Load')  # the name you gave to the in sim_config above
        load = loadsim.loadmodel.create(model_i[1]['number'], sim_start=START_DATE,
                                        houses=load_set['houses'], output_type=load_set['output_type'])  # loadmodel is the name we gave in the mosaik API file while writing META
        load_data = loaddata.Load_data.create(model_i[1]['number'])  # Load_data is the header in the txt file containing the load values.
        for i in range(model_i[1]['number']):
            world.connect(load_data[i], load[i], 'load')
    elif model_i[1]['model'] == 'Battery':
        #### no battery input data file as the input 'p_ask' comes from the controller. We connect the controller and the battery ahead.

        batterysim = world.start('Battery')  # the name you gave to the in sim_config above
        # Battery_initialset = {'initial_soc': 20}
        # Battery_set = {'max_p': 500, 'min_p': -500, 'max_energy': 500,
        #                'charge_efficiency': 0.9, 'discharge_efficiency': 0.9,
        #                'soc_min': 10, 'soc_max': 90, 'flag': -1, 'resolution': 15}  # p in kW
        battery = batterysim.Batteryset(sim_start=START_DATE, initial_set=Battery_initialset,
                                        battery_set=Battery_set)
        ## print(battery.full_id)
    elif model_i[1]['model'] == 'Electrolyser':
        electrosim = world.start('Electrolyser')
        h2storagesim = world.start('H2storage')
        fcsim = world.start('Fuelcell')
        electrolyser = electrosim.electrolysermodel(sim_start=START_DATE, eff=electrolyser_set['eff'],
                                                    resolution=electrolyser_set['resolution'],
                                                    term_eff=electrolyser_set['term_eff'],
                                                    rated_power=electrolyser_set['rated_power'],
                                                    ramp_rate=electrolyser_set['ramp_rate'])  # here resolution should be the same we have for the data sets for
        ## wind and pv and load. Make sure to keep the same resolution all across

        # h2storage_initial = {'initial_soc': 20}
        # h2_set = {'h2storage_soc_min': 10, 'h2storage_soc_max': 90, 'max_h2': 200, 'min_h2': -200, 'flag': -1}
        h2storage = h2storagesim.compressed_hydrogen(sim_start=START_DATE, initial_set=h2storage_initial,
                                                     h2_set=h2_set)
        ##
        fuelcell = fcsim.fuelcellmodel(sim_start=START_DATE, eff=fuelcell_set['eff'],
                                       resolution=fuelcell_set['resolution'],
                                       term_eff=fuelcell_set['term_eff'],
                                       max_flow=fuelcell_set['max_flow'],
                                       min_flow=fuelcell_set['min_flow']
                                       )
for i, row in connection.iterrows():
    try:
        row['more']
    except KeyError:
        world.connect(eval(row['send']), eval(row['receive']), (row['messages'], row['messager']))
    else:
        if row['more'] == 'async_requests=True':
            # world.connect(eval(row['send']),eval(row['receive']),(row['messages'],row['messager']),
            #               time_shifted=True, initial_data={row['messages']: 0})
            world.connect(eval(row['send']), eval(row['receive']), (row['messages'], row['messager']), async_requests=True)
        else:
            world.connect(eval(row['send']), eval(row['receive']), (row['messages'], row['messager']))
if realtimefactor == 0:
    world.run(until=end)
else:
    world.run(until=end, rt_factor=realtimefactor)
#################################final results show############################################
if RESULTS_SHOW_TYPE['Finalresults_show'] == True:
    import matplotlib.pyplot as plt
    import matplotlib
    # matplotlib.use('TkAgg')
    import pandas as pd

    data = pd.read_csv(outputfile)
    # Get all axes of figure
    fig = plt.figure()
    fig.subplots_adjust(hspace=0.5, wspace=0.5)
    fig.suptitle('simulation results')
    # Plot new data
    ax1 = fig.add_subplot(221)
    try:
        ax1.plot(data['PV-0.pv_0-pv_gen'])
    except KeyError:
        print('There is no PV model')
    ax1.set_title('PV power')
    ax1.set_xlabel('time')
    ax1.set_ylabel('P [kW]')

    ax2 = fig.add_subplot(222)
    try:
        ax2.plot(data['Wind-0.wind_0-wind_gen'])
    except KeyError:
        print('There is no Wind model')
    ax2.set_title('Wind power')
    ax2.set_xlabel('time')
    ax2.set_ylabel('P [kW]')

    ax3 = fig.add_subplot(223)
    try:
        ax3.plot(data['H2storage-0.h2storage_0-h2_soc'])
    except KeyError:
        print('There is no H2 model')
    ax3.set_title('H2storage SOC')
    ax3.set_xlabel('time')
    ax3.set_ylabel('soc [%]')

    ax4 = fig.add_subplot(224)
    try:
        ax4.plot(data['Battery-0.Battery_0-soc'])
    except KeyError:
        print('There is no battery model')
    ax4.set_title('Battery SOC')
    ax4.set_xlabel('time')
    ax4.set_ylabel('soc [%]')
    plt.show()
