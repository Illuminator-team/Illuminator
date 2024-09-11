from ruamel.yaml import YAML
import sys
import json
from modelling_schema import schema

_file = open('./configs/modelling-example.yaml', 'r')

yaml = YAML(typ='safe')
data = yaml.load(_file)

# yaml.dump(data, sys.stdout)

val = schema.validate(data)
print(val)

# json_data = json.dumps(data, indent=4)
# print(json_data)

