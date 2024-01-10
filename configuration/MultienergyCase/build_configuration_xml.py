import pandas as pd



sim_config=[['Wind' ,'python','Models.Wind.wind_mosaik:WindSim'],
            ['PV' ,'python', 'Models.PV.pv_mosaik:PvAdapter'],
            ['Load', 'python', 'Models.Load.load_mosaik:loadSim'],
            ['Collector', 'python', 'Models.collector:Collector'],
            ['CSVB', 'python', 'Models.mosaik_csv:CSV'],
            ['ElectricityNetwork', 'python', 'Models.Elenetwork.electricity_network_mosaik:electricitynetworkSim'],
            ['Battery', 'python', 'Models.Battery.battery_mosaik:BatteryholdSim'],
            ['Electrolyser', 'python', 'Models.Electrolyser.electrolyser_mosaik:ElectrolyserSim'],
            ['H2storage', 'python', 'Models.H2storage.h2storage_mosaik:compressedhydrogen'],
            ['Fuelcell', 'python', 'Models.Fuelcell.fuelcell_mosaik:FuelCellSim'],
            ['H2Network', 'python', 'Models.H2network.gas_network_mosaik:gasnetworkSim'],
            ['H2product','python', 'Models.H2product.h2product_mosaik:h2productSim'],
            ['H2demand','python', 'Models.H2demand.h2demand_mosaik:h2demandSim'],
            ['HeatNetwork', 'python', 'Models.Heatnetwork.heat_network_mosaik:heatnetworkSim'],
            ['HeatStorage', 'python', 'Models.Heatstorage.qstorage_mosaik:heatstorageSim'],
            ['Heatproduct', 'python', 'Models.Heatproduct.qproduct_mosaik:qproductSim'],
            ['Heatdemand', 'python', 'Models.Heatdemand.qdemand_mosaik:qdemandSim'],
            ['HeatPump','python', 'Models.Heatpump.heatpump.Heat_Pump_mosaik:HeatPumpSimulator'],
            ['Eboiler', 'python', 'Models.Eboiler.eboiler_mosaik:eboilerSim'],
            ['Qvalve', 'python', 'Models.Valves.qvalve_mosaik:qvalveSim'],
            ['H2Valve','python', 'Models.Valves.h2valve_mosaik:h2valveSim'],
            ]
sim_config_df=pd.DataFrame(sim_config, columns=['model','method','location'])
sim_config_data=sim_config_df.to_xml()

with open('../../Cases/MultienergyCase/config.xml','w') as file:
    file.write(sim_config_data)

