from illuminator.engine import Simulation
from illuminator.schema.simulation import load_config_file
from mpi4py import MPI
from ruamel.yaml import YAML
from typing import List, Any
import itertools
import os
import csv
import copy

def run_parallel(simlist: List[Simulation], create_scenario_files: bool = False):
    """
    Distributes and runs a list of Simulation objects in parallel using MPI.

    Each simulation in the list is executed on an MPI rank. Optionally, scenario 
    configuration files can be generated for each simulation.

    Parameters
    ----------
    simlist : List[Simulation]
        A list of pre-configured Simulation objects to run. Each simulation should 
        contain exactly one scenario (no multi-parameters). Each simulation
        must have a unique output file defined to prevent overwriting results.

    create_scenario_files : bool, optional
        If True, a YAML file containing the simulation configuration will be written 
        for each simulation. Default is False.

    Notes
    -----
    - Scenario files are named by taking the simulation's `_results_file` path, 
      removing the extension, and appending "_simconfig.yaml".
    """
    
    rank = MPI.COMM_WORLD.Get_rank()        # id of the MPI process executing this function
    comm_size = MPI.COMM_WORLD.Get_size()   # number of MPI processes

    # Distribute simulations among MPI processes
    subset = _get_list_subset(simlist, rank, comm_size)

    for sim in subset:
        # Run the simulation
        sim.run()

        # Write scenario configuration YAML file
        if create_scenario_files:
            scenariofile = os.path.splitext(sim._results_file)[0] # _results_file without extension
            scenariofile.append("_simconfig.yaml")
            yaml = YAML()  
            with open(scenariofile, 'w') as f:
                yaml.dump(sim.config, f)
            print(f"[Rank {rank}] created {scenariofile}")

    return


def run_parallel_file(scenario_file: str):
    rank = MPI.COMM_WORLD.Get_rank()        # id of the MPI process executing this function
    comm_size = MPI.COMM_WORLD.Get_size()   # number of MPI processes

    # Check if yaml has correct the correct format and syntax
    _ = load_config_file(scenario_file)
    
    # Load base configuration and remove parallel items
    base_config, removed_items = _remove_scenario_parallel_items(scenario_file)
    
    # Check which type of combination
    align_parameters = base_config.get("scenario", {}).get("align_parameters")
    if align_parameters is None:
        align_parameters = False
        if rank == 0:
            print("Warning: 'align_parameters' is missing in 'scenario'. Setting it to False.")

    # Get list of parallel-item combinations:
    combinations = _generate_combinations_from_removed_items(removed_items, align_parameters)
    if rank == 0:
        print("Running ", len(combinations), "different scenarios across ", comm_size, " processes." )
        # Write lookup table
        outputdir = os.path.dirname(base_config.get("monitor", {}).get("file"))
        lookuptablefile = os.path.join(outputdir, "scenariotable.csv")
        _write_lookup_table(combinations, str(lookuptablefile))

    # Get the rank's subset of the list
    subset = _get_list_subset(combinations, rank, comm_size)

    # Split the filename and extension
    cf_base, cf_ext = os.path.splitext(scenario_file)

    # For each item in the subset:
    # 1. generate scenario
    # 2. write scenario to file
    # 3. run simulation
    for s in subset:
        scenario = _generate_scenario(base_config, s)
        sim_number = s.get("simulationID")

        # Serialize scenario into yaml file
        scenariofile =  f"{cf_base}_{sim_number}{cf_ext}"
        yaml = YAML()  
        with open(scenariofile, 'w') as f:
            yaml.dump(scenario, f)
        print(f"[Rank {rank}] Wrote scenario {sim_number} to {scenariofile}")

        # Run simulation
        simulation = Simulation(scenariofile)
        simulation.run()


def _remove_scenario_parallel_items(yaml_file_path: str):
    """
    Reads a YAML file, removes multi_parameters sections in models.
    Returns the cleaned YAML data and removed items.

    Args:
        yaml_file_path (str): Path to the YAML file.

    Returns:
        cleaned_data (dict): YAML data without multi_parameters.
        removed_items (list of tuples): List of removed items in format 
            (model_name, 'parameter', key, value)
    """
    # Load YAML
    yaml_parser = YAML()
    with open(yaml_file_path, 'r') as f:
        yaml_data = yaml_parser.load(f)

    removed_items = []

    for model in yaml_data.get('models', []):
        model_name = model.get('name')

        # Remove parameters that are lists or sets
        if 'multi_parameters' in model:
            to_remove = []
            for key, value in model['multi_parameters'].items():
                if isinstance(value, (str)):
                    # For cases "range(1, 10, 1)" -> range() -> list
                    try:
                        model['multi_parameters'][key] = list(eval(model['multi_parameters'][key]))
                    except:
                        return f"Error in evaluating {key}:{value} pair. Example syntax for multi_parameters range: 'param1':'range(1, 10, 2)'"
                to_remove.append(key)
            for key in to_remove:
                removed_items.append((model_name, 'parameter', key, model['multi_parameters'][key]))
            
            # Remove section from model
            del model['multi_parameters']
                
    return yaml_data, removed_items


