from PSO_alg import run_pso
from cost_fun import *
import numpy as np

## Specify scenario and output path
scenario = "./examples/h2_system_example/h2_system_4"
output_path = '/.examples/h2_system_example/h2_system_example4.csv'

## Define the decision variables here (model, paramter)
dec_vars = [
    ('H2Buffer', 'h2_capacity_tot'),
    ('H2Buffer', 'h2_soc_min')
]
n_var = len(dec_vars)

## Determine which cost function from cost_fun.py to use
cost_fun = cost_fun1

## set lower and upper bounds for decision variables
xl = np.array([0, 0])
xu = np.array([100000, 99])


## Run PSO:
pso_result = run_pso(scenario=scenario,
                    output_path=output_path,
                    dec_vars_map=dec_vars,
                    n_var=n_var,
                    cost_fun=cost_fun,
                    xl=xl,
                    xu=xu)

def result_print(dec_vars, results):
    optimal_params = {}
    for i , (name, param) in dec_vars:
        optimal_params[param] = results.X[i] 
    cost = results.F[0]
    print(f"The optimal parameters are:\n {optimal_params}\n Resulting in a cost of: {cost}")
    return optimal_params, cost

result_print(dec_vars, pso_result)



