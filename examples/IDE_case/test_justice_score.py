from illuminator.engine import Simulation
import pandas as pd

CONFIG_FILE = 'Tutorial_2_ide_test.yaml'

simulation_justice_example = Simulation(CONFIG_FILE)

simulation_justice_example.run()