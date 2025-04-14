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

def create_world(sim_config: dict, time_resolution: int, start_time: str) -> MosaikWorld:
    """
    Creates a Mosaik world object based on the simulation configuration.

    Parameters
    ----------
    sim_config: dict
        The simulation configuration for the Mosaik world.
    time_resolution: int
        The time resolution of the simulation in seconds.
    start_time: str
        The start time of the simulation as an ISO 8601 time stamp.

    Returns
    -------
    mosaik.World
        The Mosaik world object.
    """

    world = MosaikWorld(sim_config, time_resolution=time_resolution)
    world._start_time = start_time
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
    # time_resolution = {'time_resolution': 900} # 15 minutes
    # out_file = {'file': './out.csv'}
    # # TODO: set other default values

    # if 'time_resolution' not in config_simulation['scenario']:
    #     config_simulation.update(time_resolution)
    # # file to store the results
    # if 'file' not in config_simulation['monitor']:
    #     config_simulation.update(out_file)

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
                
                if 'file_path' not in model_parameters.keys():
                    raise ValueError("The CSV model requires 'file_path' parameters. Check your YAML configuration file.")
                
                if 'start' not in model_parameters.keys():
                    model_parameters['start'] = world._start_time
                
                simulator = world.start(sim_name=model_name,
                                         sim_start=model_parameters['start'], datafile=model_parameters['file_path'], sim_params={model_name: model})
                
                model_factory = getattr(simulator, model_type)
                entity = model_factory.create(num=1)
                
            else:
                # simulator = world.start(sim_name=model_name,
                #                     # **model_parameters
                #                     model_name = model_name,
                #                     sim_params= {model_name: model} # This value gets picked up in the init() function
                #                     # Some items must be passed here, and some other at create()
                #                     )
                simulator = world.start(sim_name=model_name, sim_params={model_name: model})
        
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
                entity = model_factory.create(num=1, **model_parameters) 

            model_entities[model_name] = entity
            print(model_entities)
            
        return model_entities


