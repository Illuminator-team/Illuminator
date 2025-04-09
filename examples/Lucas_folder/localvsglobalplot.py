import numpy as np
import matplotlib.pyplot as plt

# Define a function with a local and global minimum
def f(x):
    return 0.5*x**4 - 3.5*x**3+8.5*x**2-8.5*x + 3
    


# Generate x values
x = np.linspace(0, 5, 400)
y = f(x)

# Find the approximate local and global minima
local_min_x, local_min_y = (1, f(1))   # Local minimum
global_min_x, global_min_y = (2.64039, f(2.64039)) # Global minimum

# Plot the function
plt.figure(figsize=(8, 5))
plt.plot(x, y, label='$f(x)=0.5x^4-3.5x^3+8.5x^2-8.5x+3$', color='b')
plt.scatter([local_min_x, global_min_x], [local_min_y, global_min_y], color='red', zorder=3)

# Annotate the minima
plt.text(local_min_x, local_min_y + .15, 'Local', ha='center', fontsize=12, color='red')
plt.text(global_min_x, global_min_y - .25, 'Global', ha='center', fontsize=12, color='red')
plt.xlim(0, 4)
plt.ylim(-1, 3.5)
# Labels and grid
plt.xlabel('$x$')
plt.ylabel('$f(x)$')
plt.axhline(y=0, color='black', linewidth=0.5)
plt.axvline(x=0, color='black', linewidth=0.5)
plt.legend()
plt.grid(True)

# Show plot
plt.show()
