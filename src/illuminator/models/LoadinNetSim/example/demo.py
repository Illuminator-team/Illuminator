

import mosaik
import mosaik.util
import random

import pandas as pd

SIM_CONFIG={
    'Load':{
        'python':'model_mosaikapi:LoadSim',
    },
    'Collector':{
        'python':'collector:Collector',
    },
}

START='2014-01-01 00:00:00'
END=24*3600
PROFILE_FILE='demo_lv_grid.csv'
# GRID_NAME='demo_lv_grid'
# GRID_FILE='data/%s.json' % GRID_NAME
load_series=pd.Series([2,1],index=["node_1,load_1","node_2,load_2"])
pf_load = pd.read_csv(PROFILE_FILE)

# def main():
#     word=mosaik.World(SIM_CONFIG)
#     create_scenario(word)
#     word.run(until=END)
#
#
# def create_scenario(world):
#     #start simulators
#     load=world.start('Load')
#     collector=world.start('Collector')
#     #model_series, sim_start, profile_file
#     #instantiate models
#     model=load.LoadModel(num= len(pf_data.iloc[0].index[1:].to_list()),sim_start=START, pf_data=pf_load)#model_series, sim_start, profile_file
#     print('good')
#     monitor=collector.Monitor()
#
#     #connect entities
#     world.connect(model, monitor, 'P_out','name')
#
# if __name__ == '__main__':
#     main()

word=mosaik.World(SIM_CONFIG)
load=word.start('Load')
collector=word.start('Collector')
#model_series, sim_start, profile_file
#instantiate models
model= load.LoadModel(,  #model_series, sim_start, profile_file
monitor=collector.Monitor()

#connect entities
word.connect(model, monitor, 'P_out','name')

word.run(until=END)
