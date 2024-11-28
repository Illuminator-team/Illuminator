"""
API for buildiing simulations with Illuminator. It
serves as a wrapper for the Mosaik API.
By: M. Rom & M. Garcia Alvarez
"""

import math
import importlib.util
from mosaik.scenario import Entity as MosaikEntity
from mosaik.scenario import World as MosaikWorld
from datetime import datetime
from illuminator.schema.simulation import load_config_file

current_model = {}

def create_world(sim_config: dict, time_resolution: int) -> MosaikWorld:
    """
    Creates a Mosaik world object based on the simulation configuration.

    Parameters
    ----------
    sim_config: dict
        The simulation configuration for the Mosaik world.
    time_resolution: int
        The time resolution of the simulation in seconds.

    Returns
    -------
    mosaik.World
        The Mosaik world object.
    """

    world = MosaikWorld(sim_config, time_resolution=time_resolution)
    return world


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
    out_file = {'file': './out.csv'}
    # TODO: set other default values

    if 'time_resolution' not in config_simulation['scenario']:
        config_simulation.update(time_resolution)
    # file to store the results
    if 'file' not in config_simulation['monitor']:
        config_simulation.update(out_file)

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


def start_simulators(world: MosaikWorld, models: list) -> dict:
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
            set_current_model(model)


            if 'parameters' in model:
                model_parameters = model['parameters']
            else:
                model_parameters = {}

            if model_type == 'CSV':  # the CVS model is a special model used to read data from a CSV file
                
                if 'start' not in model_parameters.keys() or 'datafile' not in model_parameters.keys():
                    raise ValueError("The CSV model requires 'start' and 'datafile' parameters. Check your YAML configuration file.")
                
                simulator = world.start(sim_name=model_name,
                                         sim_start=model_parameters['start'], datafile=model_parameters['datafile'])
                
                model_factory = getattr(simulator, model_type)
                entity = model_factory.create(num=1)
                
            else:
                simulator = world.start(sim_name=model_name,
                                    # **model_parameters
                                    model_name = model_name,
                                    sim_params= {model_name: model} # This value gets picked up in the init() function
                                    # Some items must be passed here, and some other at create()
                                    )
        
                # TODO: make all parameters in create() **kwargs
                # TODO: model_type must match model name in META for the simulator
                
                # allows instantiating an entity by using the value of 'model_type' dynamically
                model_factory = getattr(simulator, model_type) 
                # Mulple entities entities for the same model are created
                # one at a time. This is by design.
                # TODO: parameters must be passed as **kwargs in create().
                # This should be fixed by adapting models to use the Illumnator's interface

                # TODO:
                # this is a temporary solution to continue developing the CLI

                # TODO: If we wish to use different values here, we must define the parameters used here within the appropriate .yaml file.
                # Right now adder.yaml defines the custom parameters as "param1"
                
        #         entity = model_factory.create(num=1, sim_start='2012-01-01 00:00:00', 
        #                                     panel_data={'Module_area': 1.26, 'NOCT': 44, 'Module_Efficiency': 0.198, 'Irradiance_at_NOCT': 800,
        #   'Power_output_at_STC': 250,'peak_power':600},
        #                                     m_tilt=14, 
        #                                     m_az=180, 
        #                                     cap=500,
        #                                     output_type='power'
        #                                     )
            entity = model_factory.create(num=1, param1="Not in use") 

            model_entities[model_name] = entity
            print(model_entities)
            
        return model_entities


def build_connections(world:MosaikWorld, model_entities: dict[MosaikEntity], connections: list[dict], 
                      models: list[dict]) -> MosaikWorld: # TODO: limit model_config to only models
        """
        Connects the model entities in the Mosaik world based on the connections specified in the YAML configuration file.
        
        Parameters
        ----------
        world: mosaik.World
            The Mosaik world object.
        model_entities: dict
            A dictionary of model entities created for the Mosaik world.
        connections: list
            A list of connections to be established between the model entities.
        models: list
            The models involved in the connections based on the configuration file.

        Returns
        -------
        mosaik.World
            The Mosaik world object with the connections established.
        
        """

        for connection in connections:
            from_model, from_attr =  connection['from'].split('.')
            to_model, to_attr =  connection['to'].split('.')
            # TODO: check if this will work for the cases in which there are not time_shifted connections
            to_model_config = next((m for m in models if m['name'] == to_model))
            time_shifted = connection['time_shifted']
            # Establish connections in the Mosaik world
            try:
                # entities for the same model type are handled separately. Therefore, the entities list of a model only contains a single entity
                if time_shifted:
                    world.connect(model_entities[from_model][0], 
                                model_entities[to_model][0], 
                                (from_attr, to_attr),
                                time_shifted=True,
                                initial_data={from_attr: to_model_config['inputs'][to_attr]})
                                # set the initial value for the connection to equal the initial value of the model
                else:
                    world.connect(model_entities[from_model][0], # entities for the same model type
                            # are handled separately. Therefore, the entities list of a model only contains a single entity
                            model_entities[to_model][0], 
                            (from_attr, to_attr))
            except KeyError as e:
                print(f"Error: {e}. Check the 'connections' in the configuration file for errors.")
                exit(1)

        # TODO: write a unit test for this. Cases: 1) all connections were established, 2) exception raised
        return world


