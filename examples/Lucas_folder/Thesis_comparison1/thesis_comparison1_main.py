import sys
import os
from pymoo.termination.default import DefaultSingleObjectiveTermination
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Optimization_project')))

from PSO_alg_p import run_pso, run_pso_p
from GA_alg_p import run_ga, run_ga_p
from LBFGSB_alg import run_LBFGSB, run_LBFGSB2
from cost_fun import *
import numpy as np
import os
import yaml
import time
import math

start = time.time()
## Specify scenario and output path

source_scenario = './examples/Lucas_folder/Thesis_comparison1/thesis_comparison_hydrogen_monthly.yaml' # './examples/Tutorial1/Tutorial_1.yaml'# "./examples/h2_system_example/h2_system_4.yaml"
output_path = './examples/Lucas_folder/Thesis_comparison1/temp_out/thesis_comparison1.csv'# './examples/h2_system_example/h2_system_example4.csv'
scenario_temp_path = './examples/Lucas_folder/Thesis_comparison1/temp_scenario'


if __name__ == "__main__":
    ## Define the decision variables here (model, paramter)
    dec_vars = [
        ('H2Buffer1', 'h2_capacity_tot')
    ]
    n_var = len(dec_vars)

    ## Define the algorithm used (possible entries are PSO, PSO_P, GA,SA or ABC)
    alg = 'LBFGSB2' #"GA_P" # 

    ## Determine which cost function from cost_fun.py to use
    # cost_fun = cost_fun1
    cost_fun = optimal_buffer_size
    

    ## set lower and upper bounds for decision variables
    xl = np.array([100])
    xu = np.array([600])

    ## FOR PSO
    ## Determine termination criterium (FOR PSO)
    # termination = ("n_gen", 10)
    termination = DefaultSingleObjectiveTermination(
                                                    xtol=1e-3,         # Tolerance in decision variables
                                                    ftol=1e-3,         # Tolerance in objective function
                                                    period=5,          # Number of generations to check for convergence
                                                    n_max_gen=30     # Max generations
                                                    )

    ## FOR LBFGSB
    ## Determine initial guess x0 and epsilons
    epsilons = [1e5] # [1e-5, 1e-5]
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

        case 'LBFGSB2':
            result = run_LBFGSB2(scenario=source_scenario,
                                scenario_temp_path=scenario_temp_path,
                                output_path=output_path,
                                dec_vars_map=dec_vars,
                                cost_fun=cost_fun,
                                xl=xl,
                                xu=xu,
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
