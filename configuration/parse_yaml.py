import yaml

# Open and load the YAML file
with open('modelling-example.yaml', 'r') as _file:
    data = yaml.safe_load(_file)

run_path='./Desktop/illuminatorclient/configuration/runshfile/'
run_model='/home/illuminator/Desktop/Final_illuminator'

for model in data['models']:
    model_type = model.get('type')

    method = model.get('method', {})
    connect_ip = method.get('connect_ip')
    connect_port = method.get('connect_port')

    if connect_ip and connect_port:
        print(f"lxterminal -e ssh illuminator@{connect_ip} '{run_path}run{model_type}.sh {connect_ip} {connect_port} {run_model}'&")

