import numpy as np
import matplotlib.pyplot as plt
import os

plot_saving_dir = 'C:/Users/31633/Dropbox/My PC (DESKTOP-84P3QQD)/Documents/Master_thesis/Thesis_figures/Background'
figs = []
label_font_size = 18
tick_font_size = 14
linewidth = 2
marker_size = 30
second_linewidth=.5

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
fig1 = plt.figure(figsize=(8, 5))
plt.plot(x, y, label='$f(x)=0.5x^4-3.5x^3+8.5x^2-8.5x+3$', color='b', linewidth=linewidth)
plt.scatter([local_min_x, global_min_x], [local_min_y, global_min_y], color='red', s=marker_size ,zorder=3)

# Annotate the minima
plt.text(local_min_x, local_min_y + .15, 'Local', ha='center', fontsize=label_font_size, color='red')
plt.text(global_min_x, global_min_y - .25, 'Global', ha='center', fontsize=label_font_size, color='red')
plt.xlim(0, 4)
plt.ylim(-1, 3.5)
# Labels and grid
plt.xlabel('$x$', fontsize=label_font_size)
plt.ylabel('$f(x)$', fontsize=label_font_size)
# plt.axhline(y=0, color='black', linewidth=linewidth)
# plt.axvline(x=0, color='black', linewidth=linewidth)
plt.legend()
plt.grid(True)
plt.tick_params(axis='y', labelsize=tick_font_size)
plt.tick_params(axis='x', labelsize=tick_font_size)
# Show plot
plt.show()
figs.append((fig1, 'localvglobal_plot.png'))

save_all = input(f"Save all plots to {plot_saving_dir}? (y/n)").strip().lower() == 'y'
if save_all:
    os.makedirs(plot_saving_dir, exist_ok=True)

    for fig, ffilename in figs:
        path = os.path.join(plot_saving_dir, ffilename)
        fig.savefig(path, dpi=300)
        print(f"Saved {fig} as {ffilename}")