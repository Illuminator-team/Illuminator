from illuminator.engine import Simulation
import pandas as pd

CONFIG_FILE = 'Tutorial_2_ide_test.yaml'

simulation_justice_example = Simulation(CONFIG_FILE)

social_parameters = {
    'Company1': {'a': 0.91, 'b': 0.55, 'c': 0.6, 'd': 2.6},
    'Company2': {'a': 0.82, 'b': 0.40, 'c': 0.8, 'd': 2.8},
    'Company3': {'a': 0.85, 'b': 0.16, 'c': 0.2, 'd': 0.35}
}
simulation_justice_example.set_model_param('JusticeAgent1', 'social_parameters', social_parameters)

simulation_justice_example.run()