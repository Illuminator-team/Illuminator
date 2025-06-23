import numpy as np
from sim_wrapper import eval_sim
import os
from scipy.optimize import minimize
from multiprocessing import Pool
import random
random.seed(1)  # For reproducibility
import csv
import datetime


n_cores =  os.cpu_count() - 3

LBFGSB_log_file = "./examples/Lucas_folder/Optimization_project/LBFGSB_live_log.csv"
LBFGSB_grad_log_file = "./examples/Lucas_folder/Optimization_project/LBFGSB_grad_live_log.csv"
LBFGSB_log_file_p = "./examples/Lucas_folder/Optimization_project/LBFGSB_p/LBFGSB_live_log"
LBFGSB_grad_log_file_p = "./examples/Lucas_folder/Optimization_project/LBFGSB_p/LBFGSB_grad_live_log"

class LBFGSB_logger:
    def __init__(self, logfile, grad_logfile):
        self.logfile = logfile
        self.grad_logfile = grad_logfile
        self.iter = 0
        with open(self.logfile, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["iter", "fitness","timestep", "solution"])

        with open(self.grad_logfile, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["iter", "grad"])

    def log(self, x, f):
        self.iter += 1
        current_time = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        with open(self.logfile, mode='a', newline = '') as file:
            writer = csv.writer(file)
            writer.writerow([self.iter, f, current_time] + list(x))

    def log_grad(self, grad):
        with open(self.grad_logfile, mode='a', newline = '') as file:
            writer = csv.writer(file)
            writer.writerow([self.iter, grad])



class SimulationProblem:
    def __init__(self, scenario, scenario_temp_path, output_path, dec_vars_map, cost_fun, xl, xu, logger):
        self.scenario = scenario
        self.output_path = output_path
        self.dec_vars_map = dec_vars_map
        self.cost_fun = cost_fun
        self.scenario_temp_path = scenario_temp_path
        self.logger = logger

        self.last_x = None
        self.last_f = None


    def __call__(self, x, *args, **kwds):
        if self.last_x is None or not np.allclose(x, self.last_x):
            self.last_f = eval_sim(original_scenario=self.scenario,
                scenario_temp_path=self.scenario_temp_path,
                output_path=self.output_path,
                dec_vars_map=self.dec_vars_map,
                x=x,
                cost_fun=self.cost_fun,
                n_cores=n_cores
                )
            self.last_x = x.copy()
            self.logger.log(x, self.last_f)
        return self.last_f
        # f = eval_sim(original_scenario=self.scenario,
        #     scenario_temp_path=self.scenario_temp_path,
        #     output_path=self.output_path,
        #     dec_vars_map=self.dec_vars_map,
        #     x=x,
        #     cost_fun=self.cost_fun,
        #     n_cores=n_cores
        #     )
        # self.logger.log(x, f)
        # return f
        
class FiniteDifference:
    def __init__(self, x, epsilons, scenario, scenario_temp_path, output_path, dec_vars_map, cost_fun):
        self.x = x
        self.epsilons = epsilons
        self.scenario = scenario
        self.scenario_temp_path = scenario_temp_path
        self.output_path = output_path
        self.dec_vars_map = dec_vars_map
        self.cost_fun = cost_fun

    def simulate(self, i):
        x_plus = self.x.copy()
        x_plus[i] += self.epsilons[i]
        f_plus = eval_sim(
        original_scenario=self.scenario,
        scenario_temp_path=self.scenario_temp_path,
        output_path=self.output_path,
        dec_vars_map=self.dec_vars_map,
        x=x_plus,
        cost_fun=self.cost_fun,
        n_cores=n_cores
        )
        return (i, f_plus)
    
    def compute_gradient(self, f):

        with Pool(min(n_cores, len(self.x))) as pool:
            results = pool.map(self.simulate, range(len(self.x)))
        gradient = [(results[i][1] - f) / self.epsilons[i] for i in range(len(self.x))]
        return gradient
        
# def gradient(f: float, result: list[tuple], epsilons: list):
#     len_f_plus = len(result)
#     gradient = [0] * len_f_plus
#     for i in range(len_f_plus):
#         gradient[i] = (result[i][1] - f) / epsilons[i]
#     return gradient

def FD_alg(x, *args):
    epsilons, problem, logger = args
    if problem.last_x is not None and np.allclose(problem.last_x, x):
        f = problem(x)
    else:
        f = problem.last_f
    fd = FiniteDifference(x, epsilons, problem.scenario, problem.scenario_temp_path,
                          problem.output_path, problem.dec_vars_map, problem.cost_fun)
    gradient = fd.compute_gradient(f)
    logger.log_grad(gradient)
    return gradient
    


