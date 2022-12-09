import pandas as pd


# sim_config=[['Wind' ,'python','Wind.wind_mosaik:WindSim'],
#             ['PV' ,'python', 'PV.PV_mosaik:PvAdapter'],
#             ['Load','python', 'Load.load_mosaik:loadSim'],
#             ['Collector','python', 'collector:Collector'],
#             ['CSVB','python', 'mosaik_csvread:CSV'],
#             ['Controller','python', 'Controller.controller_mosaik:controlSim'],
#             ['Battery','python', 'Battery.battery_mosaik:BatteryholdSim'],
#             ['Electrolyser','python', 'Electrolyser.electrolyser_mosaik:ElectrolyserSim'],
#             ['H2storage','python', 'H2storage.h2storage_mosaik:compressedhydrogen'],
#             ['Fuelcell','python', 'Fuelcell.fuelcell_mosaik:FuelCellSim'],]
sim_config=[['Wind' ,'python','Models.Wind.wind_mosaik:WindSim'],
            ['PV' ,'python', 'Models.PV.pv_mosaik:PvAdapter'],
            ['Load','python', 'Models.Load.load_mosaik:loadSim'],
            ['Collector','python', 'Models.collector:Collector'],
            ['CSVB','python', 'mosaik_csv:CSV'],
            ['Controller','python', 'Models.Controller.controller_mosaik:controlSim'],
            ['Battery','python', 'Models.Battery.battery_mosaik:BatteryholdSim'],
            #['H2storage','connect', '192.168.0.2:5123'],
            #['PV','connect', '192.168.0.1:5123'],
            ['Electrolyser','python', 'Models.Electrolyser.electrolyser_mosaik:ElectrolyserSim'],
            ['H2storage','python', 'Models.H2storage.h2storage_mosaik:compressedhydrogen'],
            ['Fuelcell','python', 'Models.Fuelcell.fuelcell_mosaik:FuelCellSim'],
            ]
sim_config_df=pd.DataFrame(sim_config, columns=['model','method','location'])
sim_config_data=sim_config_df.to_xml()

with open('config.xml','w') as file:
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
