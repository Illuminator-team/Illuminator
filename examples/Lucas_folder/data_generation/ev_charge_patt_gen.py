import numpy as np
import csv
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

timstep = 900       # (timestep of 15min) [s]
ev_cap = 60         # (for a Tesla model Y) [kWh]
charger_peak = 22   # maximum power output of the charger [kW]
soc_0 = 0           # initial state of charge [%]
soc = soc_0


n_evs = 5
start_date = "2007-01-01"
n_days = 365

def generate_ev_presence_matrix(n_evs, start_date, n_days):
    np.random.seed(42)

    # Setup time range
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    time_index = pd.date_range(start=start_dt, periods=n_days * 96, freq="15min")  # 96 steps/day for 15min

    presence_data = {f'ev{i+1}': [] for i in range(n_evs)}

    ev_states = [False] * n_evs
    for day in range(n_days):
        current_day = start_dt + timedelta(days=day)
        weekday = current_day.weekday()

        for ev in range(n_evs):
            presence = np.zeros(96, dtype=int)

            if ev_states[ev]:
                # Continue from previous night, define departure
                departure_hour = np.clip(np.random.normal(7, 1), 5, 9)
                departure_idx = int(departure_hour * 4)
                presence[:departure_idx] = 1
                ev_states[ev] = False  # assume it leaves unless new arrival

            if weekday < 5:
                # Weekday: arrive ~17-20, leave next day morning
                arrival_hour = np.clip(np.random.normal(18, 1), 16, 20)
                arrival_idx = int(arrival_hour * 4)
                presence[arrival_idx:] = 1
                ev_states[ev] = True  # stays overnight

            else:
                # Weekend
                stay_all_day = np.random.rand() < 0.3
                if stay_all_day:
                    presence[:] = 1
                    ev_states[ev] = True  # continue to next day
                else:
                    arrival_hour = np.clip(np.random.normal(10, 2), 8, 14)
                    duration = np.clip(np.random.normal(8, 2), 4, 12)
                    departure_hour = min(arrival_hour + duration, 24)

                    arrival_idx = int(arrival_hour * 4)
                    departure_idx = int(departure_hour * 4)
                    presence[arrival_idx:departure_idx] = 1
                    ev_states[ev] = departure_hour >= 24  # continue to next day if late

            presence_data[f'ev{ev+1}'].extend(presence)

    df = pd.DataFrame(presence_data, index=time_index)
    df.index.name = "timestamp"
    return df

# Example usage
df = generate_ev_presence_matrix(n_evs, start_date, n_days)


with open("./examples/Lucas_folder/Thesis_comparison2/data/ev_presence.csv", 'w', newline='') as f:
    
    f.write("Data\n")
    df.to_csv(f, index=True)
# print(df.head(90))

df = pd.read_csv("./examples/Lucas_folder/Thesis_comparison2/data/ev_presence.csv", index_col=0, parse_dates=True, skiprows=1)

# Plotting
plt.figure(figsize=(12, 6))

for i, column in enumerate(df.columns):
    plt.plot(df.index, df[column] + i * 1.2, label=column)  # Offset lines to distinguish them

plt.xlabel("Time")
plt.ylabel("EV Presence (offset for clarity)")
plt.title("EV Presence Over Time")
plt.legend(loc="upper right")
plt.tight_layout()
plt.grid(True)
plt.show()



