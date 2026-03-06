from illuminator.builder import ModelConstructor
import numpy as np

class Pipeline(ModelConstructor):
    """
    A class to represent a Pipeline model.
    This class provides methods to simulate the flow of hydrogen gas through a pipeline.

    Attributes
    ----------
    parameters : dict
        Dictionary containing pipeline parameters such as cross-sectional area, input pressure, ambient temperature, pipe thickness, and pipe roughness.
    inputs : dict
        Dictionary containing input variables like hydrogen flow into the pipeline and input pressure.
    outputs : dict
        Dictionary containing calculated outputs like hydrogen flow out of the pipeline and output pressure.
    states : dict
        Dictionary containing the state variables of the pipeline model.
    time_step_size : int
        Time step size for the simulation.
    time : int or None
        Current simulation time.
    hhv : float
        Higher heating value of hydrogen [kJ/mol].
    mmh2 : float
        Molar mass of hydrogen (H2) [gram/mol].
    R : float
        Characteristic gas constant [J/mol*K].
    gamma : float
        Specific heat ratio [-].
    e_grav_h2 : float
        Gravimetric energy density of hydrogen [J/kg].

    Methods
    -------
    step(time, inputs, max_advance=1)
        Simulates one time step of the pipeline model.
    output_flow(flow_in, density)
        Calculates the output flow (mass) given the properties of the pipeline and hydrogen.
    permeabilty_coef(press)
        Reads the permeability coefficient of hydrogen in HDPE pipes from a table, provided the pressure of the hydrogen.
    density(p, T)
        Calculates and outputs the density of hydrogen provided pressure and temperature.
    find_z_val(press, temp)
        Finds the Z value needed to compute the density.
    output_pressure(flow_in, density)
        Calculates the output pressure given the properties of the pipeline and hydrogen.
    viscosity(T)
        Reads the viscosity of hydrogen from a table provided the temperature.
    """
    parameters={
            'A' : 2,                # cross-sectional area of the pipe [m2]
            'L' : 100,              # length of the pipe [m]
            # 'p' : 300,              # input pressure of the hydrogen [bar]        # NOTE: Moved to inputs
            'p_outer':1,            # pressure outside of the pipe [bar]
            'T_amb' : 293.15,       # ambient temperature [K]
            'd' : 0.01,             # pipe thickness [m]
            'eps' : 1.5e-6          # pipe roughness [m]

    },
    inputs={
            'flow_in' : 0,          # hydrogen flow to into the pipeline [kg/timestep]
            'pressure_in' : 0       # input pressure of the hydrogen

    },
    outputs={
            'flow_out' : 0          # hydrogen flow out of the pipeline [kg/timestep]
            },
    states={'press_out' : 0         # output pressure of the hydrogen [bar]
            }


    # other attributes
    time_step_size=1
    time=None
    hhv =  286.6                # higher heating value of hydrogen [kJ/mol]
    mmh2 = 2.02                 # molar mass hydrogen (H2) [gram/mol]
    R = 8.314                   # characteristic gas constant [J/mol*K]
    gamma = 1.41                # specific heat ratio [-]
    e_grav_h2 = 120e6           # gravimetric energy density of hydrogen [J/kg]
    
    def __init__(self, **kwargs) -> None:
        """
        Initialize the Pipeline model with the provided parameters.

        Parameters
        ----------
        kwargs : dict
            Additional keyword arguments to initialize the model.
        """
        super().__init__(**kwargs)
        self.A = self._model.parameters.get('A')
        self.L = self._model.parameters.get('L')
        # self.p = self._model.parameters.get('p')
        self.p_outer = self._model.parameters.get('p_outer')
        self.T_amb = self._model.parameters.get('T_amb')
        self.d = self._model.parameters.get('d')
        self.eps = self._model.parameters.get('eps')
        self.radius = np.sqrt(self.A / np.pi)       # Inner radius of the pipe [m]

    def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> int:
        """
        Simulates one time step of the pipeline model.

        This method processes the inputs for one timestep, updates the pipeline state based on
        the hydrogen flow, and sets the model outputs accordingly.

        Parameters
        ----------
        time : int
            Current simulation time
        inputs : dict
            Dictionary containing input values, specifically:
            - flow_in: Hydrogen flow into the pipeline in kg/timestep
            - pressure_in: Input pressure of the hydrogen in bar
        max_advance : int, optional
            Maximum time step size (default 900)

        Returns
        -------
        int
            Next simulation time step
        """
        print("\nPipeline:")
        print("inputs (passed): ", inputs)
        print("inputs (internal): ", self._model.inputs)
        # get input data push test
        input_data = self.unpack_inputs(inputs)
        print("input data: ", input_data)

        current_time = time * self.time_resolution
        print('from pipeline %%%%%%%%%%%', current_time)

        # calculate power required to compress the hydrogen from one pressure to another [kW] 
        
        density = self.density(input_data['pressure_in'], self.T_amb)          # [kg/m3]
        output_flow = self.output_flow(input_data['flow_in'], density, input_data['pressure_in'])
        p_out = self.output_pressure(input_data['flow_in'], density, input_data['pressure_in'])
        print(f"DEBUG: this is p_out in step: {p_out}")
        self.set_outputs({'flow_out' : output_flow})
        self.set_states({'press_out' : p_out})
        print("outputs:", self.outputs)
        return time + self._model.time_step_size
    
    def output_flow(self, flow_in: float, density: float, pressure_in: float) -> float:
        """
        Calculates the output flow (mass) given the properties of the pipeline and hydrogen.

        ...

        Parameters
        ----------
        flow_in : float
            Input flow [kg/timestep]
        density : float
            density of the hydrogen [kg/m3]

        Returns
        -------
        flow_out : float
            Input flow [kg/timestep]
        """
        P = self.permeabilty_coef(pressure_in) # [cm3*cm/cm2*s*Pa]
        surf_area = self.L * 2 * np.pi * self.radius    # inner surface area of the pipe [m^2]
        flow_loss_vol= (P * 1e-4 * surf_area * (abs(pressure_in - self.p_outer) * 1e5)) / (self.d)    # [m^3/s]
        flow_loss_mass = flow_loss_vol * density     # [kg/s]
        output_flow = flow_in - flow_loss_mass * self.time_resolution   # [kg/timestep]
        return output_flow
    
    def permeabilty_coef(self, press: float) -> float:
        """
        Reads the permeability coefficient of hydrogen in HDPE pipes from a table, provided the pressure of the hydrogen.
        ...

        Parameters
        ----------
        p : float
            Pressure of the hydrogen [bar]

        Returns
        -------
        P : float
            Permeability coefficient of hydrogen in HDPE pipe [cm3*cm/cm2*s*Pa]
        """
        press = press * 1e5     # convert bar to Pascall [Pa]
        coefs = [2.07e-12, 1.8e-12, 1.515e-12, 1.32e-12, 1.1025e-12]   # list of permeability coefficients [cm3*cm/cm2*s*Pa]
        pressures = [10e5, 30e5, 50e5, 70e5, 90e5]              # corresponding pressures [Pa]
        closest_pressure = closest_pressure = min(pressures, key=lambda p: abs(p - press))  # Best matching pressure [Pa]
        P = coefs[pressures.index(closest_pressure)]            # Best matching permeability coefficient [cm3*cm/cm2*s*Pa]        
        return P

    def density(self, p: float, T: float) -> float:
        """
        Calculates and outputs the density of h2 provided pressure and temperature

        ...

        Parameters
        ----------
        p : float
            Pressure [bar]
        T : float
            Temperature of operation [K]

        Returns
        -------
        density : float
            The new found density after compression [kg/m3]
        """
        z_val = self.find_z_val(p, T)
        density = ((p* 1e5) * (self.mmh2 /1e3))/(z_val * self.R * T) #  kg/m3
        
        return density

    def find_z_val(self, press: float, temp: float) -> float:
        """
        Finds the Z value needed to compute the density.

        ...

        Parameters
        ----------
        press : float
            Compressor utput pressure [bar]
        temp : float
            Temperature of operation [K]

        Returns
        -------
        z_val : float
            The Z value that best matches the given pressure and temperature
        """
        # table with Z-values. rows represent pressure, columns represent temperature
        z_values = [
            [1.00070, 1.00004, 1.0006, 1.00055, 1.00047, 1.00041, 1.00041],
            [1.00337, 1.00319, 1.00304, 1.00270, 1.00241, 1.00219, 1.00196],
            [1.00672, 1.00643, 1.00605, 1.00540, 1.00484, 1.00435, 1.00395],
            [1.03387, 1.03235, 1.03037, 1.02701, 1.02411, 1.02159, 1.01957],
            [1.06879, 1.06520, 1.06127, 1.05369, 1.04807, 1.04314, 1.03921],
            [1.10404, 1.09795, 1.09189, 1.08070, 1.07200, 1.06523, 1.05936],
            [1.14056, 1.13177, 1.12320, 1.10814, 1.09631, 1.08625, 1.07849],
            [1.17789, 1.16617, 1.15499, 1.13543, 1.12034, 1.10793, 1.08764],
            [1.21592, 1.20101, 1.18716, 1.16300, 1.14456, 1.12957, 1.11699],
            [1.25461, 1.23652, 1.21936, 1.19051, 1.16877, 1.15112, 1.13648], 
            [1.29379, 1.27220, 1.25205, 1.21842, 1.19317, 1.17267, 1.15588],
            [1.33332, 1.30820, 1.28487, 1.24634, 1.19439, 1.17533, 1,1739],
            [137284, 1.34392, 1.31784, 1.27398, 1.24173, 1.21583, 1.19463],
            [1.45188, 1.41618, 1.38797, 1.33010, 1.29040, 1.2592, 1.23373],
            [1.53161, 1.48880, 1.44991, 1.38593, 1.33914, 1.30236, 1.27226]]

        temps = [250, 273.15, 298.15, 350, 400, 450, 500]   # columns 
        pressures = [1, 5, 10, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 600, 700]   # rows

        # read out table by choosing the best matching pressure/temperature combination
        closest_temp = min(temps, key=lambda t: abs(t - temp))
        closest_pressure = min(pressures, key=lambda p: abs(p - press))
        z_val = z_values[pressures.index(closest_pressure)][temps.index(closest_temp)]
        return z_val
    
    def output_pressure(self, flow_in: float, density: float, pressure_in: float) -> float:
        """
        Calculates the output pressure [bar] given the properties of the pipeline and hydrogen.

        ...

        Parameters
        ----------
        flow_in : float
            Input flow [kg/timestep]

        Returns
        -------
        p_out : float
            Output pressure [bar]
        """
        vol_flow_in = flow_in / density     # volume flow in [m3/timestep]
        print(f"DEBUG: This is the density in the press function {density}")
        print(f"DEBUG: this is the vol flow in the press funtion: {vol_flow_in} = {vol_flow_in/self.time_resolution} m3/s")     
        p = pressure_in * 1e5                    # pressure in pascals [Pa]
        mu = self.viscosity(self.T_amb)     # viscosity of hydrogen (temperature dependent) [Pa*s]
        print(f"DEBUG: this is the viscosity in the press funtion: {mu}")
        D = 2 * np.sqrt(self.A / np.pi)     # pipe diameter [m]
        print(f"DEBUG: This is diameter: {D}")
        v = vol_flow_in / self.A /self.time_resolution  # mean velocity of the flow [m/s]
        print(f"DEBUG: this is the mean flow in the press funtion: {v} m/s")
        Re = (density * v * D) / mu # Reynolds number [-]
        print(f"DEBUG: tyhis is Reynolds number: {Re}")
        # Friction factor dependent on laminar or turbulent flow
        if Re <= 2300:
            f = 64 / Re
        else:
            print(f"DEBUG: ITS TURBULENT FLOW!")
            f = (-1.8 * np.log10((self.eps / (3.7 * D)) ** 1.11 + (6.9 / Re))) ** -2   
        print(f"DEBUG: this is friction factor: {f}")   
        p_loss = f * (self.L * density * v**2) / (2 * D)     # pressure loss [bar]
        p_loss = p_loss / 1e5       # pressure loss conversion to bar [bar]
        print(f"DEBUG: This is p_losss in the press function: {p_loss}")
        p_out = pressure_in - p_loss          # output pressure [bar]
        return p_out

    def viscosity(self, T: float) -> float:
        """
        Reads the viscosity of hydrogen from a table provided the temperature.
        ...

        Parameters
        ----------
        T : float
            Temperature [K]

        Returns
        -------
        mu : float
            Visosity of hydrogen [Pa s]
        """
        temps = [273.15, 293.15, 323.15, 373.15, 473.15, 573.15, 673.15, 773.15, 873.15] 
        visc = [0.84e-5, 0.88e-5, 0.94e-5, 1.04e-5, 1.21e-5, 1.37e-5, 1.53e-5, 1.69e-5, 1.84e-5]

        # # Sutherland's formula method
        # T_0 = 293.15             # reference temperature
        # visc_0 = 0.88e-5        # Reference viscosisty
        # S = 72                  # Sutherland's coefficient
        # viscosity = visc_0 * (T / T_0) ** 3/2 * (T_0 + S) / (T + S)


        closest_temp = min(temps, key=lambda t: abs(t - T))
        viscosity = visc[temps.index(closest_temp)]
        return viscosity

