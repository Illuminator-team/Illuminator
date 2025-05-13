from illuminator.engine import Simulation

# initialize simulation according to tutorial1 yaml
CONFIG_FILE = 'tests/data/Tutorial_1.yaml'
simulation = Simulation(CONFIG_FILE)
simulation.set_model_param(model_name='CSVload', parameter='file_path', value='tests/data/load_data.txt')
simulation.set_model_param(model_name='CSV_pv', parameter='file_path', value='tests/data/pv_data_Rotterdam_NL-15min.txt')
simulation.set_model_param(model_name='CSV_wind', parameter='file_path', value='tests/data/winddata_NL.txt')

simulation.set_monitor_param(parameter='file', value='tests/outputs/out_e2e_T1.csv')

# # set multiple models at once
# new_settings = {'Wind1': {'diameter': 5},
#                 'Load2': {'houses': 100}
#                 }
# simulation.edit_models(new_settings)

# run the simulation
simulation.run()

