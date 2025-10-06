from ruamel.yaml import YAML
from collections.abc import Iterable
from typing import List, Dict
import itertools
import os

def remove_scenario_parallel_items(yaml_file_path: str):
    """
    Reads a YAML file, removes parameters or states in models whose values
    are lists or sets, and returns the cleaned YAML data and removed items.

    Args:
        yaml_file_path (str): Path to the YAML file.

    Returns:
        cleaned_data (dict): YAML data with list/set parameters/states removed.
        removed_items (list of tuples): List of removed items in format 
            (model_name, 'parameter'/'state', key, value)
    """
    # Load YAML
    yaml_parser = YAML()
    with open(yaml_file_path, 'r') as f:
        yaml_data = yaml_parser.load(f)

    removed_items = []

    for model in yaml_data.get('models', []):
        model_name = model.get('name')

        # Remove parameters that are lists or sets
        if 'parameters' in model:
            to_remove = []
            for key, value in model['parameters'].items():
                if isinstance(value, (list, set)):
                    to_remove.append(key)
            for key in to_remove:
                removed_items.append((model_name, 'parameter', key, model['parameters'][key]))
                del model['parameters'][key]

        # Remove states that are lists or ranges
        if 'states' in model:
            to_remove = []
            for key, value in model['states'].items():
                if isinstance(value, (list, set)):
                    to_remove.append(key)
            for key in to_remove:
                removed_items.append((model_name, 'state', key, model['states'][key]))
                del model['states'][key]
                
    return yaml_data, removed_items


def generate_combinations_from_removed_items(removed_items, align = False):
    """
    Generate all possible combinations of values from removed_items,
    with optional alignment.

    This function is meant to be used with the `removed_items` list returned
    by `remove_scenario_parallel_items`, where each removed item represents a
    parameter or state whose value was a list in the scenaio YAML file.

    - If align=False (default), all combinations are generated using the
      Cartesian product of the value lists.
    - If align=True, only "aligned" combinations are generated, where the
      i-th element of each value list is paired together. All lists must
      have the same length in this case.

    Args:
        removed_items (list of tuples): 
            Each tuple is (model_name, 'parameter' or 'state', key, list_of_values)
        align (bool, optional): If True, generate only aligned combinations.
            Defaults to False.

    Returns:
        List[dict]: Each dictionary represents one full combination.
                    Keys are 3-tuples: (model_name, type, key), values are selected item.
                    Each dict also has 'sim_number' counting from 1.
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


def get_list_subset(simulation_list: List[dict], rank: int, comm_size: int) -> List[dict]:
    """
    Distributes a list of simulations among MPI processes.

    If there are more simulations than MPI processes, each process gets a subset of the list.
    If there are more MPI processes than simulations, only processes with rank less than the number of simulations get a simulation.

    Args:
        simulation_list (List[dict]): The list of simulations to distribute.
        rank (int): The rank of the MPI process.
        comm_size (int): The total number of MPI processes.

    Returns:
        List[dict]: The subset of the simulation list assigned to the MPI process.
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


def generate_scenario(base_config: dict, item_to_add: dict):
    # Remove align_parameters from base_config
    if 'align_parameters' in base_config['scenario']:
        base_config['scenario'].pop('align_parameters')

    # Add item_to_add to the correct model
    for key, value in item_to_add.items():
        if key == 'simulationID':
            continue
        model_name, section, param_or_state = key

        # Find the correct model
        model_found = False
        for model in base_config['models']:
            if model['name'] == model_name:
                model_found = True
                # Add value under the correct section
                if section == 'parameter':
                    model.setdefault('parameters', {})[param_or_state] = value
                elif section == 'state':
                    model.setdefault('states', {})[param_or_state] = value
                break  # Model found, no need to continue

        if not model_found:
            raise ValueError(f"Model '{model_name}' not found in base_config['models']. combinaion: {item_to_add}")

    # Append simulation number to monitor output file
    simID = item_to_add.get('simulationID')
    if simID is None:
        raise ValueError(f"simulationID is missing in combination: {item_to_add}")
    outputfile = base_config.get("monitor", {}).get("file")
    of_base, of_ext = os.path.splitext(outputfile)
    base_config["monitor"]["file"] = f"{of_base}_{simID}{of_ext}"
        
    return base_config


#def write_lookup_table(simulation_list: List[dict], filepath: str):
    