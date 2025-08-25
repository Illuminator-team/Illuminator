from illuminator.engine import Simulation

# initialize simulation according to tutorial1 yaml
CONFIG_FILE = 'examples/Tutorial1/Tutorial_1.yaml'
simulation = Simulation(CONFIG_FILE)


### ADDING A NEW MODEL TO THE SIMULATION ###
new_model = {
    'name': 'Load3',
    'type': 'Load',
    'parameters': {'houses': 50, 'output_type': 'power'},
    'inputs': {'load': 0},
    'outputs': {'load_dem': 0},
    'states': {}
    }

simulation.add_model(new_model)
simulation.add_connection(connection={'from': 'CSVload.load', 'to': 'Load3.load', 'time_shifted': False})
simulation.add_connection(connection={'from': 'Load3.load_dem', 'to': 'Controller1.load_dem'})
simulation.remove_connection(connection={'from': 'Load1.load_dem', 'to': 'Controller1.load_dem'})
simulation.remove_model(model_name='Load1')



### SETTING PARAMETERS AND STATES FOR MODELS ###
simulation.set_model_param(model_name='CSVload', parameter='file_path', value='examples/Tutorial1/load_data.txt')
simulation.set_model_param(model_name='CSV_pv', parameter='file_path', value='examples/Tutorial1/pv_data_Rotterdam_NL-15min.txt')
simulation.set_model_param(model_name='CSV_wind', parameter='file_path', value='examples/Tutorial1/winddata_NL.txt')

# set capacity of PV1 to 2400 W
simulation.set_model_param(model_name='PV1', parameter='cap', value=2400)

simulation.set_model_state(model_name='Battery1', state='soc', value=50)

# set multiple parameters at once
new_params = {'max_p': 0.9, 'min_p': -0.9}
simulation.set_model_parameters(model_name='Battery1', params=new_params)

# set multiple models at once
new_settings = {'Wind1': {'diameter': 5},
                'Load2': {'houses': 100}
                }
simulation.edit_models(new_settings)

# run the simulation
simulation.run()

