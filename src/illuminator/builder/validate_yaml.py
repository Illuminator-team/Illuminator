from ruamel.yaml import YAML
import sys
import json
from illuminator.builder.scenario_schema import schema

# this if a yaml file complies with the modelling schema

_file = open('./configs/modelling-example.yaml', 'r')

yaml = YAML(typ='safe')
data = yaml.load(_file)

val = schema.validate(data)

json_data = json.dumps(data, indent=4)
print(json_data)

