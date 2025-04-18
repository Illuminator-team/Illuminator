
# Online Python - IDE, Editor, Compiler, Interpreter
import numpy as np
import matplotlib.pyplot as plt 
from scipy.optimize import fsolve

def new_density(p: float, T: float) -> float:
    z_val = find_z_val(p, T)
    density = ((p* 1e5) * (mmh2 /1e3))/(z_val * R * T) #  kg/m3
    return density

def find_z_val(press: float, temp: float) -> float:

    z_values = [
        [1.00070, 1.00004, 1.0006, 1.00055, 1.00047, 1.00041, 1.00041],
        [1.00337, 1.00319, 1.00304, 1.00270, 1.00241, 1.00219, 1.00196],
        [1.00672, 1.00643, 1.00605, 1.00540, 1.00484, 1.00435, 1.00395],
        [1.03387, 1.03235, 1.03037, 1.02701, 1.02411, 1.02159, 1.01957],
        [1.06879, 1.06520, 1.06127, 1.05369, 1.04807, 1.04314, 1.03921],
        [1.10404, 1.09795, 1.09189, 1.08070, 1.07200, 1.06523, 1.05936],
        [1.14056, 1.13177, 1.12320, 1.10814, 1.09631, 1.08625, 1.07849],
        [1.17789, 1.16617, 1.15499, 1.13543, 1.12034, 1.10793, 1.08764],
        [121592, 1.20101, 1.18716, 1.16300, 1.14456, 1.12957, 1.11699],
        [1.25461, 1.23652, 1.21936, 1.19051, 1.16877, 1.15112, 1.13648], 
        [1.29379, 1.27220, 1.25205, 1.21842, 1.19317, 1.17267, 1.15588],
        [1.33332, 1.30820, 1.28487, 1.24634, 1.19439, 1.17533, 121739],
        [137284, 1.34392, 1.31784, 1.27398, 1.24173, 1.21583, 1.19463],
        [1.45188, 1.41618, 1.38797, 1.33010, 1.29040, 1.2592, 1.23373],
        [133161, 1.48880, 1.44991, 1.38593, 1.33914, 1.30236, 1.27226]]

    temps = [250, 273.15, 298.15, 350, 400, 450, 500]   # columns 
    pressures = [1, 5, 10, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 600, 700]   # rows

    # read out table by choosing the best matching pressure/temperature combination
    closest_temp = min(temps, key=lambda t: abs(t - temp))
    closest_pressure = min(pressures, key=lambda p: abs(p - press))
    z_val = z_values[pressures.index(closest_pressure)][temps.index(closest_temp)]
    return z_val


mmh2 = 2.02                 # molar mass hydrogen (H2) [gram/mol]
R = 8.314                   # characteristic gas constant [J/mol*K]
T= 300
densities_Z = []
densities = []
densities_D = []
P_bar = np.linspace(1, 500, 500)  # 1 to 100 bar
a = 0.2476 / (1000**2)  # [Pa·m^6/mol^2]
b = 0.0266 / 1000       # [m³/mol]

P = 270e5  # Pressure [Pa]
V = (50*53) / 1000  # Volume [m³]
n = (P*V)/(R*T)         # [mol]
m = n*mmh2/1000            # mass [kg]

# Van der Waals Equation
def vdw(n, P, V, T):
    return (P+(a/n**2))*(V-n*b) - n*R*T


for pressure in P_bar:
    densities_Z.append(new_density(pressure, T))
    pressure = pressure * 1e5
    
    n2 = fsolve(vdw, n, args=(pressure,V,T))[0]
    m2 = (n2*mmh2)/1000 # store mass for vdw
    
    densities.append((pressure * mmh2/1000) / (R * T))
    densities_D.append(m2/V)

# Plot
plt.figure(figsize=(8, 5))
plt.plot(P_bar, densities_Z, label='with Z val', color='green')
plt.plot(P_bar, densities, label='without Z val', color='red' )
plt.plot(P_bar, densities_D, label="Daan's formula", color='yellow')
plt.xlabel('Pressure (bar)')
plt.ylabel('Density (kg/m³)')
plt.title('Density of Hydrogen vs Pressure (Ideal Gas Law with Z val)')
plt.legend()
plt.grid()
plt.show()
    

