"""
Unit tests for the simulation.py of the schemas module.
"""

from illuminator.schema.simulation import load_config_file
from ruamel.yaml import YAML

SCENARIO_FILE = './tests/schema/scenario.example.yaml'

def test_load_config_file():
    """Test if a YAML file contains a valid definition for a simulation scenario"""

    load_config_file(SCENARIO_FILE)


# TOOD: add tests to check if exceptions are raised
    