def build_connections(world:MosaikWorld, model_entities: dict[MosaikEntity], connections: list[dict], 
                      models: list[dict]) -> MosaikWorld: # TODO: limit model_config to only models
    """
    Connects the model entities in the Mosaik world based on the connections specified in the 
    YAML configuration file.
    
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
    from_list = []  # for checking physical splits
    for connection in connections:
        from_model, from_attr =  connection['from'].split('.')
        to_model, to_attr =  connection['to'].split('.')

        # check if the model names are unique (assumption 1 model per Simulator is valid)
        if len([m for m in models if m['name'] == from_model]) > 1:
            raise ValueError(f"Multiple models found with name '{from_model}'.")

        # retrieve the first model from the models list whose name matches from_model (assumes 1 model per Simulator).
        from_model_config = next((m for m in models if m['name'] == from_model))
        to_model_config = next((m for m in models if m['name'] == to_model))
        time_shifted = connection['time_shifted']
            
        # check if the connection is a physical split
        if connection['from'] in from_list:
            if from_attr in from_model_config.get('outputs', {}):
                raise ValueError(f"Split detected in physical connection for {connection['from']}.")
            elif from_attr in from_model_config.get('states', {}):
                pass  # it is okay if a non-physical connection (state) goes to multiple destinations
            else:
                raise ValueError(f"Split detected for connection {connection['from']}. "\
                                "I can't check if this is a non-physical connection (states). "\
                                "If so, add the attribute to the states of the model configuration. (e.g., in the .yaml file)")
        from_list.append(connection['from'])

        # Establish connections in the Mosaik world
        try:
            # IMPORTANT: The attribute might not exist in the config, e.g. CSV reader states/outputs are set during their __init__()
            # for this reason, we cannot check if the attribute exists in the config here. This is anyways handled by Mosaik
            # if the model is time_shifted, we DO require the attribute to be in the config as we need to access its initial value.
            # Checking for douplicate attributes is done in the __post_init__()

            if time_shifted:
                if from_attr in from_model_config.get('outputs', {}):
                    message_type = 'output'
                elif from_attr in from_model_config.get('states', {}):
                    message_type = 'state'
                else:
                    raise ValueError(f"Attribute {from_attr} not found in outputs or states of model {from_model}")

                initial_message = {'message_origin': message_type,
                                   'value': to_model_config['inputs'][to_attr]}

                world.connect(model_entities[from_model][0], 
                            model_entities[to_model][0], 
                            (from_attr, to_attr),
                            time_shifted=True,
                            initial_data={from_attr: initial_message})
                            # set the initial value for the connection to equal the initial value of the model
            else:
                world.connect(model_entities[from_model][0], # entities for the same model type
                        # are handled separately. Therefore, the entities list of a model only contains a single entity
                        model_entities[to_model][0], 
                        (from_attr, to_attr))
        except KeyError as e:
            print(f"\nError: {e}. Check the 'connections' in the configuration file for errors.")
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

    try:
        current_model['states'] = model["states"]
    except KeyError as e:
        print(f"Warning: Missing 'states' key in model. {e}")
    except Exception as e:
        print(f"Warning: An error occurred while assigning 'outputs'. {e}")

    try:
        current_model['time_step_size'] = model["time_step_size"]
    except KeyError as e:
        print(f"Warning: Missing 'time_step_size' key in model. {e}")
    except Exception as e:
        print(f"Warning: An error occurred while assigning 'time_step_size'. {e}")
    

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

            to_attr = from_attr # enforce connecting attributes have the same name  # TODO, what if its not?
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
        world = create_world(sim_config, time_resolution=_time_resolution, start_time=_start_time)
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
        world = build_connections(world, model_entities, connections=config['connections'], models=config['models'])

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
    
    def set_scenario_param(self, parameter: str, value)-> None:
        """
        Sets a parameter value in the scenario section of the simulation configuration.

        Parameters
        ----------
        parameter : str
            Name of the parameter to set
        value : any
            New value for the parameter
            
        Returns
        -------
        None
            Updates the configuration in place
            
        Raises
        ------
        KeyError
            If parameter is not found in scenario configuration
        """

        if parameter not in self.config['scenario']:
            available_params = ', '.join(self.config['scenario'].keys())
            raise KeyError(f"Parameter {parameter} not found in scenario. Available parameters: {available_params}")
        
        self.config['scenario'][parameter] = value
        return
    

    def set_model_state(self, model_name: str, state: str, value)-> None:
        """
        Sets a state value for a specific model in the simulation configuration.

        Parameters
        ----------
        model_name : str
            Name of the model to modify
        state : str
            Name of the state to set
        value : any
            New value for the state
            
        Returns
        -------
        None
            Updates the configuration in place
            
        Raises
        ------
        KeyError
            If model_name or state is not found in configuration
        """
        for i, model in enumerate(self.config['models']):
            if model['name'] == model_name:
                if state not in self.config['models'][i]['states']:
                    available_states = ', '.join(model['states'].keys())
                    raise KeyError(f"State '{state}' not found in model '{model_name}'. Available states: {available_states}")
                
                self.config['models'][i]['states'][state] = value
                return
        raise KeyError(f"Model '{model_name}' not found. Available models: {[m['name'] for m in self.config['models']]}")


    def set_model_param(self, model_name: str, parameter: str, value)-> None:
        """
        Sets a parameter value for a specific model in the simulation configuration.

        Parameters
        ----------
        model_name : str
            Name of the model to modify
        parameter : str
            Name of the parameter to set
        value : any
            New value for the parameter
            
        Returns
        -------
        None
            Updates the configuration in place
            
        Raises
        ------
        KeyError
            If model_name or parameter is not found in configuration
        """
        for i, model in enumerate(self.config['models']):
            if model['name'] == model_name:
                if parameter not in self.config['models'][i]['parameters']:
                    available_params = ', '.join(model['parameters'].keys())
                    raise KeyError(f"Parameter '{parameter}' not found in model '{model_name}'. Available parameters: {available_params}")
                
                self.config['models'][i]['parameters'][parameter] = value
                return
        raise KeyError(f"Model '{model_name}' not found. Available models: {[m['name'] for m in self.config['models']]}")


    def set_model_parameters(self, model_name: str, params: dict)-> None:
        """
        Sets multiple parameter values for a specific model in the simulation configuration.

        Parameters
        ----------
        model_name : str
            Name of the model to modify
        params : dict
            Dictionary of parameter names and their new values to set
            
        Returns
        -------
        None
            Updates the configuration in place
            
        Raises
        ------
        KeyError
            If model_name or any parameter is not found in configuration
        """
        for param, value in params.items():
            self.set_model_param(model_name=model_name, parameter=param, value=value)
        return


    def edit_models(self, configuration: dict)-> None:
        """
        Updates multiple parameter values for multiple models in the simulation configuration.

        Parameters
        ----------
        configuration : dict
            Dictionary with model names as keys and parameter dictionaries as values.
            Example: {'model1': {'param1': val1}, 'model2': {'param2': val2}}
            
        Returns
        -------
        None
            Updates the configuration in place
            
        Raises
        ------
        KeyError
            If any model name or parameter is not found in configuration
        
        """
        for model_name, parameters in configuration.items():
            # Check if model exists
            if not any(model['name'] == model_name for model in self.config['models']):
                raise KeyError(f"Model '{model_name}' not found. Available models: {[m['name'] for m in self.config['models']]}")

            self.set_model_parameters(model_name=model_name, params=parameters)
        return
