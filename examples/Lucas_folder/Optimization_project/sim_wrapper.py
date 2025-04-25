import pandas as pd
import subprocess
import matplotlib.pyplot as plt
import yaml
import numpy as np
import time
import os

def eval_sim(scenario: str, output_path: str, dec_vars_map: list, x: np.ndarray, cost_fun, n_cores: int):
    output_path = unique_output_path(output_path, x, n_cores)
    update_scenario(scenario, dec_vars_map, x, output_path)
    command = ['illuminator', 'scenario', 'run', scenario]
    process = subprocess.Popen(command)
    # os.system(f'illuminator scenario run {scenario}')
    df = pd.read_csv(output_path)
    df = read_csv_out(process, output_path)
    result = cost_fun(df)
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
    while True:
        if process.poll() is not None:
            try:
                time.sleep(0.2)
                df = pd.read_csv(output_path)
                return df
            except pd.errors.EmptyDataError:
                print("Output CSV not available yet")
                time.sleep(2)
     
def unique_output_path(original_path, x, n_cores):
    x_floored = x.astype(int)
    if original_path.endswith(".csv"):
        splitted_path = original_path.split('/')
        file_name = splitted_path[-1].removesuffix('.csv')
        temp_out_dir = '/'.join(splitted_path[:-1])
        unique_path = f"examples/Lucas_folder/Optimization_project/temp_out/{file_name}_{'_'.join(map(str, x_floored))}.csv"
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




    

