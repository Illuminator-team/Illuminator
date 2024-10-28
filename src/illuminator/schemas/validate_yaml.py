from ruamel.yaml import YAML
import sys
import json
from illuminator.schemas.simulation import schema

# this if a yaml file complies with the modelling schema
_file = open('simple_test.yaml', 'r')

yaml = YAML(typ='safe')
data = yaml.load(_file)

val = schema.validate(data)
print(val)

json_data = json.dumps(data, indent=4)
print(json_data)

