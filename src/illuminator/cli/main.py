"""
A CLI for running simulations in the Illuminator
By: M. Rom & M. Garcia Alvarez
"""

import mosaik
import importlib.util
import mosaik.util
import argparse
from ruamel.yaml import YAML
from illuminator.schemas.simulation import schema

def validate_config_data(config_file: str) -> dict:
    """Returns the content of an scenerio file writtent in YAML after
    validating its content against the Illuminator's Schema.
    """

    _file = open(config_file, 'r')
    yaml = YAML(typ='safe')
    data = yaml.load(_file)
    return schema.validate(data)


def get_collector_path() -> str:
    """Returns the path to the default collector script."""

    # find the module specification for the collector module
    specifiction = importlib.util.find_spec('illuminator.models.collector')
    if specifiction is None or specifiction.origin is None:
        raise ImportError('The collector module was not found.')
    
    collector_path=specifiction.origin
    return collector_path
    # TODO: write a unit test for this

def apply_default_values(config_simulation: dict) -> dict:
    """Applies Illuminator default values to the configuration if they are not
    specified. 
    
    Parameters
    ----------
    config_simulation: dict
        valid Illuminator's simulation configuration
    
    Returns
    -------
    dict
        Illuminator's simulation configuration with default values applied.
    """

    # defaults
    time_resolution = {'time_resolution': 900} # 15 minutes
    results = {'results': './out.csv'}
    # TODO: set other default values

    if 'time_resolution' not in config_simulation:
        config_simulation.update(time_resolution)
    # file to store the results
    if 'results' not in config_simulation:
        config_simulation.update(results)

    #TODO: Write a unit test for this
    return config_simulation


def generate_mosaik_configuration(config_simulation:dict,  collector:str =None) -> dict:
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
    # print(default_collector)

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


def start_simulators(world: mosaik.World, models: list) -> dict:
        """
        Instantiates simulators in the Mosaik world based on the model configurations .
        
        Parameters
        ----------
        world: mosaik.World
            The Mosaik world object.
        models: dict
            A list of models to be started for the Mosaik world as defined by 
            Illuminator's schema.

        Returns
        -------
        dict
            A dictionary of simulator entities (instances) created for the Mosaik world.
        """

        model_entities = {}

        for model in models:
            model_name = model['name']
            model_type = model['type']


            if 'parameters' in model:
                model_parameters = model['parameters']
            else:
                model_parameters = {}

            if model_type == 'CSV':  # the CVS model is a special model used to read data from a CSV file
                
                if 'start' not in model_parameters.keys() or 'datafile' not in model_parameters.keys():
                    raise ValueError("The CSV model requires 'start' and 'datafile' parameters. Check your YAML configuration file.")
                
                simulator = world.start(sim_name=model_name,
                                         sim_start=model_parameters['start'], datafile=model_parameters['datafile'])
            else:
                simulator = world.start(sim_name=model_name,
                                    sim_params={model_type: model_parameters})
            
            entities = simulator.Model()
            model_entities[model_name] = entities

        return model_entities




def main():
    parser = argparse.ArgumentParser(description='Run the simulation with the specified scenario file.')
    parser.add_argument('file_path', nargs='?', default='simple_test.yaml', 
                        help='Path to the scenario file. [Default: config.yaml]')
    args = parser.parse_args()
    file_path = args.file_path

    # load and validate configuration file
    config = validate_config_data(file_path)
    config = apply_default_values(config)
    
    # Define the Mosaik simulation configuration
    sim_config = generate_mosaik_configuration(config)

    # simulation time
    _start_time = config['scenario']['start_time']
    _time_resolution = config['time_resolution']
    # output file with forecast results
    _results_file = config['results']

    # Initialize the Mosaik worlds
    world = mosaik.World(sim_config)
    # TODO: collectors are also customisable simulators, define in the same way as models.
    # A way to define custom collectors should be provided by the Illuminator.
    collector = world.start('Collector', 
                            time_resolution=_time_resolution, 
                            start_date=_start_time,  
                            results_show={'write2csv':True, 'dashboard_show':False, 'Finalresults_show':False,'database':False, 'mqtt':False}, 
                            output_file=_results_file)
    
    monitor = collector.Monitor()

    # Dictionary to keep track of created model entities
    model_entities = start_simulators(world, config['models'])

    # Create the models based on the configuration
    # Each model is assgined to a simulator.
    for model in config['models']:
        # Start the simulator in Mosaik and create a ModelFactory
        model_name = model['name']
        model_type = model['type']
        if 'parameters' in model:
            model_parameters = model['parameters']
        else:
            model_parameters = {}

        if model_type == 'CSV':
            
           # TODO: START THE CSV SIMULATOR
            pass
        else:
            simulator = world.start(sim_name=model_name,
                                sim_params={model_type: model_parameters})
        
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

    # config_yaml = 'examples/simulation.example.yaml'

    # conf = validate_config_data(config_yaml)
    # print(conf)

    # mosaik_conf= generate_mosaik_configuration(conf)
    # print(mosaik_conf)

    main()
