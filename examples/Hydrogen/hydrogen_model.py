import os
from illuminator.models.import_custom_model import import_custom_model
from Hydrogen_production_controller import Hydrogen_production_controller
import_custom_model(Hydrogen_production_controller)


from illuminator.engine import Simulation
# from illuminator_system_visualization import generate_hydrogen_system_diagram
# from visualize_results import visualize_results



# Set CWD to the directory containing the script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# initialize simulation according to tutorial1 yaml
CONFIG_FILE = 'Hydrogen_production.yaml'
OUT_FILE = f"output_{CONFIG_FILE[:-5]}.csv"
# generate_hydrogen_system_diagram(CONFIG_FILE, 'system_diagram.png')

simulation = Simulation(CONFIG_FILE)
simulation.set_monitor_param('file', OUT_FILE)

# run the simulation
simulation.run()

# visualize_results(OUT_FILE)
pass
