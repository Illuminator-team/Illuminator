from illuminator.engine import Simulation

# initialize simulation according to tutorial1 yaml
CONFIG_FILE = 'tests/data/Tutorial_1.yaml'
simulation = Simulation(CONFIG_FILE)
simulation.set_model_param(model_name='CSV_pv', parameter='file_path', value='examples/Tutorial1/pv_data_Rotterdam_NL-15min.txt')
simulation.set_model_param(model_name='CSV_wind', parameter='file_path', value='examples/Tutorial1/winddata_NL.txt')

csv_files = ['examples/Tutorial1/load_data.txt', 'examples/Tutorial1/load_data_2.txt']
simulation.set_model_param(model_name='CSVload', parameter='file_path', value=csv_files)



# run the simulation
simulation.run()