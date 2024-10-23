import subprocess
import mosaik.util
import numpy as np
import pandas as pd
from io import StringIO
import itertools
import Models.Elenetwork.electricity_network_mosaik as en
import Models.H2network.gas_network_mosaik as h2n
import Models.Heatnetwork.heat_network_mosaik as qn
from configuration.buildmodelset import *

# ERROR:
# mosaik.exceptions.ScenarioError: Simulator "HeatPump" could not be started: Could not import module: No module named 'Heat_Pump_Model' --> No module named 'Heat_Pump_Model'
# !!!UPDATE ON ERROR:
# With the environment yaml alex gave, this actually runs

outputfile='Result/MultienergyCase/results.csv'
sim_config_file="Cases/MultienergyCase/"
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

START_DATE = '2012-01-01 00:00:00'
end = 1 * 24 * 3600  # last one interval is not computed

WIND_on_DATA = 'Scenarios/winddata_NL.txt'  # same wind but different turbines
WIND_off_DATA = 'Scenarios/winddata_NL.txt'
Pv_DATA = 'Scenarios/pv_data_Rotterdam_NL-15min.txt'
load_DATA = 'Scenarios/load_data.txt'
battery_DATA = 'Scenarios/battery_data.txt'
electrolyser_DATA = 'Scenarios/electrolyser_data.txt'
h2storage_DATA = 'Scenarios/h2storage_data.txt'
ttrailers_DATA = 'Scenarios/ttrailers_data.txt'
fuelcell_DATA = 'Scenarios/fuelcell_data.txt'
h2product_DATA = 'Scenarios/h2product_data.txt'
h2demand_r_DATA = 'Scenarios/h2demand_r_data.txt'
h2demand_fs_DATA = 'Scenarios/h2demand_fs_data.txt'
h2demand_ev_DATA = 'Scenarios/h2demand_ev_data.txt'
qstorage_DATA = 'Scenarios/qstorage_data.txt'
qstorage_s_DATA = 'Scenarios/qstorage_s_data.txt'
qstorage_d_DATA = 'Scenarios/qstorage_d_data.txt'
qproduct_DATA = 'Scenarios/qproduct_data.txt'
qdemand_i_DATA = 'Scenarios/qdemand_i_data.txt'
qdemand_r_DATA = 'Scenarios/qdemand_r_data.txt'
hp_DATA = 'Scenarios/hp_data.txt'
eboiler_DATA = 'Scenarios/eboiler_data.txt'

# set up the "world" of the scenario
models = pd.concat([connection["send"], connection["receive"]])
models = models.drop_duplicates(keep='first', inplace=False)
models.reset_index(drop=True, inplace=True)


def inremental_attributes():
    global incr_attr_added, row
    connection_list = pd.DataFrame(connection).replace(np.nan, 'NA').values.tolist()  # Replace missing values with 'NA'
    incr_attr = [en.incremental_attributes, h2n.incremental_attributes,
                 qn.incremental_attributes]  # find inc. attr. in files
    incr_attr_added = [[], [], []]
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
                    en.META['models']['ElectricityNetwork']['attrs'].append(attr_value)
                    en.META['models']['ElectricityNetwork']['attrs'] = \
                        list(dict.fromkeys(en.META['models']['ElectricityNetwork']['attrs']))
            elif row == 1:
                for attr_value in incr_attr_added[row]:
                    h2n.META['models']['GasNetwork']['attrs'].append(attr_value)
                    h2n.META['models']['GasNetwork']['attrs'] = \
                        list(dict.fromkeys(h2n.META['models']['GasNetwork']['attrs']))
            elif row == 2:
                for attr_value in incr_attr_added[row]:
                    qn.META['models']['HeatNetwork']['attrs'].append(attr_value)
                    qn.META['models']['HeatNetwork']['attrs'] = \
                        list(dict.fromkeys(qn.META['models']['HeatNetwork']['attrs']))
    incr_attr_added = list(itertools.chain(*incr_attr_added))


inremental_attributes()

############################## start simulation

world = mosaik.World(sim_config, debug=True)

