    

import numpy as np


n_cores = 9
xu = [55, 56, 57]
xl = [5, 6, 7]

dec_vars = [1, 2, 3]
print(type(dec_vars))
x0_matrix = np.zeros((n_cores, len(dec_vars)))


for var in range(len(dec_vars)):
    x0_matrix[:, var] = np.linspace(xl[var], xu[var], n_cores)
    print(x0_matrix)
for x0 in range(len(x0_matrix)):
    print(type(x0_matrix[x0][:]))
