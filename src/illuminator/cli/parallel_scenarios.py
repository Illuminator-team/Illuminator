from ruamel.yaml import YAML
from collections.abc import Iterable
import itertools

def remove_scenario_parallel_items(yaml_file_path):
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


def generate_combinations_from_removed_items(removed_items):
    """
    Generate all combinations of values from removed_items returned by 
    remove_scenario_parallel_items.

    Args:
        removed_items (list of tuples): 
            Each tuple is (model_name, 'parameter' or 'state', key, list_of_values)

    Returns:
        List[dict]: List of dictionaries representing one full combination each.
                    Keys are 3-tuples: (model_name, type, key), values are selected item.
    """
    keys = []
    value_lists = []
    for model, kind, param_key, values in removed_items:
        keys.append((model, kind, param_key))
        value_lists.append(values)
    
    combinations = list(itertools.product(*value_lists))

    result = []
    for combo in combinations:
        result.append(dict(zip(keys, combo)))

    return result