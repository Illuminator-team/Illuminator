import mosaik
import mosaik.util
import argparse
from .yaml_interpreter import YamlInterpreter

def main():
    parser = argparse.ArgumentParser(description='Run the simulation with the specified scenario file.')
    parser.add_argument('file_path', nargs='?', default='config.yaml', help='Path to the scenario file. [Default: config.yaml]')
    args = parser.parse_args()
    file_path = args.file_path

    # Use the YamlInterpreter to parse the configuration file
    config = YamlInterpreter(file_path)
    
    # Define the Mosaik simulation configuration
    sim_config = {
        'StateSpaceSimulator': {
            'python': 'Illuminator_Engine.state_space_simulator:StateSpaceSimulator',
        },
        'Collector': {
            'cmd': '%(python)s Illuminator_Engine/collector.py %(addr)s',
        },
    }

    # Initialize the Mosaik world
    world = mosaik.World(sim_config)
    collector = world.start('Collector')
    monitor = collector.Monitor()

    # Dictionary to keep track of created model entities
    model_entities = {}

    # Create the models based on the configuration
    for model_name, model_data in config.simulators.items():
        # Start the simulator in Mosaik and create a ModelFactory
        simulator = world.start(sim_name='StateSpaceSimulator', sim_params={model_name: model_data})
        
        # Create the model instances using the model name defined in meta
        entities = simulator.Model()
        model_entities[model_name] = entities

    # Connect the models based on the connections specified in the configuration
    for connection in config.connections:
        from_model = connection['from_model']
        from_attr = connection['from_attr']
        to_model = connection['to_model']
        to_attr = connection['to_attr']
        
        # Establish connections in the Mosaik world
        world.connect(model_entities[from_model], model_entities[to_model], (from_attr, to_attr))

    # Run the simulation until the specified end time
    end_time = config.end_time
    print(f"Running simulation from {config.start_time} to {end_time}.")
    world.run(until=end_time)

if __name__ == '__main__':
    main()
