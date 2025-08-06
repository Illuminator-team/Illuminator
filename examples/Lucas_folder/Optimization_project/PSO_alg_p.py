from pymoo.algorithms.soo.nonconvex.pso import PSO
from pymoo.core.problem import ElementwiseProblem, StarmapParallelization
from pymoo.core.problem import Problem

from pymoo.optimize import minimize
from sim_wrapper import eval_sim
import numpy as np
import csv
import os
from multiprocessing.pool import Pool
# from multiprocessing.pool import ThreadPool

n_cores = os.cpu_count() - 3 # leave three cores
# n_cores = 3     # this is amount of simulataneous processes
# print(n_cores)
# n_threads = 3


PSO_log_file = "./examples/Lucas_folder/Optimization_project/PSO_live_log.csv"
# PSO_log_file = "./examples/Lucas_folder/Illuminator_presentation/PSO_live_log.csv"

class PSOLogger:
    def __init__(self, logfile):
        self.logfile = logfile
        # os.makedirs(os.path.dirname(self.logfile), exist_ok=True)
        with open(self.logfile, mode='w', newline='') as file:
            writer = csv.writer(file)
            # writer.writerow(["generation", "best_generation_solution", "best_genearion_fitness", "mean_fitness", "best_solution", "best_fitness", "std_fitness"])
            writer.writerow(["generation", "solution", "fitness"])  # Header with solution and fitness
    def __call__(self, algorithm):
        gen = algorithm.n_gen
        X = algorithm.pop.get("X")
        F = algorithm.pop.get("F")
        # print(f"DEBUG: in logger x={X} fitness={F}")
        best_idx = F.argmin()
        best_gen_solution = X[best_idx].tolist()
        best_gen_fitness = F[best_idx]
        mean = F.mean()
        std_fitness = F.std()
        global_best_solution = algorithm.opt.get("X").tolist()
        global_best_fitness = algorithm.opt.get("F")[0]

        with open(self.logfile, mode='a', newline = '') as file:
            writer = csv.writer(file)
            # writer.writerow([gen, best_gen_solution, best_gen_fitness, mean, global_best_solution, global_best_fitness, std_fitness])
            for sol, fit in zip(X, F):
                writer.writerow([gen, sol.tolist(), fit.tolist()])  # Log solution and its fitness

class SimulationProblem(ElementwiseProblem):
    def __init__(self, scenario, scenario_temp_path, output_path, dec_vars_map, n_var, cost_fun, xl, xu, runner=None):
        if runner is not None:
            super().__init__(n_var=n_var, n_obj=1, xl=xl, xu=xu, elementwise_runner=runner)
        else:
            super().__init__(n_var=n_var, n_obj=1, xl=xl, xu=xu)
        self.scenario = scenario
        self.output_path = output_path
        self.dec_vars_map = dec_vars_map
        self.cost_fun = cost_fun
        self.scenario_temp_path = scenario_temp_path
        
    def _evaluate(self, x, out, *args, **kwargs):
        # print(f"DEBUG: in _evaluate x = {x}")
        result = eval_sim(original_scenario=self.scenario,
                scenario_temp_path=self.scenario_temp_path,
                output_path=self.output_path,
                dec_vars_map=self.dec_vars_map,
                x=x,
                cost_fun=self.cost_fun,
                n_cores=n_cores
                )
        # print(f"DEBUG: IN _evaluate after result: x={x} and result={result}")
        out["F"] = result

def run_pso_p(scenario, scenario_temp_path, output_path, dec_vars_map, n_var, cost_fun, termination, xl, xu):

    
    pool = Pool(processes=n_cores)
    runner = StarmapParallelization(pool.starmap)
    problem = SimulationProblem(
                                scenario=scenario,
                                scenario_temp_path=scenario_temp_path,
                                output_path=output_path,
                                dec_vars_map=dec_vars_map,
                                n_var=n_var,
                                cost_fun=cost_fun,
                                xl=xl,
                                xu=xu,
                                runner=runner)
    
    algorithm = PSO(pop_size=9,
                    w=0.9,
                    c1=1.5,
                    c2=1.5,
                    vmax=np.inf,
                    adaptive=True,
                    remove_duplicates=True)

    result = minimize(problem,
                    algorithm,
                    callback=PSOLogger(PSO_log_file),
                    termination=termination,
                    seed=1,
                    verbose=True,
                    )
    pool.close()
    pool.join()
    return result

def run_pso(scenario, scenario_temp_path, output_path, dec_vars_map, n_var, cost_fun, termination, xl, xu):
    # print(dec_vars_map)
    
    
    problem = SimulationProblem(scenario=scenario,
                                scenario_temp_path=scenario_temp_path,
                                output_path=output_path,
                                dec_vars_map=dec_vars_map,
                                n_var=n_var,
                                cost_fun=cost_fun,
                                xl=xl,
                                xu=xu,
                                runner=None)
    algorithm = PSO(pop_size=9,
                    w=0.9,
                    c1=2.0,
                    c2=2.0,
                    vmax=np.inf,
                    adaptive=False,
                    remove_duplicates=True)

    result = minimize(problem,
                      algorithm,
                      callback=PSOLogger(PSO_log_file),
                      termination=termination,
                      seed=42,
                      verbose=True)
    return result

    
