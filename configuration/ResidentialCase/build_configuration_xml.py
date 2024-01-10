import pandas as pd


sim_config=[['Wind' ,'python','Models.Wind.wind_mosaik:WindSim'],
            ['PV' ,'python', 'Models.PV.pv_mosaik:PvAdapter'],
            ['Load','python', 'Models.Load.load_mosaik:loadSim'],
            ['Collector','python', 'Models.collector:Collector'],
            ['CSVB','python', 'Models.mosaik_csv:CSV'],
            ['Controller','python', 'Controllers.ResidentialController.controller_mosaik:controlSim'],
            ['Battery','python', 'Models.Battery.battery_mosaik:BatteryholdSim'],
            ['Electrolyser','python', 'Models.Electrolyser.electrolyser_mosaik:ElectrolyserSim'],
            ['H2storage','python', 'Models.H2storage.h2storage_mosaik:compressedhydrogen'],
            ['Fuelcell','python', 'Models.Fuelcell.fuelcell_mosaik:FuelCellSim'],]
# sim_config=[['Wind' ,'connect','192.168.0.1:5123'],
#             ['PV' ,'connect','192.168.0.2:5123'],
#             ['Load','connect','192.168.0.3:5123'],
#             ['Battery','connect','192.168.0.4:5123'],
#             ['Collector','python', 'Models.collector:Collector'],
#             ['CSVB','python', 'mosaik_csv:CSV'],
#             ['Controller','python', 'Models.Controller.controller_mosaik:controlSim'],
#             #['H2storage','connect', '192.168.0.2:5123'],
#             #['PV','connect', '192.168.0.1:5123'],
#             ['Electrolyser','python', 'Models.Electrolyser.electrolyser_mosaik:ElectrolyserSim'],
#             ['H2storage','python', 'Models.H2storage.h2storage_mosaik:compressedhydrogen'],
#             ['Fuelcell','python', 'Models.Fuelcell.fuelcell_mosaik:FuelCellSim'],
#             ]
sim_config_df=pd.DataFrame(sim_config, columns=['model','method','location'])
sim_config_data=sim_config_df.to_xml()

with open('../../Cases/ResidentialCase/config.xml','w') as file:
    file.write(sim_config_data)
# sim_config_ddf=pd.read_xml('config.xml')
# sim_config={row[1]:{row[2]:row[3]}for row in sim_config_ddf.values}

# tosh=sim_config_ddf[sim_config_ddf['method']=='connection']
# #! /usr/bin/env python
#
# with open ('run.sh', 'w') as rsh:
#     rsh.write('''\
# #! /bin/bash''')
#     for row in tosh.values:
#         rsh.write("\n"+"ssh illuminator@"+row[3]+"'./run"+row[1]+".sh'")
connection=[['pv[0]', 'ctrl', 'pv_gen','pv_gen'],
             ['wind[0]', 'ctrl', 'wind_gen','wind_gen'],
             ['load[0]', 'ctrl', 'load_dem','load_dem'],
             #['battery', 'ctrl','soc','soc'],
             #['h2storage', 'ctrl', 'h2_soc','h2_soc'],
             ['ctrl', 'battery', 'flow2b','flow2b','async_requests=True'],
             ['ctrl', 'electrolyser', 'flow2e','flow2e','async_requests=True'],
             ['ctrl', 'fuelcell', 'h2_out', 'h2_consume','async_requests=True'],
             ['electrolyser', 'h2storage', 'h2_gen', 'eleh2_in'],
             ['fuelcell', 'h2storage', 'fc_gen','fuelh2_out'],
             ['battery', 'monitor', 'p_out','p_out'],
             ['battery', 'monitor', 'soc','soc'],
             ['pv[0]', 'monitor', 'pv_gen','pv_gen'],
             ['wind[0]', 'monitor', 'wind_gen','wind_gen'],
             ['load[0]', 'monitor', 'load_dem','load_dem'],
             ['ctrl', 'monitor', 'flow2b','flow2b'],
             ['ctrl', 'monitor', 'flow2e','flow2e'],
             ['ctrl', 'monitor', 'h2_out','h2_out'],
             ['electrolyser', 'monitor', 'h2_gen','h2_gen'],
             ['h2storage', 'monitor', 'eleh2_in','eleh2_in'],
             ['h2storage', 'monitor', 'fuelh2_out','fuelh2_out'],
             ['h2storage', 'monitor', 'h2_soc','h2_soc'],
             ['fuelcell', 'monitor', 'fc_gen','fc_gen']]
try:
    df=pd.DataFrame(connection, columns=['send','receive','messages','messager','more'])
except ValueError:
    df=pd.DataFrame(connection, columns=['send','receive','messages','messager'])
data=df.to_xml()

with open('../../Cases/ResidentialCase/connection.xml','w') as file:
    file.write(data)
