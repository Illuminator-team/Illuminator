import pandas as pd


sim_config=[['Grid' ,'python','Models.EleDisNetworkSim.simulator:Pandapower'],
            ['Load','python', 'Models.LoadinNetSim.mosaik-model:LoadholdSim'],
            ['Collector','python', 'Models.collector:Collector'],
            ['CSVB','python', 'Models.mosaik_csv:CSV'],
            ['Controller','python', 'Controllers.NetVoltageControllerSim.mosaik-model:controlSim'],]


sim_config_df=pd.DataFrame(sim_config, columns=['model','method','location'])
sim_config_data=sim_config_df.to_xml()

with open('../../Cases/DNcontrolCase/config.xml','w') as file:
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