def run_LBFGSB(scenario, scenario_temp_path, output_path, dec_vars_map, cost_fun, xl, xu, x0, epsilons):
    logger = LBFGSB_logger(LBFGSB_log_file, LBFGSB_grad_log_file)
    problem = SimulationProblem(scenario=scenario,
                            scenario_temp_path=scenario_temp_path,
                            output_path=output_path,
                            dec_vars_map=dec_vars_map,
                            cost_fun=cost_fun,
                            xl=xl,
                            xu=xu,
                            logger=logger)

    result = minimize(fun=problem,
                      x0=x0,
                      args=(epsilons, problem, logger),
                      jac=FD_alg,
                      bounds=list(zip(xl, xu)),
                      method="L-BFGS-B",
                      options={"maxiter": 3,
                               "disp": True,
                               "ftol": 1e-6}
                               )

    return result

## Parallelized LBFGSB
class FiniteDifference2:
    def __init__(self, x, epsilons, scenario, scenario_temp_path, output_path, dec_vars_map, cost_fun):
        self.x = x
        self.epsilons = epsilons
        self.scenario = scenario
        self.scenario_temp_path = scenario_temp_path
        self.output_path = output_path
        self.dec_vars_map = dec_vars_map
        self.cost_fun = cost_fun

    def simulate(self, i):
        x_plus = self.x.copy()
        x_plus[i] += self.epsilons[i]
        f_plus = eval_sim(
        original_scenario=self.scenario,
        scenario_temp_path=self.scenario_temp_path,
        output_path=self.output_path,
        dec_vars_map=self.dec_vars_map,
        x=x_plus,
        cost_fun=self.cost_fun,
        n_cores=n_cores
        )
        return f_plus
    
    def compute_gradient(self, f):
        gradient = np.zeros(len(self.x))
        for i in range(len(self.x)):
            f_plus = self.simulate(i)
            gradient[i] = (f_plus - f) / self.epsilons[i]
        return gradient
    
def FD_alg2(x, *args):
    epsilons, problem, logger = args
    if problem.last_x is not None and np.allclose(problem.last_x, x):
        f = problem(x)
    else:
        f = problem.last_f
    fd = FiniteDifference2(x, epsilons,problem.scenario, problem.scenario_temp_path,
                           problem.output_path, problem.dec_vars_map, problem.cost_fun)
    gradient = fd.compute_gradient(f)
    logger.log_grad(gradient)
    return gradient

def run_single_LBFGSB(x0, scenario, scenario_temp_path, output_path, dec_vars_map, cost_fun, xl, xu, epsilons):
    logger = LBFGSB_logger(f'{LBFGSB_log_file_p}_{os.getpid()}.csv', f'{LBFGSB_grad_log_file_p}_{os.getpid()}.csv')
    problem = SimulationProblem(scenario=scenario,
                            scenario_temp_path=scenario_temp_path,
                            output_path=output_path,
                            dec_vars_map=dec_vars_map,
                            cost_fun=cost_fun,
                            xl=xl,
                            xu=xu,
                            logger=logger)
    result = minimize(fun=problem,
                      x0=x0,
                      args=(epsilons, problem, logger),
                      jac=FD_alg2,
                      bounds=list(zip(xl, xu)),
                      method="L-BFGS-B",
                      options={"maxiter": 100,
                               "disp": True}
                               )

    return result

def run_LBFGSB2(scenario, scenario_temp_path, output_path, dec_vars_map, cost_fun, xl, xu, epsilons):
    
    n_instances = n_cores
    x0_matrix = np.zeros((n_instances, len(dec_vars_map)))

    for var in range(len(dec_vars_map)):
        # x0_matrix[:, var] = np.linspace(xl[var], xu[var], n_instances)
        x0_matrix[:, var] = np.random.uniform(low=xl[var], high=xu[var], size=n_instances)

        # x0_matrix[:, var] = (xu[var] + xl[var]) / 2
    print(x0_matrix)
    args_list = [
        (np.ravel(x0_matrix[i, :]), scenario, scenario_temp_path, output_path, dec_vars_map, cost_fun, xl, xu, epsilons)
        for i in range(n_instances)
    ]

    with Pool(processes=n_cores) as pool:
        results = pool.starmap(run_single_LBFGSB, args_list)

    # Find best result
    best_result = min(results, key=lambda res: res.fun)

    return best_result