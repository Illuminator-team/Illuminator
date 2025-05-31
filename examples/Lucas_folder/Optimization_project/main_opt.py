from PSO_alg_p import run_pso_p, run_pso
from GA_alg_p import run_ga, run_ga_p
from LBFGSB_alg import run_LBFGSB
from cost_fun import *
import numpy as np
import os
import yaml
import time
import math

start = time.time()
## Specify scenario and output path

# source_scenario = './examples/Lucas_folder/EV_optimize/EV_scenario1.yaml' # './examples/Tutorial1/Tutorial_1.yaml'# "./examples/h2_system_example/h2_system_4.yaml"
# output_path = './examples/Lucas_folder/Optimization_project/temp_out/EV_single_day_out.csv'# './examples/h2_system_example/h2_system_example4.csv'
# scenario_temp_path = './examples/Lucas_folder/Optimization_project/temp_scenario'
# source_scenario = './examples/Lucas_folder/Illuminator_presentation/presentation_scenario.yaml'
source_scenario = './examples/Tutorial1/Tutorial_1.yaml'

output_path = './examples/Lucas_folder/Illuminator_presentation/temp_out/out_presentation_scenario.csv'# './examples/h2_system_example/h2_system_example4.csv'
scenario_temp_path =  './examples/Lucas_folder/Illuminator_presentation/temp_scenario'


if __name__ == "__main__":
    ## Define the decision variables here (model, paramter)
    dec_vars = [
        # ('H2Buffer', 'h2_capacity_tot'),
        # ('H2Buffer', 'h2_soc_min')
        # ('PV1', 'm_tilt'),
        # ('PV1', 'm_area')
        # ('EV1', 'start_charge'),
        # ('EV2', 'start_charge'),
        # ('EV3', 'start_charge'),
        # ('EV4', 'start_charge'),
        # ('EV5', 'start_charge')
        ('H2Buffer1', 'h2_capacity_tot')
    ]
    n_var = len(dec_vars)

    ## Define the algorithm used (possible entries are PSO, PSO_P, GA, GA_p or LFBGSB)
    alg = "PSO_P" #'LBFGSB' # 

    ## Determine which cost function from cost_fun.py to use
    # cost_fun = cost_fun1
    cost_fun = cost_fun1

    ## set lower and upper bounds for decision variables
    # xl = np.array([0, 0])
    # xu = np.array([100000, 99])
    xl = np.array([0, 0])
    xu = np.array([90, 10])
    # xl = np.array([32, 0, 0, 52, 0])
    # xu = np.array([43, 73, 73, 67, 73])

    # xl = np.array([100])
    # xu = np.array([200])

    ## FOR PSO
    ## Determine termination criterium (FOR PSO & GA)
    termination = ("n_gen", 5)

    ## FOR LBFGSB
    ## Determine initial guess x0 and epsilons
    epsilons = [2] # [1e-5, 1e-5]
    x0 = (xl + xu)/2



    def result_print(dec_vars, params, cost):
        print(f"The optimal parameters are:\n {params}\n Resulting in a cost of: {cost}")
        return params, cost

    # ## Run PSO:
    match alg:
        case 'PSO':
            result = run_pso(scenario=source_scenario,
                        scenario_temp_path=scenario_temp_path,
                        output_path=output_path,
                        dec_vars_map=dec_vars,
                        n_var=n_var,
                        cost_fun=cost_fun,
                        termination=termination,
                        xl=xl,
                        xu=xu)
            params = {}
            for i , (name, param) in enumerate(dec_vars):
                params[param] = result.X[i] 
            cost = result.F[0]
            
        case 'PSO_P':
            result = run_pso_p(scenario=source_scenario,
                        scenario_temp_path=scenario_temp_path,
                        output_path=output_path,
                        dec_vars_map=dec_vars,
                        n_var=n_var,
                        cost_fun=cost_fun,
                        termination=termination,
                        xl=xl,
                        xu=xu)
            params = {}
            for i , (name, param) in enumerate(dec_vars):
                params[param] = result.X[i] 
            cost = result.F[0]
            
        case 'LBFGSB':
            result = run_LBFGSB(scenario=source_scenario,
                                scenario_temp_path=scenario_temp_path,
                                output_path=output_path,
                                dec_vars_map=dec_vars,
                                cost_fun=cost_fun,
                                xl=xl,
                                xu=xu,
                                x0=x0,
                                epsilons=epsilons
                                        )
            params = {}
            for i , (name, param) in enumerate(dec_vars):
                params[param] = result.x[i] 
            cost = result.fun

        case 'GA':
            result = run_ga(scenario=source_scenario,
                        scenario_temp_path=scenario_temp_path,
                        output_path=output_path,
                        dec_vars_map=dec_vars,
                        n_var=n_var,
                        cost_fun=cost_fun,
                        termination=termination,
                        xl=xl,
                        xu=xu)
            params = {}
            for i , (name, param) in enumerate(dec_vars):
                params[param] = result.X[i] 
            cost = result.F[0]

        case 'GA_P':
            result = run_ga_p(scenario=source_scenario,
                        scenario_temp_path=scenario_temp_path,
                        output_path=output_path,
                        dec_vars_map=dec_vars,
                        n_var=n_var,
                        cost_fun=cost_fun,
                        termination=termination,
                        xl=xl,
                        xu=xu)
            params = {}
            for i , (name, param) in enumerate(dec_vars):
                params[param] = result.X[i] 
            cost = result.F[0]

    print(result)
    result_print(dec_vars, params, cost)
    elapsed = time.time() - start
    print("Elapsed time is ", elapsed)
