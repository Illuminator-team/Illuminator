"""
A CLI for running simulations in the Illuminator
By: M. Rom & M. Garcia Alvarez
"""

import mosaik
import importlib.util
import mosaik.util
import argparse
from ruamel.yaml import YAML
from illuminator.schemas.simulation import simulation_schema

def validate_config_data(config_file: str) -> dict:
    """Returns the content of an scenerio file writtent in YAML after
    validating its content against the Illuminator's Schema.
    """

    _file = open(config_file, 'r')
    yaml = YAML(typ='safe')
    data = yaml.load(_file)
    return simulation_schema.validate(data)


def get_collector_path() -> str:
    """Returns the path to the default collector script."""

    # find the module specification for the collector module
    specifiction = importlib.util.find_spec('illuminator.models.collector')
    if specifiction is None or specifiction.origin is None:
        raise ImportError('The collector module was not found.')
    
    collector_path=specifiction.origin
    return collector_path
    # TODO: write a unit test for this



def generate_mosaik_simulator_configuration(config_simulation:dict,  collector:str =None) -> dict:
    """
    Returns a configuration for the Mosaik simulator based on
    the Illuminators simulation definition.

    Parameters
    ----------
    config_simulation: dict
        valid Illuminator's simulation configuration
    collector: str
        command and path to a custom collector. If None
        the default collector is used. 
        Example: '%(python)s Illuminator_Engine/collector.py %(addr)s'
    
    Returns
    -------
    dict
        Mosaik's world simulator configuration. Example::

            {
                'Collector': {
                    'cmd': '%(python)s Illuminator_Engine/collector.py %(addr)s'
                },
                'Model1': {
                    'python': 'illuminator.models:Model1'
                },
                'Model2': {
                    'python': 'illuminator.models:Model2'
                }
            }
    """

    mosaik_configuration = {}

    default_collector = get_collector_path()

    if collector is None:
        _collector = "%(python)s " +default_collector+ " %(addr)s"
    else:
        _collector = collector

    mosaik_configuration.update({'Collector':
                                 {
                                     'cmd': _collector
                                 }
                                 })

    
    for model in config_simulation['models']:
        model_config = {model['name']:
                        {'python': 'illuminator.models' + ':' + model['type']}
        }
        mosaik_configuration.update(model_config)

    # TODO: write a unit test for this
    return mosaik_configuration


def main():
    parser = argparse.ArgumentParser(description='Run the simulation with the specified scenario file.')
    parser.add_argument('file_path', nargs='?', default='config.yaml', help='Path to the scenario file. [Default: config.yaml]')
    args = parser.parse_args()
    file_path = args.file_path

    # load and validate configuration file
    config = validate_config_data(file_path)
    
    # Define the Mosaik simulation configuration
    sim_config = generate_mosaik_simulator_configuration(config)

    # Initialize the Mosaik world
    world = mosaik.World(sim_config)
    collector = world.start('Collector')
    monitor = collector.Monitor()

    # Dictionary to keep track of created model entities
    model_entities = {}

    # Create the models based on the configuration
    # Each model is assgined to a simulator.
    for model_name, model_data in config.models.items():
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

    config_yaml = 'examples/simulation.example.yaml'

    conf = validate_config_data(config_yaml)
    print(conf)

    mosaik_conf= generate_mosaik_simulator_configuration(conf)
    print(mosaik_conf)

    main()
