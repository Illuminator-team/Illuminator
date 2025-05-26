import pandas as pd
import numpy as np
import ast
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors

# Load and process data
data = pd.read_csv('examples\Lucas_folder\Optimization_project\PSO_live_log.csv')

# Convert 'solution' column to list of ceiled integers
data['solution'] = data['solution'].apply(lambda x: [int(np.ceil(val)) for val in ast.literal_eval(x)])

# Extract fitness numeric values for sorting and coloring
data['fitness_sort'] = data['fitness'].apply(lambda x: ast.literal_eval(x)[0])
data = data.sort_values(by='fitness_sort').drop(columns=['fitness_sort'])
data['fitness_numeric'] = data['fitness'].apply(lambda x: ast.literal_eval(x)[0])

# Normalize fitness values for colormap
min_c = data['fitness_numeric'].min()
max_c = data['fitness_numeric'].max()
norm = mcolors.Normalize(vmin=min_c, vmax=max_c)
cmap = cm.plasma  # You can also try 'plasma', 'inferno', 'coolwarm', etc.

# Plot
plt.figure(figsize=(8, 5))
x_vals = range(5)

for i, (_, row) in enumerate(data.iterrows()):
    # if i>300:
    #     continue
    # if i % 10 != 0:
    #     continue  # skip lines except every 10th
    y_vals = row['solution']
    c_val = row['fitness_numeric']
    color = cmap(norm(c_val))
    plt.plot(x_vals, y_vals, marker='o', color=color, linewidth=2)

# Add colorbar
sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])  # Required for colorbar
cbar = plt.colorbar(sm)
cbar.set_label("Fitness Value")

# Labels and layout
plt.xlabel('Index in List (Position in B)')
plt.ylabel('Ceiled Values from B')
plt.title('Solutions Colored by Fitness (Lower = Better)')
plt.grid(True)
plt.tight_layout()
plt.show()