def compute_mosaik_end_time(start_time:str, end_time:str, time_resolution:int = 900) -> int:
    """
    Computes the number to time steps for a Mosaik simulation given the start and end timestamps, and
    a time resolution. Values are approximated to the lowest interger.
    
    Parameters
    ----------
    start_time: str
        Start time as ISO 8601 time stamp. Example: '2012-01-01 00:00:00'.

    end_time: str
        Start time as ISO 8601 time stamp. Example: '2012-01-01 00:00:00'.
    
    time_resolution: number of seconds that correspond to one mosaik time step in this situation. Default is 900 secondd (15 min).

    """

    start = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

    duration_seconds = (end - start).total_seconds()
    steps = math.floor(duration_seconds/time_resolution)

    return steps

# def get_current_model():
#     return current_model

def set_current_model(model):
    global current_model
    try:
        current_model["type"] = model['type']
    except KeyError as e:
        print(f"Warning: Missing 'type' key in model. {e}")
    except Exception as e:
        print(f"Warning: An error occurred while assigning 'type'. {e}")

    try:
        current_model['parameters'] = model['parameters']
    except KeyError as e:
        print(f"Warning: Missing 'parameters' key in model. {e}")
    except Exception as e:
        print(f"Warning: An error occurred while assigning 'parameters'. {e}")

    try:
        current_model['inputs'] = model["inputs"]
    except KeyError as e:
        print(f"Warning: Missing 'inputs' key in model. {e}")
    except Exception as e:
        print(f"Warning: An error occurred while assigning 'inputs'. {e}")

    try:
        current_model['outputs'] = model["outputs"]
    except KeyError as e:
        print(f"Warning: Missing 'outputs' key in model. {e}")
    except Exception as e:
        print(f"Warning: An error occurred while assigning 'outputs'. {e}")
    

def connect_monitor(world: MosaikWorld,  model_entities: dict[MosaikEntity], 
                    monitor:MosaikEntity, monitor_config: dict) -> MosaikWorld:
    """
    Connects model entities to the monitor in the Mosaik world.

    Parameters
    ----------
    world: mosaik.World
        The Mosaik world object.
    model_entities: dict
        A dictionary of model entities created for the Mosaik world.
    monitor: mosaik.Entity
        The monitor entity in the Mosaik world.
    monitor_config: dict
        The configuration for the monitor.

    Returns
    -------
    mosaik.World
        The Mosaik world object with model entities connected to the monitor.
    """

    for item in monitor_config['items']:
            from_model, from_attr =  item.split('.')

            to_attr = from_attr # enforce connecting attributes have the same name
            try:
                model_entity = model_entities[from_model][0]
            except KeyError as e:
                print(f"Error: {e}. Check the 'monitor' section in the configuration file for errors.")
                exit(1)

            # Establish connections in the Mosaik world
            try:
                world.connect(model_entity, 
                              monitor, 
                              (from_attr, to_attr)
                            )
            except Exception as e:
                print(f"Error: {e}. Connection could not be established for {from_model} and the monitor.")
                exit(1)
        
        # TODO: write a unit test for this. Cases: 1) all connections were established, 2) exception raised
    return world


class Simulation:
    """A simplified interface to run simulations with Illuminator."""

    def __init__(self, config_file:str) -> None:
        """Loads and validates the configuration file for the simulation."""
        self.config_file = load_config_file(config_file)


    def run(self):
        """Runs a simulation scenario"""

        config = apply_default_values(self.config_file)
        
        # Define the Mosaik simulation configuration
        sim_config = generate_mosaik_configuration(config)

        # simulation time
        _start_time = config['scenario']['start_time']
        _end_time = config['scenario']['end_time']
        _time_resolution = config['scenario']['time_resolution']
        # output file with forecast results
        _results_file = config['monitor']['file']

        # Initialize the Mosaik worlds
        world = create_world(sim_config, time_resolution=_time_resolution)
        # TODO: collectors are also customisable simulators, define in the same way as models.
        # A way to define custom collectors should be provided by the Illuminator.
        collector = world.start('Collector', 
                                time_resolution=_time_resolution, 
                                start_date=_start_time,  
                                results_show={'write2csv':True, 'dashboard_show':False, 
                                            'Finalresults_show':False,'database':False, 'mqtt':False}, 
                                output_file=_results_file)
        
        # initialize monitor
        monitor = collector.Monitor()

        # Dictionary to keep track of created model entities
        model_entities = start_simulators(world, config['models'])

        # Connect the models based on the connections specified in the configuration
        world = build_connections(world, model_entities, config['connections'], config['models'])

        # Connect monitor
        world = connect_monitor(world, model_entities, monitor, config['monitor'])
        
        # Run the simulation until the specified end time
        mosaik_end_time =  compute_mosaik_end_time(_start_time,
                                                _end_time,
                                                _time_resolution
                                            )

        world.run(until=mosaik_end_time)

    @property
    def config(self)-> dict:
        """Returns the configuration file for the simulation."""
        return self.config_file
    