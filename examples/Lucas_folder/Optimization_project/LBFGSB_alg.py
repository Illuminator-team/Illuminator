import numpy as np
from sim_wrapper import eval_sim
import os
from scipy.optimize import minimize
from multiprocessing import Pool
import csv

## NOTE to self:    right now the simulation of a new x is evaluated twice, 
#                   once for the objective function itself and once for the jacobian 
#                   ficing this would improve run time by: 1sim time * # steps required

n_cores =  os.cpu_count() - 3

LBFGSB_log_file = "./examples/Lucas_folder/Optimization_project/LBFGSB_live_log.csv"
LBFGSB_grad_log_file = "./examples/Lucas_folder/Optimization_project/LBFGSB_grad_live_log.csv"

class LBFGSB_logger:
    def __init__(self, logfile, grad_logfile):
        self.logfile = logfile
        self.grad_logfile = grad_logfile
        self.iter = 0
        with open(self.logfile, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["iter", "obj", "x"])

        with open(self.grad_logfile, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["iter", "grad"])

    def log(self, x, f):
        self.iter += 1
        with open(self.logfile, mode='a', newline = '') as file:
            writer = csv.writer(file)
            writer.writerow([self.iter, f]+ list(x))

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
        
    def __call__(self, x, *args, **kwds):
        f = eval_sim(original_scenario=self.scenario,
            scenario_temp_path=self.scenario_temp_path,
            output_path=self.output_path,
            dec_vars_map=self.dec_vars_map,
            x=x,
            cost_fun=self.cost_fun,
            n_cores=n_cores
            )
        self.logger.log(x, f)
        return f
        
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
    epsilons, scenario, scenario_temp_path, output_path, dec_vars_map, cost_fun, logger = args
    f = eval_sim(original_scenario=scenario,
            scenario_temp_path=scenario_temp_path,
            output_path=output_path,
            dec_vars_map=dec_vars_map,
            x=x,
            cost_fun=cost_fun,
            n_cores=n_cores
            )
    fd = FiniteDifference(x, epsilons, scenario, scenario_temp_path, output_path, dec_vars_map, cost_fun)
    gradient = fd.compute_gradient(f)
    logger.log_grad(gradient)
    return gradient
    
    # def FD_task(i):
    #     x_plus = x.copy()
    #     x_plus[i] += epsilons[i]
    #     f_plus = eval_sim(original_scenario=scenario,
    #                 scenario_temp_path=scenario_temp_path,
    #                 output_path=output_path,
    #                 dec_vars_map=dec_vars_map,
    #                 x=x,
    #                 cost_fun=cost_fun,
    #                 n_cores=n_cores
    #                 )
    #     return (i , f_plus)
    
    # with Pool(min(n_cores, len(x))) as pool:
    #     result = pool.map(FD_task, range(len(x)))
    # # pool.close()
    # # pool.join()
    # return gradient(f, result, epsilons)


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
                      args=(epsilons, scenario, scenario_temp_path, output_path, dec_vars_map, cost_fun, logger),
                      jac=FD_alg,
                      bounds=list(zip(xl, xu)),
                      method="L-BFGS-B",
                      options={"maxiter": 20,
                               "disp": True}
                               )

    return result
