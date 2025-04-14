from os import chdir, getcwd
from illuminator.engine import Simulation
cwd = getcwd()

chdir('Illuminator/examples/Tutorial3')  # working directory (path to the folder containing the tutorial files)

# initialize simulation according to tutorial1 yaml
CONFIG_FILE = 'Tutorial_3.yaml'
simulation = Simulation(CONFIG_FILE)

# write the output to a file
# OUT_FILE = 'out_Tutorial3.csv'
# simulation.set_model_param(model_name='monitor', parameter='file', value=OUT_FILE)

# set multiple models at once
new_settings = {'Wind1': {'diameter': 5},
                'Load1': {'houses': 100}
                }
simulation.edit_models(new_settings)

# run the simulation
simulation.run()

chdir(cwd)  # change back to the original working directory

