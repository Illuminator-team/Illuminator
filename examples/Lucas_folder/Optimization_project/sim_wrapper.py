import pandas as pd
import subprocess
import matplotlib.pyplot as plt
import yaml
import numpy as np
import time
import os
import shutil
import secrets
from pathlib import Path
from datetime import datetime
import math

def count_calls(func):
    def wrapper(*args, **kwargs):
        wrapper.call_count += 1
        return func(*args, **kwargs)
    wrapper.call_count = 0
    return wrapper

@count_calls
def eval_sim(original_scenario: str, scenario_temp_path: str, output_path: str, dec_vars_map: list, x: np.ndarray, cost_fun, n_cores: int):
    x_floored = x.astype(int)
    output_path = unique_output_path(output_path, x_floored, n_cores)
    scenario = unique_scenario_path(original_scenario, scenario_temp_path, x_floored, n_cores)
    shutil.copy(original_scenario, scenario)
    update_scenario(scenario, dec_vars_map, x, output_path)
    # print(f"DEBUG:\nthis is scenario in eval_sim: {scenario}\n this is x: {x}")
    command = ['illuminator', 'scenario', 'run', scenario]
    process = subprocess.Popen(command)
    # print(f"DEBUG: A NEW PROCESS STARTED FOR SCENARIO {scenario}")
    # print("Function called so many times: ", eval_sim.call_count)
    df = read_csv_out(output_path)
    # result = cost_fun(df)
    result = cost_fun(df, x)
    # print(f"DEBUG: CSV read with result = {result}")
    return result

def update_scenario(scenario, dec_vars_map, x, output_path):
    # print(f"DEBUG: THIS IS OUTPUT FILE FOR X={x}: {output_path}")
    with open(scenario, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    for model in data['models']:
        for i, (model_name, param) in enumerate(dec_vars_map):
            if model['name'] == model_name:
                model["parameters"][param] = float(x[i])
    data['monitor']['file'] = output_path
    with open(scenario, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)

def read_csv_out(output_path):
    """Wait until CSV exists and is stable, then read it."""
    # print("DEBUG: NOW IN READ csv FUNCTION")
    stable_wait = 2
    while True:
        # print(f"DEBUG: Trying to read {output_path}")
        if os.path.exists(output_path):
            last_size = os.path.getsize(output_path)
            time.sleep(stable_wait)
            new_size = os.path.getsize(output_path)

            if last_size == new_size:
                # print("CSV is stable, reading...")
                # time.sleep(2)
                df = pd.read_csv(output_path)
                return df
            # else:
                # print("CSV still growing, waiting...")
        else:
            # print("CSV not available yet, waiting...")
            time.sleep(1)
        
def unique_output_path(original_path, x, n_cores):
    if original_path.endswith(".csv"):
        original_path = Path(original_path)
        file_name = original_path.stem
        temp_out_dir = original_path.parent
        random_suffix = secrets.token_hex(6)
        
        while True:
            timestamp = datetime.now().strftime("%H%M%S%f")
            unique_path = temp_out_dir / f"{file_name}_{timestamp}_{random_suffix}_{'_'.join(map(str, x))}.csv"
            if not unique_path.exists():
                # remove_obsolete_files(temp_out_dir, n_cores)
                return str(unique_path)
        # unique_path = f"./examples/Lucas_folder/Optimization_project/temp_out/{file_name}_{'_'.join(map(str, x))}.csv"
        # unique_path = f"./examples/Lucas_folder/Illuminator_presentation/temp_out/{file_name}_{'_'.join(map(str, x))}.csv"
        # unique_path = f"./examples/Lucas_folder/Illuminator_presentation/temp_out/{file_name}_{random.randint(0, 1e6)}.csv"

    else:
        raise ValueError("Provided output file is not a csv file")
    
 


def unique_scenario_path(scenario, scenario_temp_path, x, n_cores):
    if scenario.endswith('.yaml'):
        scenario = Path(scenario)
        scenario_temp_path = Path(scenario_temp_path)
        file_name = scenario.stem
        # remove_obsolete_files(scenario_temp_path, n_cores)
        random_suffix = secrets.token_hex(6)
        while True:
            timestamp = datetime.now().strftime("%H%M%S%f")
            unique_path = scenario_temp_path / f"{file_name}_{timestamp}_{random_suffix}_{'_'.join(map(str, x))}.yaml"
            if not unique_path.exists():
                
                return str(unique_path)
        
        # unique_scenario = f"./examples/Lucas_folder/Illuminator_presentation/temp_scenario/{file_name}_{'_'.join(map(str, x))}.yaml"
        # unique_scenario = f"./examples/Lucas_folder/Illuminator_presentation/temp_scenario/{file_name}_{random.randint(0, 1e6)}.yaml"
    else:
        raise ValueError("Provided scenario file is not a yaml file")
    
    
def remove_obsolete_files(dir, n_cores):
   # remove files that are outdated (2 generation back)
    file_paths_in_dir = [os.path.join(dir, f) for f in os.listdir(dir)]
    n_files = len(file_paths_in_dir)

    if n_files > 2 * n_cores:
        file_paths_in_dir.sort(key=lambda x: os.path.getmtime(x))
        print(file_paths_in_dir)
        for f in file_paths_in_dir[n_cores:]:
            os.remove(f)
