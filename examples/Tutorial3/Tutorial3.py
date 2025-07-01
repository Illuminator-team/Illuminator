from illuminator.engine import Simulation

# initialize simulation according to tutorial1 yaml
CONFIG_FILE = 'examples/Tutorial3/Tutorial_physical_congestion_RES_bat_elec_loadshift.yaml'
simulation = Simulation(CONFIG_FILE)

simulation.set_model_param(model_name='CSVload', parameter='file_path', value='examples/Tutorial3/data/load_data.txt')
simulation.set_model_param(model_name='CSVloadEV', parameter='file_path', value='examples/Tutorial3/data/10_EVs_2012_synthetic.csv')
simulation.set_model_param(model_name='CSVloadHP', parameter='file_path', value='examples/Tutorial3/data/hp_profiles_10h_kW.csv')
simulation.set_model_param(model_name='CSV_pv', parameter='file_path', value='examples/Tutorial3/data/pv_data_Rotterdam_NL-15min.txt')
simulation.set_model_param(model_name='CSV_wind', parameter='file_path', value='examples/Tutorial3/data/winddata_NL.txt')



# write the output to a file
OUT_FILE = 'examples/Tutorial3/out_Tutorial3.csv'
simulation.set_monitor_param('file', value=OUT_FILE)

# run the simulation
simulation.run()

