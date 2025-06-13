    
import numpy as np
from scipy.optimize import minimize

def fun(x):
    return (x[0]-1)**2 + (x[1]-2)**2

x0 = [0,0]
res = minimize(fun, x0, method='L-BFGS-B', options={"maxiter": 5, "disp": True})
print(res)