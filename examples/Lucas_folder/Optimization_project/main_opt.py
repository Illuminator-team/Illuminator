from PSO_alg import run_pso
from PSO_alg_p import run_pso_p
from cost_fun import *
import numpy as np
import os
import yaml
## Specify scenario and output path
source_scenario = './examples/Tutorial1/Tutorial_1.yaml'# "./examples/h2_system_example/h2_system_4.yaml"
output_path = 'examples/Tutorial1/out_Tutorial1.csv'# './examples/h2_system_example/h2_system_example4.csv'

if __name__ == "__main__":
    ## Define the decision variables here (model, paramter)
    dec_vars = [
        # ('H2Buffer', 'h2_capacity_tot'),
        # ('H2Buffer', 'h2_soc_min')
        ('PV1', 'm_tilt'),
        ('PV1', 'm_area')
    ]
    n_var = len(dec_vars)


    ## Define the algorithm used (possible entries are PSO,GA,SA or ABC)
    alg = "PSO"

    ## Determine which cost function from cost_fun.py to use
    cost_fun = cost_fun1

    ## Determine termination criterium
    termination = ("n_gen", 10)

    ## set lower and upper bounds for decision variables
    # xl = np.array([0, 0])
    # xu = np.array([100000, 99])
    xl = np.array([0, 0])
    xu = np.array([90, 10])

    def result_print(dec_vars, results):
        optimal_params = {}
        for i , (name, param) in enumerate(dec_vars):
            optimal_params[param] = results.X[i] 
        cost = results.F[0]
        print(f"The optimal parameters are:\n {optimal_params}\n Resulting in a cost of: {cost}")
        return optimal_params, cost

    def make_dynamic_yaml_path(original_scenario: str, alg: str):
        """
        Takes the original yaml and creates a new one that can be dynamically editted without interfering with the original
        """
        if original_scenario.endswith(".yaml"):
            file_name = original_scenario.split('/')[-1].removesuffix('.yaml')
            dynamic_path = f"examples\Lucas_folder\Optimization_project\dynamic_yamls/{file_name}_{alg}.yaml"
        else:
            raise ValueError("Provided scenario is not a yaml file")
        print(dynamic_path)
        os.makedirs(os.path.dirname(dynamic_path), exist_ok=True)
        # Read the original YAML file
        with open(original_scenario, 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)

        # Write the data to the new temporary YAML file
        with open(dynamic_path, 'w') as file:
            yaml.dump(data, file)
        return dynamic_path


    # ## Run PSO:
    match alg:
        case 'PSO':
            result = run_pso_p(scenario=make_dynamic_yaml_path(source_scenario, alg),
                        output_path=output_path,
                        dec_vars_map=dec_vars,
                        n_var=n_var,
                        cost_fun=cost_fun,
                        termination=termination,
                        xl=xl,
                        xu=xu)
        # add other algs

    print(result)
    result_print(dec_vars, result)
