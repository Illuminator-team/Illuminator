from ruamel.yaml import YAML
import sys
import json
from illuminator.schemas.simulation import simulation_schema

# this if a yaml file complies with the modelling schema

_file = open('./src/illuminator/schemas/simulation.example.yaml', 'r')

yaml = YAML(typ='safe')
data = yaml.load(_file)

val = simulation_schema.validate(data)

# json_data = json.dumps(data, indent=4)
# print(json_data)

