import pandas as pd
import matplotlib.pyplot as plt
import itertools
from mpl_toolkits.mplot3d import Axes3D  # Enables 3D plotting
import numpy as np
import ast 
import os
import glob

data_folder = './examples/Lucas_folder/Thesis_comparison2/data/sc_log'


log_files = glob.glob(os.path.join(data_folder, "*.csv"))
# print(log_files)

column_names = ["x1", "x2", "fitness"]

# Read and concatenate all CSVs with column names
df_list = [pd.read_csv(file, header=None, names=column_names) for file in log_files]
combined_df = pd.concat(df_list, ignore_index=True)
sorted_df = combined_df.sort_values(by=["x1", "x2"])

# Save to a new CSV
combined_df.to_csv("./examples/Lucas_folder/Thesis_comparison2/data/sc_log/combined_output.csv", index=False)


markers = itertools.cycle(('o', 's', '^', 'v', 'D', 'P', '*', 'X', 'H'))

df = pd.read_csv("./examples/Lucas_folder/Thesis_comparison2/data/sc_log/combined_output.csv")
df.drop_duplicates()

# Convert to numeric
df["x1"] = pd.to_numeric(df["x1"], errors="coerce")
df["x2"] = pd.to_numeric(df["x2"], errors="coerce")
df["fitness"] = pd.to_numeric(df["fitness"], errors="coerce")

# Drop or aggregate duplicates
df = df.groupby(["x1", "x2"], as_index=False).mean()

# Pivot to grid
pivot = df.pivot(index="x2", columns="x1", values="fitness")

# Create meshgrid
x = np.array(pivot.columns)
y = np.array(pivot.index)
X, Y = np.meshgrid(x, y)
Z = pivot.values

# --- 3D Surface Plot ---
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(X, Y, Z, cmap="viridis", edgecolor='k', linewidth=0.5, alpha=0.8)

ax.set_xlabel("x1")
ax.set_ylabel("x2")
ax.set_zlabel("Fitness")
ax.set_title("L-BFGS-B: Search Space Exploration (3D Surface)")
plt.tight_layout()
plt.show()

# Ensure fitness is numeric
df["fitness"] = pd.to_numeric(df["fitness"], errors='coerce')
df["x1"] = pd.to_numeric(df["x1"], errors='coerce')
df["x2"] = pd.to_numeric(df["x2"], errors='coerce')
print(df.loc[df["fitness"].idxmin()])

# --- Search Space Plot ---
plt.figure(figsize=(8, 5))
plt.scatter(df["x1"], df["x2"], c=df["fitness"], cmap='viridis', alpha=0.6)
plt.colorbar(label='Fitness')
plt.xlabel('x1')
plt.ylabel('x2')
plt.title('L-BFGS-B: Search Space Exploration (Parallel)')
plt.grid(True)
plt.tight_layout()


# --- Search space plot x1 ---
plt.figure(figsize=(8, 5))

# Ensure fitness is numeric
df["fitness"] = pd.to_numeric(df["fitness"], errors='coerce')

plt.scatter(df["x1"], df["fitness"], c=df["fitness"], cmap='viridis', alpha=0.6)
plt.colorbar(label='Fitness')
plt.xlabel('x1')
plt.ylabel('fitness')
plt.title('L-BFGS-B: Search Space Exploration x1 (Parallel)')
plt.grid(True)
plt.legend(fontsize='x-small', loc='best')
plt.tight_layout()

# --- Search space plot x2 ---
plt.figure(figsize=(8, 5))

# Ensure fitness is numeric
df["fitness"] = pd.to_numeric(df["fitness"], errors='coerce')

    
plt.scatter(df["x2"], df["fitness"], c=df["fitness"], cmap='viridis', alpha=0.6)

plt.colorbar(label='Fitness')
plt.xlabel('x2')
plt.ylabel('fitness')
plt.title('L-BFGS-B: Search Space Exploration x2 (Parallel)')
plt.grid(True)
plt.legend(fontsize='x-small', loc='best')
plt.tight_layout()
# plt.show()

# from mpl_toolkits.mplot3d import Axes3D  # Already imported
# from mpl_toolkits.mplot3d.art3d import Poly3DCollection
# from matplotlib import cm

# # Pivot the data into a 2D grid (Z must be reshaped accordingly)
# pivot = df.pivot(index='x2', columns='x1', values='fitness')

# # Ensure x and y are sorted properly for grid compatibility
# x_unique = np.sort(df['x1'].unique())
# y_unique = np.sort(df['x2'].unique())
# X, Y = np.meshgrid(x_unique, y_unique)
# Z = pivot.values  # Z must have shape (len(y), len(x))

# # --- 3D surface plot ---
# fig = plt.figure(figsize=(10, 6))
# ax = fig.add_subplot(111, projection='3d')
# surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='k', alpha=0.9)

# fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label='Fitness')
# ax.set_xlabel('x1')
# ax.set_ylabel('x2')
# ax.set_zlabel('Fitness')
# ax.set_title('3D Grid Search Fitness Surface')
# plt.tight_layout()
plt.show()



