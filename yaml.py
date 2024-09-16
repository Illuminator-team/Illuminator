from ruamel.yaml import YAML
import sys

_file = open('./illuminator.yaml', 'r')

yaml = YAML(typ='safe')
data = yaml.load(_file)

yaml.dump(data, sys.stdout)
