import yaml
import os

# Constants
DEFAULT_PORT = 5123
RUN_PATH = './Desktop/illuminatorclient/configuration/runshfile/'
RUN_MODEL = '/home/illuminator/Desktop/Final_illuminator'

def load_yaml(file_path):
    """Loads a YAML file and returns its content."""
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except yaml.YAMLError as exc:
        print(f"Error while parsing YAML: {exc}")
        return None

def build_run_command(model_type, connect_ip, connect_port):
    """Builds the SSH run command for a given model."""
    return f"lxterminal -e ssh illuminator@{connect_ip} '{RUN_PATH}run{model_type}.sh {connect_ip} {connect_port} {RUN_MODEL}'&"

def process_models(data):
    """Processes each model in the YAML data."""
    if 'models' not in data:
        print("Error: No 'models' key found in the YAML data.")
        return

    for model in data['models']:
        model_type = model.get('type', 'unknown')

        # Extract connection details
        connect = model.get('connect', {})
        connect_ip = connect.get('ip')
        connect_port = connect.get('port', DEFAULT_PORT)

        # Ensure both IP and port are available
        if connect_ip:
            run_command = build_run_command(model_type, connect_ip, connect_port)
            print(run_command)

def main():
    yaml_file = 'modelling-example.yaml'
    data = load_yaml(yaml_file)
    
    if data:
        process_models(data)

if __name__ == "__main__":
    main()

