import mosaik
from mosaik.util import connect_many_to_one
# Doing this causes issues: an example is that it tries to import the incorrect numpy classes
# from Models.EleDisNetworkSim.network import * 
from Models.EleDisNetworkSim.network import create_cigre_lv_resident
import pandas as pd
from configuration.buildmodelset import *

# ERROR 1:
# Incorrect format at position 1172 within the given csv
# ERROR 2:
# Could not import module controller
# !!! Error update
# When ran with environment given by alex, it runs until it receives the following error:
# mosaik.exceptions.SimulationError:
# "Loop ['Controller-0', 'Grid-0'] reached maximal iteration count of 100. Adjust `max_loop_iterations` in the scenario if needed"



outputfile='Result/DNcontrolCase/results.csv'
sim_config_file="Cases/DNcontrolCase/"
sim_config_ddf=pd.read_xml(sim_config_file+'config.xml')
sim_config={row[1]:{row[2]:row[3]}for row in sim_config_ddf.values}

START = '2022-01-01 00:00:00'
END = 1 * 24 * 3600  # half day
PROFILE_FILE = 'Scenarios/results1month_update.csv'
GRID_NAME = 'cigre_lv_resident'
LOAD_DATA = {'start': '2022-01-01 00:00:00', 'resolution': 15, 'unit': 'W'}  # unit of resolution is minute!
net=create_cigre_lv_resident()
upvollimit = 1.05
downvollimit = 0.95
uproom_p = [-0.01] * 20
downroom_p = [0.01] * 20
uproom_q = [-0.00000000000000000001] * 20
downroom_q = [0.000000000000000000001] * 20

room = {
    'upvollimit': upvollimit,
    'downvollimit': downvollimit,
    'uproom_p': uproom_p,
    'downroom_p': downroom_p,
    'uproom_q': uproom_q,
    'downroom_q': downroom_q
}
world = mosaik.World(sim_config)

# Initialize the simulators
gridsim = world.start('Grid', step_size=None)
loadsim = world.start('Load')

# Instantiate model entities

grid = gridsim.Grid(gridfile=GRID_NAME).children

loads = loadsim.Loadset(sim_start=START,
                        data_info=LOAD_DATA,
                        profile_file=PROFILE_FILE).children

# connect entities
# get the nodes and lines of the grid
grid_nodes_gen = [element for element in grid if 'ext_gen' in element.eid]
grid_nodes = [e for e in grid if e.type in 'Bus']
grid_lines = [e for e in grid if e.type in 'Line']
grid_loads = [e for e in grid if e.type in 'Load']

# connect loads to grid
load_data = world.get_data(loads, 'load_id')
load_loc = {b.eid.split('-')[1]: b for b in grid_loads}
for load in loads:
    load_id = load_data[load]['load_id']
    world.connect(load, load_loc[load_id], ('P_out', 'p_mw'))
collector = world.start('Collector', start_date=START,results_show=RESULTS_SHOW_TYPE,output_file=outputfile)
monitor = collector.Monitor()



controller=world.start('Controller')
ctrl = controller.Ctrl(net=net, room=room)

connect_many_to_one(world,grid_nodes,ctrl,'p_mw', 'q_mvar','vm_pu')
# load_data_new = world.get_data([ctrl])
# print(load_data_new)
for load in loads:
    load_id = load_data[load]['load_id']
    load_index=net.load.loc[net.load['name'] == load_id].index[0]
    world.connect(ctrl, load_loc[load_id], (f'p_m_update{load_index}', 'p_mw'),weak=True)

connect_many_to_one(world, grid_nodes, monitor, 'p_mw', 'vm_pu')

world.run(until=END, print_progress=True)