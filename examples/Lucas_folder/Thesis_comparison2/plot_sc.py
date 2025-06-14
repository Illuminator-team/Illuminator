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
plt.show()



