import yaml
from datetime import datetime
import os

class YamlInterpreter:
    def __init__(self, file_path):
        self.file_path = file_path
        self.yaml_data = self.load_yaml(self.file_path)
        
        self.load_scenario()     # Load scenario settings
        self.load_simulators()   # Load simulators and models
        self.load_connections()  # Load connections
        self.load_monitors()     # Load monitors
        
    def load_scenario(self):
        self.scenario = self.yaml_data.get('scenario', 'DefaultScenario')
        self.start_time = self.yaml_data.get('start_time', '2012-01-01 00:00:00')
        self.end_time = self.yaml_data.get('end_time', 1440)

        # Convert start_time to datetime if necessary
        if isinstance(self.start_time, str):
            self.start_time = datetime.fromisoformat(self.start_time)
                
    def load_simulators(self):
        available_models = self.get_model_files()
        self.simulators = {}  # Key: simulator name, value: simulator data

        for sim_conf in self.yaml_data.get('simulators', []):
            model_type = sim_conf['model_type']
            step_size = sim_conf.get('step_size', 1)  # Default step size if not specified
            model_path = available_models.get(model_type.lower(), None)

            for model_conf in sim_conf.get('models', []):
                model_name = model_conf['name']

                # Collect inputs, outputs, parameters, states, triggers
                inputs = model_conf.get('Inputs') or {}
                outputs = model_conf.get('Outputs') or {}
                parameters = model_conf.get('Parameters') or {}
                states = model_conf.get('States') or {}
                triggers = model_conf.get('Triggers') or {}

                # Create a model data dictionary
                model_data = {
                    'model_type': model_type,
                    'inputs': inputs,
                    'outputs': outputs,
                    'parameters': parameters,
                    'states': states,
                    'triggers': triggers,
                    'model_path': model_path,
                    'step_size': step_size,
                    'start_time': self.start_time,
                }
                meta = self.generate_meta(model_data)
                model_data['meta'] = meta

                self.simulators[model_name] = model_data

    def generate_meta(self, model_data):
        inputs = set(model_data['inputs'].keys())
        outputs = set(model_data['outputs'].keys())
        parameters = set(model_data['parameters'].keys())
        states = set(model_data['states'].keys())
        triggers = set(model_data['triggers'].keys())

        models_meta = {
            "Model": {
                'public': True,
                'params': list(parameters | states),
                'attrs': list(inputs | outputs | states | triggers),
                'any_inputs': False,
                'trigger': list(triggers),
            }
        }

        meta = {
            'api_version': '3.0',
            'type': 'hybrid',
            'models': models_meta,
        }
        return meta
            
    def load_connections(self):
        self.connections = []
        for conn_conf in self.yaml_data.get('connections', []):
            from_str = conn_conf['from']
            to_str = conn_conf['to']

            # from: source_model.attribute
            # to: dest_model.attribute
            from_model_attr = from_str.split('.')
            to_model_attr = to_str.split('.')
            if len(from_model_attr) != 2 or len(to_model_attr) != 2:
                print(f"Invalid connection format: {conn_conf}")
                continue

            from_model, from_attr = from_model_attr
            to_model, to_attr = to_model_attr

            connection = {
                'from_model': from_model,
                'from_attr': from_attr,
                'to_model': to_model,
                'to_attr': to_attr,
            }

            self.connections.append(connection)
            
    def load_monitors(self):
        self.monitors = []
        for monitor_str in self.yaml_data.get('monitor', []):
            # monitor_str is in the format 'ModelName.Attribute'
            model_attr = monitor_str.split('.')
            if len(model_attr) != 2:
                print(f"Invalid monitor format: {monitor_str}")
                continue

            model_name, attr_name = model_attr
            monitor = {
                'model_name': model_name,
                'attribute': attr_name,
            }
            self.monitors.append(monitor)
            
    @staticmethod
    def get_model_files(models_folder='Models'):
        """
        Get a dictionary of available model names and their corresponding file paths.
        """
        model_files = {}
        # Ensure the Models folder exists
        if not os.path.isdir(models_folder):
            print(f"The folder '{models_folder}' does not exist.")
            return model_files

        # List all files in the Models folder
        for filename in os.listdir(models_folder):
            # Check if the file matches the pattern *_model.py
            if filename.endswith('_model.py'):
                # Extract the model_name from the filename
                model_name = filename[:-len('_model.py')]
                # Get the full file path
                file_path = os.path.join(models_folder, filename)
                # Add the model_name and file_path to the dictionary
                model_files[model_name] = file_path

        return model_files

    @staticmethod
    def load_yaml(file_path):
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        return data

if __name__ == "__main__":
    interpreter = YamlInterpreter('config.yaml')
    print(interpreter.scenario)
    print(interpreter.start_time)
    print(interpreter.end_time)
    print(interpreter.simulators)
    print(interpreter.connections)
    print(interpreter.monitors)
    