connection=[
    ['pv[0]', 'enetwork[0]', 'pv_gen', 'p_in[0]'],
    ['wind_on[0]', 'enetwork[0]', 'wind_gen', 'p_in[1]'],
    ['wind_off[0]', 'enetwork[0]', 'wind_gen', 'p_in[2]'],
    ['load[0]', 'enetwork[0]', 'load_dem', 'p_out[0]'],
    ['battery[0]', 'enetwork[0]', 'p_out', 'p_out[1]'],

    ['enetwork[0]', 'monitor', 'p_in[0]','p_in[0]'],
    ['enetwork[0]', 'monitor', 'p_in[1]','p_in[1]'],
    ['enetwork[0]', 'monitor', 'p_in[2]','p_in[2]'],
    ['enetwork[0]', 'monitor', 'p_out[0]','p_out[0]'],
    ['enetwork[0]', 'monitor', 'p_out[1]','p_out[1]'],
    ['enetwork[0]', 'monitor', 'p_tot','p_tot'],
    ['battery[0]', 'monitor', 'soc','soc'],
    ['battery[0]', 'monitor', 'p_out','p_out'],
    ['battery[0]', 'monitor', 'flag','flag'],


    ['electrolyser[0]', 'h2valve[0]', 'h2_gen', 'h2_elec'],
    ['h2storage[0]', 'h2valve[0]', 'h2_flow', 'h2_stor'],
    ['fuelcell[0]', 'h2valve[0]', 'h2_consume', 'h2_fc'],

    ['fuelcell[0]', 'enetwork[0]', 'fc_gen', 'p_in[3]'],
    ['electrolyser[0]', 'enetwork[0]', 'flow2e', 'p_out[2]'],
    ['enetwork[0]', 'monitor', 'p_in[3]','p_in[3]'],
    ['enetwork[0]', 'monitor', 'p_out[2]','p_out[2]'],
    ['electrolyser[0]', 'monitor', 'q_product','q_product'],
    ['fuelcell[0]', 'monitor', 'q_product','q_product'],

    ['h2valve[0]', 'monitor', 'h2_elec','h2_elec'],
    ['h2valve[0]', 'monitor', 'h2_stor','h2_stor'],
    ['h2valve[0]', 'monitor', 'h2_fc','h2_fc'],
    ['h2valve[0]', 'monitor', 'h2_elec_stor','h2_elec_stor'],
    ['h2valve[0]', 'monitor', 'h2_stor_fc','h2_stor_fc'],
    ['h2valve[0]', 'monitor', 'h2_elec_net','h2_elec_net'],
    ['h2valve[0]', 'monitor', 'h2_fc_net','h2_fc_net'],
    ['h2valve[0]', 'monitor', 'h2_stor_net','h2_stor_net'],
    ['h2storage[0]', 'monitor', 'h2_soc','h2_soc'],


    ['h2valve[0]', 'h2network[0]', 'h2_elec_net', 'flow_in[0]'],
    ['h2valve[0]', 'h2network[0]', 'h2_stor_net', 'flow_in[1]'],
    ['h2valve[0]', 'h2network[0]', 'h2_fc_net', 'flow_out[0]'],

    ['h2network[0]', 'monitor', 'flow_in[0]','flow_in[0]'],
    ['h2network[0]', 'monitor', 'flow_in[1]','flow_in[1]'],
    ['h2network[0]', 'monitor', 'flow_out[0]','flow_out[0]'],
    ['h2network[0]', 'monitor', 'p_int','p_int'],
    ['h2network[0]', 'monitor', 'flow_tot','flow_tot'],


    ['h2demand_r[0]', 'h2network[0]', 'h2demand_dem','flow_out[1]'],
    ['h2demand_fs[0]', 'h2network[0]', 'h2demand_dem','flow_out[2]'],
    ['h2demand_ev[0]', 'h2network[0]', 'h2demand_dem','flow_out[3]'],
    ['h2product[0]', 'h2network[0]', 'h2product_gen', 'flow_in[2]'],

    ['h2network[0]', 'monitor', 'flow_out[1]','flow_out[1]'],
    ['h2network[0]', 'monitor', 'flow_out[2]','flow_out[2]'],
    ['h2network[0]', 'monitor', 'flow_out[3]','flow_out[3]'],
    ['h2network[0]', 'monitor', 'flow_in[2]','flow_in[2]'],

    ['ttrailers[0]', 'h2network[0]', 'h2_flow', 'flow_out[4]'],
    ['ttrailers[0]', 'monitor', 'h2_soc','h2_soc'],
    ['h2network[0]', 'monitor', 'flow_out[4]','flow_out[4]'],

    ['electrolyser[0]', 'heatnetwork[0]', 'q_product', 'q_in[0]'],
    ['fuelcell[0]', 'heatnetwork[0]', 'q_product', 'q_in[1]'],
    ['heatnetwork[0]', 'monitor', 'q_in[0]','q_in[0]'],
    ['heatnetwork[0]', 'monitor', 'q_in[1]','q_in[1]'],
    ['heatnetwork[0]', 'monitor', 't_int','t_int'],
    ['heatnetwork[0]', 'monitor', 'q_loss','q_loss'],

    ['heatstorage_s[0]', 'heatnetwork[0]', 'q_flow', 'q_out[0]'],
    ['heatnetwork[0]', 'monitor', 'q_out[0]','q_out[0]'],
    ['heatstorage_s[0]', 'monitor', 't_int','t_int'],
    ['heatstorage_s[0]', 'monitor', 'q_loss','q_loss'],
    ['heatstorage_s[0]', 'monitor', 'q_soc','q_soc'],

    ['heatstorage_d[0]', 'heatnetwork[0]', 'q_flow', 'q_out[1]'],
    ['heatnetwork[0]', 'monitor', 'q_out[1]','q_out[1]'],
    ['heatstorage_d[0]', 'monitor', 't_int','t_int'],
    ['heatstorage_d[0]', 'monitor', 'q_loss','q_loss'],
    ['heatstorage_d[0]', 'monitor', 'q_soc','q_soc'],

    ['heatdemand_r[0]', 'heatnetwork[0]', 'qdemand_dem', 'q_out[2]'],
    ['heatdemand_i[0]', 'heatnetwork[0]', 'qdemand_dem', 'q_out[3]'],
    ['heatproduct[0]', 'heatnetwork[0]', 'qproduct_gen', 'q_in[2]'],

    ['heatnetwork[0]', 'monitor', 'q_out[2]','q_out[2]'],
    ['heatnetwork[0]', 'monitor', 'q_out[3]','q_out[3]'],
    ['heatnetwork[0]', 'monitor', 'q_in[2]','q_in[2]'],

    ['heatpump', 'enetwork[0]', 'P_Required', 'p_out[3]'],
    ['enetwork[0]', 'monitor', 'p_out[3]','p_out[3]'],
    ['heatpump', 'heatnetwork[0]', 'Q_Supplied', 'q_in[3]'],
    ['heatnetwork[0]', 'monitor', 'q_in[3]','q_in[3]'],

    ['eboiler[0]', 'enetwork[0]', 'eboiler_dem', 'p_out[4]'],
    ['eboiler[0]', 'qvalve[0]', 'q_gen', 'q_eboiler'],
    ['heatstorage[0]', 'qvalve[0]', 'q_flow', 'q_stor'],

    ['qvalve[0]', 'monitor', 'q_eboiler','q_eboiler'],
    ['qvalve[0]', 'monitor', 'q_stor','q_stor'],
    ['qvalve[0]', 'monitor', 'q_eboiler_stor','q_eboiler_stor'],
    ['qvalve[0]', 'monitor', 'q_eboiler_net','q_eboiler_net'],
    ['qvalve[0]', 'monitor', 'q_stor_net','q_stor_net'],
    ['heatstorage[0]', 'monitor', 'q_soc', 'q_soc'],
    ['qvalve[0]', 'heatnetwork[0]', 'q_eboiler_net', 'q_in[4]'],
    ['qvalve[0]', 'heatnetwork[0]', 'q_stor_net', 'q_in[5]'],

]

try:
    df=pd.DataFrame(connection, columns=['send','receive','messages','messager','more'])
except ValueError:
    df=pd.DataFrame(connection, columns=['send','receive','messages','messager'])
data=df.to_xml()

with open('../../Cases/MultienergyCase/connection.xml','w') as file:
    file.write(data)
