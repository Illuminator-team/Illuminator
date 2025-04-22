import pandas as pd
import subprocess
import matplotlib.pyplot as plt
import yaml
import numpy as np
import time


def eval_sim(scenario: str, output_path: str, dec_vars_map: list, x: np.ndarray, cost_fun):
    update_scenario(scenario, dec_vars_map, x)
    command = ['illuminator', 'scenario', 'run', scenario]
    process = subprocess.Popen(command)
    df = read_csv_out(process, output_path)
    result = cost_fun(df)
    return result
        
def update_scenario(scenario, dec_vars_map, x):
    print(f"DEBUG: THIS IS X: {x}")
    with open(scenario, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    print(f"DEBUG: THIS IS X: {x}")
    for model in data['models']:
        for i, (model_name, param) in enumerate(dec_vars_map):
            print(f"DEBUG: this is i type: {type(i)} and x[i] type: {type(x[i])}")
            if model['name'] == model_name:
                model["parameters"][param] = float(x[i])
    with open(scenario, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)

def read_csv_out(process, output_path):
    while True:
        if process.poll() is not None:
            try:
                df = pd.read_csv(output_path)
                return df
            except pd.errors.EmptyDataError:
                print("Output CSV not available yet")
                time.sleep(2)
     





    

