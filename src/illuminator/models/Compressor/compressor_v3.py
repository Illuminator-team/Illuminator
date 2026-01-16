from illuminator.builder import ModelConstructor

class Compressor(ModelConstructor):
    """
    A class to represent a Compressor model.
    This class provides methods to simulate the compression of hydrogen gas.

    Attributes
    ----------
    parameters : dict
        Dictionary containing compressor parameters such as input pressure, output pressure, ambient temperature, and compressor efficiency.
    inputs : dict
        Dictionary containing input variables like hydrogen flow to the compressor.
    outputs : dict
        Dictionary containing calculated outputs like hydrogen flow from the compressor, power required for compression, and volumetric output flow.
    states : dict
        Dictionary containing the state variables of the compressor model.
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
    max_power_in : float
        the maximum input power of the compressor [kW]
        

    Methods
    -------
    step(time, inputs, max_advance=900)
        Simulates one time step of the compressor model.
    power_req(flow, p_in, p_out, T_amb, max_advance)
        Calculates the power required to compress the hydrogen and limits the output flow and power based on this required power.
    new_density(p, T)
        Calculates the new density of hydrogen after compression.
    find_z_val(press, temp)
        Finds the Z value needed to compute the new density.
    """
    parameters={
            'p_in' : 30,            # input pressure [bar]
            'p_out' : 500,          # output pressure [bar]
            'T_amb' : 293.15,       # ambient temperature [K]
            'compressor_eff': 99,   # compressor efficiency [%]
            'max_power_in' : 10     # maximum power input [kW]
    },
    inputs={
            'flow2c' : 0            # hydrogen flow to the compressor [kg/timestep]

    },
    outputs={
            'flow_from_c' : 0       # hydrogen flow from the compressor [kg/timestep]

    },
    states={'power_req' : 0,        # power required for the compression [kW]
            'volume_flow_out' : 0   # volumetric output flow [m3/timestep]
            }

    # other attributes
    time_step_size=1
    time = None
    hhv =  286.6                # higher heating value of hydrogen [kJ/mol]
    mmh2 = 2.02                 # molar mass hydrogen (H2) [gram/mol]
    R = 8.314                   # characteristic gas constant [J/mol*K]
    gamma = 1.41                # specific heat ratio [-]
    e_grav_h2 = 120e6           # gravimetric energy density of hydrogen [J/kg]

    def __init__(self, **kwargs) -> None:
        """
        Initialize the Compressor model with the provided parameters.

        Parameters
        ----------
        kwargs : dict
            Additional keyword arguments to initialize the model.
        """
        super().__init__(**kwargs)
        self.p_in = self._model.parameters.get('p_in')
        self.p_out = self._model.parameters.get('p_out')
        self.T_amb = self._model.parameters.get('T_amb')
        self.compressor_eff = self._model.parameters.get('compressor_eff')
        self.max_power_in = self._model.parameters.get('max_power_in')

    def step(self, time:int, inputs:dict=None, max_advance:int=900) -> None:
        """
        Simulates one time step of the compressor model.

        This method processes the inputs for one timestep, updates the compressor state based on
        the hydrogen flow, and sets the model outputs accordingly.

        Parameters
        ----------
        time : int
            Current simulation time
        inputs : dict
            Dictionary containing input values, specifically:
            - flow2c: Hydrogen flow to the compressor in kg/timestep
        max_advance : int, optional
            Maximum time step size (default 1)

        Returns
        -------
        int
            Next simulation time step
        """
        
        # get input data
        input_data = self.unpack_inputs(inputs)


        current_time = time * self.time_resolution


        # calculate power required to compress the hydrogen from one pressure to another [kW] 
        power_params = self.power_req(flow=input_data['flow2c'],
                                   p_in=self.p_in,
                                   p_out=self.p_out,
                                   T_amb=self.T_amb
                                    )
        volume_flow_out = input_data['flow2c'] / self.new_density(p=self.p_out, T=self.T_amb)
        self.set_outputs({'flow_from_c': power_params['output_flow']})
        self.set_states({'power_req': power_params['power_req']})
        self.set_states({'volume_flow_out': volume_flow_out})
        # self._model.outputs['flow_from_c'] = input_data['flow2c']
        # self._model.outputs['power_req'] = power_req
        # self._model.outputs['volume_flow_out'] = volume_flow_out


        return time + self._model.time_step_size

    def power_req(self, flow: float, p_in: float, p_out: float, T_amb: float) -> dict:
        """
        Calculates the power required to compress the hydrogen and limits the output flow and power based on this required power.

        ...

        Parameters
        ----------
        flow : float
            Hydrogen flow to the compressor [kg/timestep]
        p_in : float
            Input pressure [bar]
        p_out : float
            Output pressure [bar]
        T_amb : float
            Ambient temperature [K]

        Returns
        -------
        power_in : float
            Power required for compression [kW]
        """
        # calculates the power required to compress the hydrogen in the compressor
        w_isentropic = (self.gamma / (self.gamma - 1)) * self.R * T_amb * ((p_out / p_in) ** ((self.gamma - 1) / self.gamma) - 1) # [J/mol]
        w_real = w_isentropic / (self.compressor_eff / 100)
        flow_ps = flow / self.time_resolution   # input hydrogen per second [kg/s]
        power_in = w_real * flow_ps / self.mmh2    # [kW]
        output_flow = flow
        # take max power input into consideration
        if power_in > self.max_power_in:
            power_in = self.max_power_in                                    # power is limited by its upper bound
            output_flow = power_in * self.mmh2 / w_real * self.time_resolution     # The output flow is now limited by the power
        power_params = {'power_req' : power_in,
                        'output_flow' : output_flow}
        return power_params

    def new_density(self, p: float, T: float) -> float:
        """
        Calculates and outputs the new density of h2 after compression

        ...

        Parameters
        ----------
        p : float
            Output pressure [bar]
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
        Finds the Z value needed to compute the new density.

        ...

        Parameters
        ----------
        press : float
            Compressor output pressure [bar]
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
    