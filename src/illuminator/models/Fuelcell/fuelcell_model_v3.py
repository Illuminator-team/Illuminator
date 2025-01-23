from illuminator.builder import ModelConstructor

class Fuelcell(ModelConstructor):
    """
    A class to represent a Fuelcell model.
    This class provides methods to simulate the operation of a fuelcell.

    Attributes
    ----------
    parameters : dict
        Dictionary containing fuelcell parameters such as efficiency, maximum hydrogen input flow, and minimum hydrogen input flow.
    inputs : dict
        Dictionary containing input variables like hydrogen flow to the fuelcell.
    outputs : dict
        Dictionary containing calculated outputs like power output.
    states : dict
        Dictionary containing the state variables of the fuelcell model.
    time_step_size : int
        Time step size for the simulation.
    time : int or None
        Current simulation time.
    hhv : float
        Higher heating value of hydrogen [kJ/mol].
    mmh2 : float
        Molar mass of hydrogen (H2) [gram/mol].

    Methods
    -------
    step(time, inputs, max_advance=900)
        Simulates one time step of the fuelcell model.
    power_out(h2_flow2f)
        Calculates the power output of the fuelcell.
    """
    parameters={
            'fuelcell_eff': 99,     # fuelcell efficiency [%]
            'h2_max' : 10,          # max hyrogen input flow [kg/timestep]  
            'h2_min' : 0,           # min hydrogen input flow [kg/timestep]
            'max_p_out' : 1,        # maximum power output [kW]
            'max_ramp_up' : 10      # maximum ramp up in power per timestep [kW/timestep] 
    },
    inputs={
            'h2_flow2f' : 0         # hydrogen flow to the fuelcell [kg/timestep]
    },
    outputs={
            'p_out' : 0             # power output [kW]
    },
    states={},

    # other attributes
    time_step_size=1,
    time=None
    hhv =  286.6                # higher heating value of hydrogen [kJ/mol]
    mmh2 = 2.02                 # molar mass hydrogen (H2) [g/mol]
 
    def __init__(self, **kwargs) -> None:
        """
        Initialize the Fuelcell model with the provided parameters.

        Parameters
        ----------
        kwargs : dict
            Additional keyword arguments to initialize the model.
        """
        super().__init__(**kwargs)
        self.fuelcell_eff = self._model.parameters.get('fuelcell_eff')
        self.h2_max = self._model.parameters.get('h2_max')
        self.h2_min = self._model.parameters.get('h2_min')
        self.max_ramp_up = self._model.parameters.get('max_ramp_up')
        self.max_p_out = self._model.parameters.get('max_p_out')
        self.p_in_last = 0  # Indicator of the last power input initialized to be 0 

    def step(self, time: int, inputs: dict=None, max_advance: int = 900) -> None:
        """
        Simulates one time step of the fuelcell model.

        This method processes the inputs for one timestep, updates the fuelcell state based on
        the hydrogen flow, and sets the model outputs accordingly.

        Parameters
        ----------
        time : int
            Current simulation time
        inputs : dict
            Dictionary containing input values, specifically:
            - h2_flow2f: Hydrogen flow to the fuelcell in kg/timestep
        max_advance : int, optional
            Maximum time step size (default 900)

        Returns
        -------
        int
            Next simulation time step
        """

        print("\nFuelcell:")
        print("inputs (passed): ", inputs)
        print("inputs (internal): ", self._model.inputs)
        # get input data 
        input_data = self.unpack_inputs(inputs)
        print("input data: ", input_data)
        current_time = time * self.time_resolution
        print('from fuelcell %%%%%%%%%%%', current_time)
        self._model.outputs['p_out'] = self.power_out(input_data['h2_flow2f'], max_advance)
        print("outputs:", self.outputs)
        
        return time + self._model.time_step_size
        
    def power_out(self, h2_flow2f: float, max_advance: int) -> float:
        """
        Calculates the output power of the fuelcell

        ...

        Parameters
        ----------
        h2_flow2f : float
            H2 flow into the fuelcell [kg/timestep]

        Returns
        -------
        p_out : float
            The outout power of the fuelcell [kW]
        """
        # limit hydrogen consumption by the minimum and maximum hydrogen the fuelcell can accept
        h2_flow = max(self.h2_min, min(self.h2_max, h2_flow2f))         # [kg/timestep]
        h2_flow = h2_flow / max_advance                                 # [kg/s]
        p_out = (h2_flow * self.fuelcell_eff * self.hhv) / self.mmh2    # [kW]
        p_out = min(p_out, self.max_p_out)                               # limit power output by the max power output [kW]
        p_out = self.ramp_lim(p_out, max_advance)                       # considering ramp limits [kW]
        return p_out

    def ramp_lim(self, p_out, max_advance):
        """
        Limits the power output ramp rate of the fuelcell.

        ...

        Parameters
        ----------
        p_out : float
            Desired power output [kW]
        max_advance : int
            Maximum time step size

        Returns
        -------
        power_out : float
            Adjusted power output [kW] after applying ramp rate limits
        """
        # restrict the power input to not increase more than max_p_ramp_rate
        # compared to the last timestep
        p_change = p_out - self.p_in_last
        if abs(p_change) > self.max_ramp_up:
            if p_change > 0:
                power_out = self.p_in_last + self.max_ramp_up * max_advance
            else:
                power_out = self.p_in_last - self.max_ramp_up * max_advance
        else:
            power_out = p_out
        self.p_in_last = power_out
        return power_out