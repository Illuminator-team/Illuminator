import sys
import os
import pandas as pd
from pymoo.termination.default import DefaultSingleObjectiveTermination
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Optimization_project')))
import numpy as np
from sim_wrapper import eval_sim
import os
from scipy.optimize import minimize
from multiprocessing import Pool, Lock, Manager
import random
random.seed(42)  # For reproducibility
import csv

from cost_fun import *

import numpy as np
import os
import yaml
import time
import math


source_scenario = './examples/Lucas_folder/Thesis_comparison2/NH_scenario1.yaml' # './examples/Tutorial1/Tutorial_1.yaml'# "./examples/h2_system_example/h2_system_4.yaml"
output_path = './examples/Lucas_folder/Thesis_comparison2/temp_out/thesis_comparison2.csv'# './examples/h2_system_example/h2_system_example4.csv'
scenario_temp_path = './examples/Lucas_folder/Thesis_comparison2/temp_scenario'
log_path = './examples/Lucas_folder/Thesis_comparison2/sc_log'

dec_vars = [
    ('Controller1', 'upper_price'),
    ('Controller1', 'lower_price')]

step_size_x1 = 0.02
step_size_x2 = 0.02

n_cores =  os.cpu_count() - 3

xl = np.array([0, 0])
xu = np.array([0.4, 0.16])


x1_vals = np.linspace(xl[0], xu[0], int((xu[0] - xl[0]) / step_size_x1 +1))
x2_vals = np.linspace(xl[1], xu[1], int((xu[1] - xl[1]) / step_size_x2 + 1))
print(x1_vals)
print(x2_vals)

# for  x1 in x1_vals:
#     for x2 in x2_vals:
#         x = np.array([x1, x2])
#         print(f"Evaluating x: {x}")
#         fitness = eval_sim(source_scenario, scenario_temp_path, output_path, dec_vars, x, cost_fun2, n_cores)
#         with open(log_path, mode='a', newline = '') as file:
#             writer = csv.writer(file)
#             writer.writerow([x, fitness])  # Log solution and its fitness

def evaluate_and_log(args):
    x_pair, shared_params = args
    x1, x2 = x_pair
    x = np.array([x1, x2])
    print(f"Evaluating x: {x}")
    pid = os.getpid()

    # Unpack shared config
    source_scenario, scenario_temp_path, output_path, dec_vars, cost_fun = shared_params

    fitness = eval_sim(source_scenario, scenario_temp_path, output_path, dec_vars, x, cost_fun, n_cores=1)
    print(f'DEBUG: fitness for x = {x} is {fitness}')
    log_path = './examples/Lucas_folder/Thesis_comparison2/sc_log'
    os.makedirs(log_path, exist_ok=True)  # Ensure log directory exists
    log_file = f'{log_path}/{pid}.csv'
    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([x1, x2, fitness])


if __name__ == '__main__':
    log_path = './examples/Lucas_folder/Thesis_comparison2/sc_log'
    n_cores = os.cpu_count() - 3
    x1_vals = np.linspace(xl[0], xu[0], int((xu[0] - xl[0]) / step_size_x1) + 1)
    x2_vals = np.linspace(xl[1], xu[1], int((xu[1] - xl[1]) / step_size_x2) + 1)
    grid = [(x1, x2) for x1 in x1_vals for x2 in x2_vals]

    # # Log header
    # with open(log_path, mode='w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(["x1", "x2", "fitness"])

    # Set your actual params here
    source_scenario = './examples/Lucas_folder/Thesis_comparison2/NH_scenario1.yaml' # './examples/Tutorial1/Tutorial_1.yaml'# "./examples/h2_system_example/h2_system_4.yaml"
    output_path = './examples/Lucas_folder/Thesis_comparison2/temp_out/thesis_comparison2.csv'# './examples/h2_system_example/h2_system_example4.csv'
    scenario_temp_path = './examples/Lucas_folder/Thesis_comparison2/temp_scenario'
    cost_fun2 = cost_fun2

    manager = Manager()


    shared_params = (source_scenario, scenario_temp_path, output_path, dec_vars, cost_fun2)

    args_list = [((x1, x2), shared_params) for (x1, x2) in grid]

    with Pool(processes=n_cores) as pool:
        pool.map(evaluate_and_log, args_list)