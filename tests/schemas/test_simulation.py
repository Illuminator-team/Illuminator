"""
Unit tests for the simulation.py of the schemas module.
"""

from illuminator.schemas.simulation import schema
from ruamel.yaml import YAML

SCENARIO_FILE = open('./src/illuminator/schemas/simulation.example.yaml', 'r')


def test_valid_scenario_schema():
    """Test if a YAML file contains a valid definition for a simulation scenario"""

    yaml = YAML(typ='safe')
    data = yaml.load(SCENARIO_FILE)
    
    schema.validate(data) 
    