import pandas as pd
import subprocess
import matplotlib.pyplot as plt
import yaml
import numpy as np
import time

def eval_sim(scenario: str, output_path: str, dec_vars_map: list, x: np.ndarray):
    update_scenario(scenario, dec_vars_map, x)
    command = ['illuminator', 'scenario', 'run', scenario]
    process = subprocess.Popen(command)
    df = read_csv_out(process, output_path)
    return df
        
def update_scenario(scenario, dec_vars_map, x):
    with open(scenario, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    for model in data['models']:
        for i, (model_name, param) in enumerate(dec_vars_map):
            if model['name'] == model_name:
                model["parameters"][param] = x[i]
    with open(scenario, 'w') as file:
        yaml.dump(data, file)

def read_csv_out(process, output_path):
    while True:
        if process.poll() is not None:
            try:
                df = pd.read_csv(output_path)
                return df
            except pd.errors.EmptyDataError:
                print("Output CSV not available yet")
                time.sleep(2)
                





    

