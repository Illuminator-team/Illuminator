import numpy as np
from sim_wrapper import eval_sim
import os
from scipy.optimize import minimize
from multiprocessing import Pool

## NOTE to self:    right now the simulation of a new x is evaluated twice, 
#                   once for the objective function itself and once for the jacobian 
#                   ficing this would improve run time by: 1sim time * # steps required

n_cores =  os.cpu_count() - 3

class SimulationProblem:
    def __init__(self, scenario, scenario_temp_path, output_path, dec_vars_map, cost_fun, xl, xu):
        self.scenario = scenario
        self.output_path = output_path
        self.dec_vars_map = dec_vars_map
        self.cost_fun = cost_fun
        self.scenario_temp_path = scenario_temp_path
    def __call__(self, x, *args, **kwds):
        f = eval_sim(original_scenario=self.scenario,
            scenario_temp_path=self.scenario_temp_path,
            output_path=self.output_path,
            dec_vars_map=self.dec_vars_map,
            x=x,
            cost_fun=self.cost_fun,
            n_cores=n_cores
            )
        return f
        
def gradient(f: float, result: list[tuple], epsilons: list):
    len_f_plus = len(result)
    gradient = [0] * len_f_plus
    for i in range(len_f_plus):
        gradient[i] = (result[i][1] - f) / epsilons[i]
    return gradient
        
def FD_alg(x, epsilons, scenario, scenario_temp_path, output_path, dec_vars_map, cost_fun, xl, xu):
    f = eval_sim(original_scenario=scenario,
            scenario_temp_path=scenario_temp_path,
            output_path=output_path,
            dec_vars_map=dec_vars_map,
            x=x,
            cost_fun=cost_fun,
            n_cores=n_cores
            )
    
    def FD_task(i):
        x_plus = x.copy()
        x_plus[i] += epsilons[i]
        f_plus = eval_sim(original_scenario=scenario,
                    scenario_temp_path=scenario_temp_path,
                    output_path=output_path,
                    dec_vars_map=dec_vars_map,
                    x=x,
                    cost_fun=cost_fun,
                    n_cores=n_cores
                    )
        return (i , f_plus)
    
    with Pool(min(n_cores(), len(x))) as pool:
        result = pool.map(FD_task, range(len(x)))
    pool.close()
    pool.join()
    return gradient(f, result, epsilons)


def run_LBFGSB():
    problem = SimulationProblem(scenario=scenario,
                            scenario_temp_path=scenario_temp_path,
                            output_path=output_path,
                            dec_vars_map=dec_vars_map,
                            cost_fun=cost_fun,
                            xl=xl,
                            xu=xu)
    jac = 
    result = minimize(problem,
                      x_initial,
                      jac = FD_alg)

    return result
