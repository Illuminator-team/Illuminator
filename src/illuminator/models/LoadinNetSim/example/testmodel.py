# from loadmodel import LoadModel
# import pandas as pd
# import datetime
# datafile='demo_lv_grid.csv'
# pf_load = pd.read_csv(datafile)
# hm=LoadModel(pf_load,'node_1,load_1')
# timeset='2014-01-01 00:00:00'
# DATA_FORMAT=['YYYY-MM-DD HH:mm:ss']
# timeset=pd.to_datetime(timeset)
# time = timeset + datetime.timedelta(minutes=15)
# ret = hm.get(time)
# print(time, ret)

import model_mosaikapi
import pandas as pd
datafile='demo_lv_grid.csv'
pf_load = pd.read_csv(datafile)
START='2014-01-01 00:00:00'


name='node_1,load_1'
sim=model_mosaikapi.LoadSim()
sim.init('sid')
eneti=sim.create(sim_start=START, pf_data=pf_load,name=name, number=2)
