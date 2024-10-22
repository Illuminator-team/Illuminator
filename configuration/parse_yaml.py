import yaml

"""
This script reads a yaml file of an illuminator model. It extracts the connection information.
If an IP port is not specified it will default to 5123.
If both IP address and port are known than a line will be prined that can be used in the run.sh file.
The run.sh file is used to start the processes on remote pi's. 
"""

# Open and load the YAML file
with open('modelling-example.yaml', 'r') as _file:
    data = yaml.safe_load(_file)

run_path='./Desktop/illuminatorclient/configuration/runshfile/'
run_model='/home/illuminator/Desktop/Final_illuminator'

for model in data['models']:
    model_type = model.get('type')

    connect = model.get('connect', {})

    if connect:
        connect_ip = connect.get('ip')
        connect_port = connect.get('port')

        if not connect_port:
            connect_port = 5123

        if connect_ip and connect_port:
            print(f"lxterminal -e ssh illuminator@{connect_ip} '{run_path}run{model_type}.sh {connect_ip} {connect_port} {run_model}'&")

