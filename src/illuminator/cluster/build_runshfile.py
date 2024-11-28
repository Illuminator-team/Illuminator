import yaml
import os
import sys
from illuminator.schema.simulation import load_config_file

# Constants
DEFAULT_PORT = 5123
RUN_PATH = './Desktop/illuminatorclient/configuration/runshfile/'
RUN_MODEL = '/home/illuminator/Desktop/Final_illuminator'
RUN_FILE = 'run.sh'


def build_run_command(model_type, connect_ip, connect_port):
    """Builds the SSH run command for a given model."""
    return f"lxterminal -e ssh illuminator@{connect_ip} '{RUN_PATH}run{model_type}.sh {connect_ip} {connect_port} {RUN_MODEL}'&"

def process_models(data, output_file):
    """Processes each model in the YAML data and writes the commands to a file."""
    if 'models' not in data:
        print("Error: No 'models' key found in the YAML data.")
        return

    with open(output_file, 'w') as file:
        file.write('#! /bin/bash\n')

        for model in data['models']:
            model_type = model.get('type', 'unknown')

            # Extract connection details
            connect = model.get('connect', {})
            connect_ip = connect.get('ip')
            connect_port = connect.get('port', DEFAULT_PORT)

            # Ensure both IP and port are available
            if connect_ip:
                run_command = build_run_command(model_type, connect_ip, connect_port)
                file.write(run_command + '\n')
            else:
                print(f"Warning: Model '{model_type}' has no IP address specified.")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 "+sys.argv[0]+" <path_to_yaml_file>")
        sys.exit(1)

    yaml_file = sys.argv[1]
    output_file = RUN_FILE
    data = load_config_file(yaml_file)
    
    if data:
        process_models(data, output_file)
        print(f"Commands have been written to {output_file}")


if __name__ == "__main__":
    main()

