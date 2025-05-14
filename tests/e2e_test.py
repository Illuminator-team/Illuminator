from illuminator.engine import Simulation

# initialize simulation according to tutorial1 yaml

def tutorial1():
    CONFIG_FILE = 'tests/data/Tutorial_1.yaml'
    simulation = Simulation(CONFIG_FILE)
    simulation.set_monitor_param(parameter='file', value='tests/outputs/out_e2e_T1.csv')

    # run the simulation
    simulation.run()
    return

def tutorial3():
    CONFIG_FILE = 'tests/data/Tutorial_physical_congestion_RES_bat_elec_loadshift.yaml'
    simulation = Simulation(CONFIG_FILE)

    new_settings = {'Wind1': {'p_rated': 10},
                    'Load1': {'houses': 10},
                    'PV1': {'cap': 20000},
                    'Battery1': {'max_p': 40, 'min_p': -40, 'soc_min': 10, 'soc_max': 90},
                    'Grid1':{'connection_capacity' : 15, 'tolerance_limit': 0.67, 'critical_limit': 0.9},
                    'Controller1': {'load_shift_active' : True}
                    }

    simulation.edit_models(new_settings)

    # you can switch between the selected days 2012-02-01 and 2012-07-06 by changing the date in the two lines below for better readibility it is advised to keep the observed time slot at 1 day
    simulation.set_scenario_param('start_time', '2012-02-01 00:00:00')
    simulation.set_scenario_param('end_time', '2012-02-01 23:45:00')

    simulation.set_monitor_param(parameter='file', value='tests/outputs/out_e2e_T3.csv')

    # run the simulation
    simulation.run()

tutorial1()
tutorial3()