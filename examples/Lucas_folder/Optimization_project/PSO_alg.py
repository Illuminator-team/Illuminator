from pymoo.algorithms.soo.nonconvex.pso import PSO
from pymoo.core.problem import Problem
from pymoo.optimize import minimize
from sim_wrapper import eval_sim


def run_pso(scenario, output_path, dec_vars_map, n_var, cost_fun, xl, xu):
    class SimulationProblem(Problem):
        def __init__(self):
            super().__init__(n_var=n_var,
                            n_obj=1,
                            xl=xl,
                            xu=xu)
        def _evaluate(self, x, out, *args, **kwargs):
            df = eval_sim(scenario=scenario,
                    output_path=output_path,
                    dec_vars_map=dec_vars_map,
                    x=x
                    )
            out["F"] = cost_fun(df)
    
    problem = SimulationProblem()
    algorithm = PSO()
    result = minimize(problem,
                      algorithm,
                      seed=42,
                      verbose=True)
    return result



    