def _generate_combinations_from_removed_items(removed_items, align = False):
    """
    Generate all possible combinations of values from removed_items,
    with optional alignment.

    This function is meant to be used with the `removed_items` list returned
    by `remove_scenario_parallel_items`, where each removed item represents a
    multi_parameter in the scenaio YAML file.

    - If align=False (default), all combinations are generated using the
      Cartesian product of the value lists.
    - If align=True, only "aligned" combinations are generated, where the
      i-th element of each value list is paired together. All lists must
      have the same length in this case.

    Args:
        removed_items (list of tuples): 
            Each tuple is (model_name, 'parameter', key, list_of_values)
        align (bool, optional): If True, generate only aligned combinations.
            Defaults to False.

    Returns:
        List[dict]: Each dictionary represents one full combination.
                    Keys are 3-tuples: (model_name, 'paramter', key), values are selected item.
                    Each dict also has 'simulationID' counting from 1.
    Raises:
        ValueError: If `align=True` but the value lists are not all the same length.
    """
    keys = []
    value_lists = []
    for model, kind, param_key, values in removed_items:
        keys.append((model, kind, param_key))
        value_lists.append(values)

    if align:
        # Check all lists have the same length
        lengths = [len(v) for v in value_lists]
        if not all(l == lengths[0] for l in lengths):
            raise ValueError("Multi-value model attributes don't have the same length. Did you mean align = False?")
        # Take i-th element from each list
        combinations = zip(*value_lists)
    else:
        # Full cartesian product
        combinations = list(itertools.product(*value_lists))

    result = []
    simnum = 1
    for combo in combinations:
        combo_dict = dict(zip(keys, combo))
        combo_dict['simulationID'] = simnum
        result.append(combo_dict)
        simnum = simnum + 1

    return result


def _get_list_subset(simulation_list: List[Any], rank: int, comm_size: int) -> List[dict]:
    """
    Distributes a list of simulations among MPI processes.

    If there are more simulations than MPI processes, each process gets a subset of the list.
    If there are more MPI processes than simulations, only processes with rank less than the number of simulations get a simulation.

    Args:
        simulation_list (List[Any]): The list of simulations to distribute.
        rank (int): The rank of the MPI process.
        comm_size (int): The total number of MPI processes.

    Returns:
        List[Any]: The subset of the simulation list assigned to the MPI process.
    """
    # If we have more simulations than MPI processes
    if (comm_size <= len(simulation_list)):
        base_size = len(simulation_list) // comm_size
        start = rank * base_size
        end = start + base_size - 1
        # Each MPI process gets a subset of the list 
        subset = simulation_list[start:end+1]
        # Assign leftover elements
        if(rank < len(simulation_list) % comm_size):
            i = -1 - rank
            subset.append(simulation_list[i])
        return subset
    else:
        # if we have more MPI processes than simulations
        if (rank < len(simulation_list)):
            return [simulation_list[rank]]
        else:
            return []


def _generate_scenario(base_config: dict, item_to_add: dict):
    """
    Generates a complete scenario configuration by injecting a single combination of parameters
    into the base configuration.

    It also updates the output file name to include the simulation ID.

    Args:
        base_config (dict): The base YAML configuration (as parsed from the scenario file).
        item_to_add (dict): A dictionary with:
            - 'simulationID' (int): Unique identifier for the simulation.
            - (model_name, 'parameter', key): Tuple keys indicating where to inject the value
              into the corresponding model section.

    Returns:
        dict: A new scenario dictionary with injected parameters and updated monitor file name.
    """
    new_config = copy.deepcopy(base_config)

    # Remove align_parameters from base_config
    if 'align_parameters' in new_config['scenario']:
        new_config['scenario'].pop('align_parameters')

    # Add item_to_add to the correct model
    for key, value in item_to_add.items():
        if key == 'simulationID':
            continue
        model_name, section, param = key

        # Find the correct model
        model_found = False
        for model in new_config['models']:
            if model['name'] == model_name:
                model_found = True
                model.setdefault('parameters', {})[param] = value
                break  # Model found, no need to continue

        if not model_found:
            raise ValueError(f"Model '{model_name}' not found in base_config['models']. combinaion: {item_to_add}")

    # Append simulation number to monitor output file
    simID = item_to_add.get('simulationID')
    if simID is None:
        raise ValueError(f"simulationID is missing in combination: {item_to_add}")
    outputfile = new_config.get("monitor", {}).get("file")
    of_base, of_ext = os.path.splitext(outputfile)
    new_config["monitor"]["file"] = f"{of_base}_{simID}{of_ext}"
        
    return new_config


def _write_lookup_table(simulation_list: List[dict], filepath: str):
    """
    Writes a CSV file mapping each simulation ID to the combination of parameter values used.

    Args:
        simulation_list (List[dict]): List of simulation configurations, each with a 'simulationID' and combination values.
        filepath (str): Path to the output CSV file.
    """
    # Collect all keys from the first dictionary
    all_keys = simulation_list[0].keys()

    # Build column names with 'simulationID' first and then sorted in alphabetical order
    header_keys = ['simulationID'] + sorted(k for k in all_keys if k != 'simulationID')
    header_labels = []
    for key in header_keys:
        if isinstance(key, tuple):
            header_labels.append(".".join(key))
        else:
            header_labels.append(str(key)) # simulationID

    # Write to CSV file
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header_labels)
        for row in simulation_list:
            writer.writerow([row[k] for k in header_keys])