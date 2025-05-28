import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('C:/Users/31633/Python_projects/Illuminator/examples/Lucas_folder/Thesis_comparison2/data/household_power_consumption_15min.csv')
# Convert 'date' column to datetime (ensure correct day/month ordering)

# Convert date column to datetime
df['date'] = pd.to_datetime(df['date'], dayfirst=True)

# Convert power values to numeric
df['load1'] = pd.to_numeric(df['load1'], errors='coerce')
df['load2'] = pd.to_numeric(df['load2'], errors='coerce')
df['load3'] = pd.to_numeric(df['load3'], errors='coerce')
df['load4'] = pd.to_numeric(df['load4'], errors='coerce')
df['load5'] = pd.to_numeric(df['load5'], errors='coerce')


# Sort by date to be safe
df = df.sort_values('date')

# Plot the first 24 points
plt.figure(figsize=(10, 5))
plt.plot(df['date'][24*4*7:24*4*14], df['load1'][24*4*7:24*4*14], label='load1')
plt.plot(df['date'][24*4*7:24*4*14], df['load2'][24*4*7:24*4*14], label='load2')
plt.plot(df['date'][24*4*7:24*4*14], df['load3'][24*4*7:24*4*14], label='load3')
plt.plot(df['date'][24*4*7:24*4*14], df['load4'][24*4*7:24*4*14], label='load4')
plt.plot(df['date'][24*4*7:24*4*14], df['load5'][24*4*7:24*4*14], label='load5')
plt.xlabel('Time')
plt.ylabel('Power (kW)')
plt.legend()
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()