Defined_models = pd.DataFrame()
Defined_models['model'] = pd.Series(['HeatPump', 'Wind_on', 'Wind_off', 'PV', 'Load', 'Battery', 'Enetwork',
                                     'Fuelcell', 'H2Storage', 'Electrolyser',
                                     'H2network', 'H2product',
                                     'H2demand_r', 'H2demand_fs', 'H2demand_ev', 'Ttrailers',
                                     'Heatnetwork', 'Heatstorage_s', 'Heatstorage_d',
                                     'Heatdemand_i', 'Heatdemand_r', 'Heatproduct', 'Eboiler',
                                     'Qvalve', 'Heatstorage','H2Valve'])
number = []
for model in Defined_models['model']:
    number.append(
        int((models.str.startswith(model.lower()) == True).sum())
    )
Defined_models['number'] = number
collector = world.start('Collector', start_date=START_DATE, results_show=RESULTS_SHOW_TYPE,output_file=outputfile)
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

    elif model_i[1]['model'] == 'Wind_on':
        WSdata = world.start('CSVB', sim_start=START_DATE, datafile=WIND_on_DATA)
        wind_on_sim = world.start('Wind')
        wind_on = wind_on_sim.windmodel.create(model_i[1]['number'], sim_start=START_DATE,
                                               p_rated=Wind_on_set['p_rated'], u_rated=Wind_on_set['u_rated'],
                                               u_cutin=Wind_on_set['u_cutin'], u_cutout=Wind_on_set['u_cutout'],
                                               cp=Wind_on_set['cp'], diameter=Wind_on_set['diameter'],
                                               output_type=Wind_on_set['output_type'])
        windspeed_on_data = WSdata.WS_datafile.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(windspeed_on_data[i], wind_on[i], 'u')

    elif model_i[1]['model'] == 'Wind_off':
        WSdata = world.start('CSVB', sim_start=START_DATE, datafile=WIND_off_DATA)
        wind_off_sim = world.start('Wind')
        wind_off = wind_off_sim.windmodel.create(model_i[1]['number'], sim_start=START_DATE,
                                                 p_rated=Wind_off_set['p_rated'], u_rated=Wind_off_set['u_rated'],
                                                 u_cutin=Wind_off_set['u_cutin'], u_cutout=Wind_off_set['u_cutout'],
                                                 cp=Wind_off_set['cp'], diameter=Wind_off_set['diameter'],
                                                 output_type=Wind_off_set['output_type'])
        windspeed_off_data = WSdata.WS_datafile.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(windspeed_off_data[i], wind_off[i], 'u')

    elif model_i[1]['model'] == 'Load':
        loaddata = world.start('CSVB', sim_start=START_DATE, datafile=load_DATA)
        loadsim = world.start('Load')
        load = loadsim.loadmodel.create(model_i[1]['number'], sim_start=START_DATE,
                                        houses=load_set['houses'], output_type=load_set['output_type'])
        load_data = loaddata.Load_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(load_data[i], load[i], 'load')

    elif model_i[1]['model'] == 'Enetwork':
        enetsim = world.start('ElectricityNetwork')
        enetwork = enetsim.ElectricityNetwork.create(model_i[1]['number'], sim_start=START_DATE,
                                                     max_congestion=enetwork_set['max_congestion'],
                                                     p_loss_m=enetwork_set['p_loss_m'],
                                                     length=enetwork_set['length'])

    elif model_i[1]['model'] == 'Battery' and model_i[1]['number'] != 0:
        batterydata = world.start('CSVB', sim_start=START_DATE, datafile=battery_DATA)
        batterysim = world.start('Battery')
        battery = batterysim.Batteryset.create(model_i[1]['number'], sim_start=START_DATE,
                                               initial_set=Battery_initialset, battery_set=Battery_set)
        battery_data = batterydata.Battery_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(battery_data[i], battery[i], 'flow2b')

    elif model_i[1]['model'] == 'Electrolyser':
        electrodata = world.start('CSVB', sim_start=START_DATE, datafile=electrolyser_DATA)
        electrosim = world.start('Electrolyser')
        electrolyser = electrosim.electrolysermodel.create(model_i[1]['number'], sim_start=START_DATE,
                                                           eff=electrolyser_set['eff'],
                                                           resolution=electrolyser_set['resolution'],
                                                           term_eff=electrolyser_set['term_eff'],
                                                           rated_power=electrolyser_set['rated_power'],
                                                           ramp_rate=electrolyser_set['ramp_rate'])
        electrolyser_data = electrodata.Electrolyser_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(electrolyser_data[i], electrolyser[i], 'flow2e')

    elif model_i[1]['model'] == 'Fuelcell':
        fuelcelldata = world.start('CSVB', sim_start=START_DATE, datafile=fuelcell_DATA)
        fcsim = world.start('Fuelcell')
        fuelcell = fcsim.fuelcellmodel.create(model_i[1]['number'], sim_start=START_DATE,
                                              eff=fuelcell_set['eff'], resolution=fuelcell_set['resolution'],
                                               term_eff=fuelcell_set['term_eff'],
                                               max_flow=fuelcell_set['max_flow'],
                                               min_flow=fuelcell_set['min_flow'])
        fuelcell_data = fuelcelldata.Fuelcell_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(fuelcell_data[i], fuelcell[i], 'h2_consume')

    elif model_i[1]['model'] == 'H2Storage':
        h2storagedata = world.start('CSVB', sim_start=START_DATE, datafile=h2storage_DATA)
        h2storagesim = world.start('H2storage')
        h2storage = h2storagesim.compressed_hydrogen.create(model_i[1]['number'], sim_start=START_DATE,
                                                            initial_set=h2storage_initial, h2_set=h2_set)
        h2storage_data = h2storagedata.H2storage_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(h2storage_data[i], h2storage[i], 'flow2h2s')

    elif model_i[1]['model'] == 'Ttrailers':
        ttrailersdata = world.start('CSVB', sim_start=START_DATE, datafile=ttrailers_DATA)
        ttrailerssim = world.start('H2storage')
        ttrailers = ttrailerssim.compressed_hydrogen.create(model_i[1]['number'], sim_start=START_DATE,
                                                            initial_set=ttrailers_initial, h2_set=h2_set)
        ttrailers_data = ttrailersdata.Ttrailers_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(ttrailers_data[i], ttrailers[i], 'flow2h2s')

    elif model_i[1]['model'] == 'H2Valve':
        h2valvesim = world.start('H2Valve')
        h2valve = h2valvesim.H2Valve.create(model_i[1]['number'], sim_start=START_DATE)

    elif model_i[1]['model'] == 'H2network':
        h2netsim = world.start('H2Network')
        h2network = h2netsim.GasNetwork.create(model_i[1]['number'], sim_start=START_DATE,
                                             max_congestion=h2network_set['max_congestion'],
                                             V=h2network_set['V'],
                                             leakage=h2network_set['leakage'])

    elif model_i[1]['model'] == 'H2demand_r':
        h2demand_rdata = world.start('CSVB', sim_start=START_DATE, datafile=h2demand_r_DATA)
        h2demand_rsim = world.start('H2demand')
        h2demand_r = h2demand_rsim.h2demandmodel.create(model_i[1]['number'], sim_start=START_DATE,
                                                        houses=h2demand_r_set['houses'])
        h2demand_r_data = h2demand_rdata.H2demand_r_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(h2demand_r_data[i], h2demand_r[i], 'h2demand')

    elif model_i[1]['model'] == 'H2demand_fs':
        h2demand_fsdata = world.start('CSVB', sim_start=START_DATE, datafile=h2demand_fs_DATA)
        h2demand_fssim = world.start('H2demand')
        h2demand_fs = h2demand_fssim.h2demandmodel.create(model_i[1]['number'], sim_start=START_DATE,
                                                          houses=h2demand_fs_set['tanks'])
        h2demand_fs_data = h2demand_fsdata.H2demand_fs_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(h2demand_fs_data[i], h2demand_fs[i], 'h2demand')

    elif model_i[1]['model'] == 'H2demand_ev':
        h2demand_evdata = world.start('CSVB', sim_start=START_DATE, datafile=h2demand_ev_DATA)
        h2demand_evsim = world.start('H2demand')
        h2demand_ev = h2demand_evsim.h2demandmodel.create(model_i[1]['number'], sim_start=START_DATE,
                                                          houses=h2demand_ev_set['cars'])
        h2demand_ev_data = h2demand_evdata.H2demand_ev_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(h2demand_ev_data[i], h2demand_ev[i], 'h2demand')

    elif model_i[1]['model'] == 'H2product':
        h2productdata = world.start('CSVB', sim_start=START_DATE, datafile=h2product_DATA)
        h2productsim = world.start('H2product')
        h2product = h2productsim.h2productmodel.create(model_i[1]['number'], sim_start=START_DATE,
                                                       houses=h2product_set['houses'])
        h2product_data = h2productdata.H2product_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(h2product_data[i], h2product[i], 'h2product')

    elif model_i[1]['model'] == 'Heatnetwork':
        heatnetsim = world.start('HeatNetwork')
        heatnetwork = heatnetsim.HeatNetwork.create(model_i[1]['number'], sim_start=START_DATE,
                                              max_temperature=heatnetwork_set['max_temperature'],
                                              insulation=heatnetwork_set['insulation'],
                                              ext_temp=heatnetwork_set['ext_temp'],
                                              therm_cond=heatnetwork_set['therm_cond'],
                                              length=heatnetwork_set['length'],
                                              diameter=heatnetwork_set['diameter'],
                                              density=heatnetwork_set['density'],
                                              c=heatnetwork_set['c'])

    elif model_i[1]['model'] == 'Heatstorage':
        heatstoragedata = world.start('CSVB', sim_start=START_DATE, datafile=qstorage_DATA)
        heatstoragesim = world.start('HeatStorage')
        heatstorage = heatstoragesim.HeatStorage.create(model_i[1]['number'], sim_start=START_DATE,
                                                  soc_init=heatstorage_set['soc_init'],
                                                  max_temperature=heatstorage_set['max_temperature'],
                                                  min_temperature=heatstorage_set['min_temperature'],
                                                  insulation=heatstorage_set['insulation'],
                                                  ext_temp=heatstorage_set['ext_temp'],
                                                  therm_cond=heatstorage_set['therm_cond'],
                                                  length=heatstorage_set['length'],
                                                  diameter=heatstorage_set['diameter'],
                                                  density=heatstorage_set['density'],
                                                  c=heatstorage_set['c'],
                                                  eff=heatstorage_set['eff'],
                                                  max_q=heatstorage_set['max_q'], min_q=heatstorage_set['min_q'])
        heatstorage_data = heatstoragedata.Qstorage_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(heatstorage_data[i], heatstorage[i], 'flow2qs')

    elif model_i[1]['model'] == 'Heatstorage_s':
        heatstorage_sdata = world.start('CSVB', sim_start=START_DATE, datafile=qstorage_s_DATA)
        heatstorage_ssim = world.start('HeatStorage')
        heatstorage_s = heatstorage_ssim.HeatStorage.create(model_i[1]['number'], sim_start=START_DATE,
                                                         soc_init=heatstorage_s_set['soc_init'],
                                                         max_temperature=heatstorage_s_set['max_temperature'],
                                                         min_temperature=heatstorage_s_set['min_temperature'],
                                                         insulation=heatstorage_s_set['insulation'],
                                                         ext_temp=heatstorage_s_set['ext_temp'],
                                                         therm_cond=heatstorage_s_set['therm_cond'],
                                                         length=heatstorage_s_set['length'],
                                                         diameter=heatstorage_s_set['diameter'],
                                                         density=heatstorage_s_set['density'],
                                                         c=heatstorage_s_set['c'],
                                                         eff=heatstorage_s_set['eff'],
                                                         max_q=heatstorage_s_set['max_q'],
                                                            min_q=heatstorage_s_set['min_q'])
        heatstorage_s_data = heatstorage_sdata.Qstorage_s_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(heatstorage_s_data[i], heatstorage_s[i], 'flow2qs')


    elif model_i[1]['model'] == 'Heatdemand_r':
        heatdemand_rdata = world.start('CSVB', sim_start=START_DATE, datafile=qdemand_r_DATA)
        heatdemand_rsim = world.start('Heatdemand')
        heatdemand_r = heatdemand_rsim.qdemandmodel.create(model_i[1]['number'], sim_start=START_DATE,
                                                           utilities=heatdemand_r_set['houses'])
        heatdemand_r_data = heatdemand_rdata.Qdemand_r_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(heatdemand_r_data[i], heatdemand_r[i], 'qdemand')

    elif model_i[1]['model'] == 'Heatdemand_i':
        heatdemand_idata = world.start('CSVB', sim_start=START_DATE, datafile=qdemand_i_DATA)
        heatdemand_isim = world.start('Heatdemand')
        heatdemand_i = heatdemand_isim.qdemandmodel.create(model_i[1]['number'], sim_start=START_DATE,
                                                           utilities=heatdemand_i_set['factories'])
        heatdemand_i_data = heatdemand_idata.Qdemand_i_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(heatdemand_i_data[i], heatdemand_i[i], 'qdemand')

    elif model_i[1]['model'] == 'Heatproduct':
        heatproductdata = world.start('CSVB', sim_start=START_DATE, datafile=qproduct_DATA)
        heatproductsim = world.start('Heatproduct')
        heatproduct = heatproductsim.qproductmodel.create(model_i[1]['number'], sim_start=START_DATE,
                                                    utilities=heatproduct_set['utilities'])
        heatproduct_data = heatproductdata.Qproduct_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(heatproduct_data[i], heatproduct[i], 'qproduct')

    elif model_i[1]['model'] == 'Heatstorage_d':
        heatstorage_ddata = world.start('CSVB', sim_start=START_DATE, datafile=qstorage_d_DATA)
        heatstorage_dsim = world.start('HeatStorage')
        heatstorage_d = heatstorage_dsim.HeatStorage.create(model_i[1]['number'], sim_start=START_DATE,
                                                      soc_init=heatstorage_d_set['soc_init'],
                                                      max_temperature=heatstorage_d_set['max_temperature'],
                                                      min_temperature=heatstorage_d_set['min_temperature'],
                                                      insulation=heatstorage_d_set['insulation'],
                                                      ext_temp=heatstorage_d_set['ext_temp'],
                                                      therm_cond=heatstorage_d_set['therm_cond'],
                                                      length=heatstorage_d_set['length'],
                                                      diameter=heatstorage_d_set['diameter'],
                                                      density=heatstorage_d_set['density'],
                                                      c=heatstorage_d_set['c'],
                                                      eff=heatstorage_d_set['eff'],
                                                      max_q=heatstorage_d_set['max_q'], min_q=heatstorage_d_set['min_q'])
        heatstorage_d_data = heatstorage_ddata.Qstorage_d_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(heatstorage_d_data[i], heatstorage_d[i], 'flow2qs')

    elif model_i[1]['model'] == 'Eboiler':
        eboilerdata = world.start('CSVB', sim_start=START_DATE, datafile=eboiler_DATA)
        eboilersim = world.start('Eboiler')
        eboiler = eboilersim.eboilermodel.create(model_i[1]['number'], sim_start=START_DATE,
                                                 eboiler_set=eboiler_set)
        eboiler_data = eboilerdata.Eboiler_data.create(model_i[1]['number'])
        for i in range(model_i[1]['number']):
            world.connect(eboiler_data[i], eboiler[i], 'eboiler_dem')

    elif model_i[1]['model'] == 'Qvalve':
        qvalvesim = world.start('Qvalve')
        qvalve = qvalvesim.Qvalve.create(model_i[1]['number'], sim_start=START_DATE)


    elif model_i[1]['model'] == 'HeatPump':
        heatpumpsim = world.start('HeatPump', step_size=15 * 60)
        csv = world.start('CSVB', sim_start=START_DATE, datafile=hp_DATA)

        # Instantiate models
        heatpump = heatpumpsim.HeatPump(params=hp_params)
        heat_load = csv.Hp_data()

        # Connect entities
        world.connect(heat_load, heatpump, ('Q_Demand', 'Q_Demand'), ('heat_source_T', 'heat_source_T'),
                      ('heat_source_T','T_amb'),('cond_in_T', 'cond_in_T'))

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
                          initial_data={row['message']: 0})  # time_shifted=True, initial_data={row['message']: 0}
            print(f'Connect {row["send"]} to {row["receive"]} output {row["messages"]} input {row["messager"]} with time_shift')

if realtimefactor == 0:
    world.run(until=end)
else:
    world.run(until=end, rt_factor=realtimefactor)
