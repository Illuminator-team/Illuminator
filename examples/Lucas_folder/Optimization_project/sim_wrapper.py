import pandas as pd
import subprocess
import matplotlib.pyplot as plt
import yaml
import numpy as np
import time
import os
import shutil
import random

def eval_sim(original_scenario: str, output_path: str, dec_vars_map: list, x: np.ndarray, cost_fun, n_cores: int):
    x_floored = x.astype(int)
    output_path = unique_output_path(output_path, x_floored, n_cores)
    scenario = unique_scenario_path(original_scenario, x_floored, n_cores)
    shutil.copy(original_scenario ,scenario)
    update_scenario(scenario, dec_vars_map, x, output_path)
    print(f"DEBUG:\nthis is scenario in eval_sim: {scenario}\n this is x: {x}")
    command = ['illuminator', 'scenario', 'run', scenario]
    process = subprocess.Popen(command)
    print(f"DEBUG: A NEW PROCESS STARTED FOR SCENARIO {scenario}")
    # df = pd.read_csv(output_path)
    df = read_csv_out(process, output_path)
    # result = cost_fun(df)
    result = cost_fun(df, x)
    print(f"DEBUG: CSV read with result = {result}")
    return result
        
def update_scenario(scenario, dec_vars_map, x, output_path):
    print(f"DEBUG: THIS IS OUTPUT FILE FOR X={x}: {output_path}")
    with open(scenario, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    for model in data['models']:
        for i, (model_name, param) in enumerate(dec_vars_map):
            if model['name'] == model_name:
                model["parameters"][param] = float(x[i])
    data['monitor']['file'] = output_path
    with open(scenario, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)

def read_csv_out(process, output_path):
    # while True:
    #     if process.poll() is not None:
    #         try:
    #             time.sleep(0.2)
    #             df = pd.read_csv(output_path)
    #             return df
    #         except pd.errors.EmptyDataError:
    #             print("Output CSV not available yet")
    #             time.sleep(2)
    """Wait until CSV exists and is stable, then read it."""
    print("DEBUG: NOW IN READ csv FUNCTION")
    stable_wait = 3
    while True:
        print(f"DEBUG: Trying to read {output_path}")
        if os.path.exists(output_path):
            last_size = os.path.getsize(output_path)
            time.sleep(stable_wait)
            new_size = os.path.getsize(output_path)

            if last_size == new_size:
                print("CSV is stable, reading...")
                time.sleep(2)
                df = pd.read_csv(output_path)
                return df
            else:
                print("CSV still growing, waiting...")
        else:
            print("CSV not available yet, waiting...")
            time.sleep(1)
        


    # while True:
    #     if process.wait() == 0 and os.path.exists(output_path):
    #         try:
    #             df = pd.read_csv(output_path)
    #             return df
    #         except pd.errors.EmptyDataError:s
    #             print("Output CSV not available yet")
    #             time.sleep(2)
     
def unique_output_path(original_path, x, n_cores):
    if original_path.endswith(".csv"):
        splitted_path = original_path.split('/')
        file_name = splitted_path[-1].removesuffix('.csv')
        temp_out_dir = '/'.join(splitted_path[:-1])
        # unique_path = f"./examples/Lucas_folder/Optimization_project/temp_out/{file_name}_{'_'.join(map(str, x))}.csv"
        # unique_path = f"./examples/Lucas_folder/Illuminator_presentation/temp_out/{file_name}_{'_'.join(map(str, x))}.csv"
        unique_path = f"./examples/Lucas_folder/Illuminator_presentation/temp_out/{file_name}_{random.randint(0, 1e6)}.csv"

    else:
        raise ValueError("Provided output file is not a csv file")
    
    # remove files that are outdated (2 generation back)
    file_paths_in_dir = [os.path.join(temp_out_dir, f) for f in os.listdir(temp_out_dir)]
    n_files = len(file_paths_in_dir)

    # if n_files > 2 * n_cores:
    #     file_paths_in_dir.sort(key=lambda x: os.path.getmtime(x))
    #     for f in file_paths_in_dir[:n_files - n_cores]:
    #         os.remove(f)

    return unique_path

def unique_scenario_path(scenario, x, n_cores):
    if scenario.endswith('.yaml'):
        splitted_path = scenario.split('/')
        file_name = splitted_path[-1].removesuffix('.yaml')
        temp_scenario_dir = '/'.join(splitted_path[:-1])
        # unique_scenario = f"./examples/Lucas_folder/Optimization_project/temp_scenario/{file_name}_{'_'.join(map(str, x))}.yaml"
        # unique_scenario = f"./examples/Lucas_folder/Illuminator_presentation/temp_scenario/{file_name}_{'_'.join(map(str, x))}.yaml"
        unique_scenario = f"./examples/Lucas_folder/Illuminator_presentation/temp_scenario/{file_name}_{random.randint(0, 1e6)}.yaml"
    else:
        raise ValueError("Provided scenario file is not a yaml file")
    
    return unique_scenario
    

