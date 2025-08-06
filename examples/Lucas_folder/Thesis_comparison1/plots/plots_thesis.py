import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import itertools
from mpl_toolkits.mplot3d import Axes3D  # Enables 3D plotting
import numpy as np
import ast 
import os
import glob



figs = []


label_font_size = 18
tick_font_size = 14
linewidth = 2
marker_size = 30


plot_saving_dir = 'C:/Users/31633/Dropbox/My PC (DESKTOP-84P3QQD)/Documents/Master_thesis/Thesis_figures/Discussion/Additional_plots'

time_num_iter_pso = np.array(sorted(np.array([[9, 282.852271],
                            [9, 324.635174],
                            [9, 337.153749]]), key=lambda x: x[0]))

time_num_iter_ga = np.array(sorted(np.array([[12, 378.087273],
                            [12, 398.462270],
                            [11, 362.772634]]), key=lambda x: x[0]))

time_num_iter_lbfgsb = np.array(sorted(np.array([[41, 2811.39956],
                            [61, 4099.06786],
                            [57, 2762.72854],
                            [43, 2510.97016]]), key=lambda x: x[0]))





fig1 = plt.figure(figsize=(8, 5))
plt.plot(time_num_iter_pso[:, 0], time_num_iter_pso[:, 1], linewidth=linewidth)
plt.plot(time_num_iter_ga[:, 0], time_num_iter_ga[:, 1], linewidth=linewidth)
plt.plot(time_num_iter_lbfgsb[:, 0], time_num_iter_lbfgsb[:, 1], linewidth=linewidth)
# plt.title('Search Space (Log-Scaled Fitness)')
plt.xlabel('Numer of iterations', fontsize=label_font_size)
plt.ylabel('Total elapsed time [s]', fontsize=label_font_size)
# plt.xlim(100, 600)
# plt.ylim(2.5, 5.6)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.grid(True)
plt.tight_layout()

figs.append((fig1, 'discussion_time_iter.png'))

plt.show()
# save_all = input(f"Save all plots to {plot_saving_dir}? (y/n)").strip().lower() == 'y'
# if save_all:
#     os.makedirs(plot_saving_dir, exist_ok=True)

#     for fig, ffilename in figs:
#         path = os.path.join(plot_saving_dir, ffilename)
#         fig.savefig(path, dpi=300)
#         print(f"Saved {fig} as {ffilename}")