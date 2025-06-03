from illuminator.builder import ModelConstructor

class Thermolyzer(ModelConstructor):
    """
    Thermolyzer model class for simulating a thermolyzer that converts biomass and electricity 
    into hydrogen.

    Parameters
    ----------
    eff : float
        Thermolyzer efficiency as a percentage [%]
    C_bio_h2 : float
        Conversion factor from biomass to hydrogen [-]
    CO_2 : float
        Absorption factor carbondioxide per h2 produced [-]
    C_Eelec_h2 : float
        Conversion factor electrical energy to hydrogen mass [kWh/kg]
    max_ramp_up : float
        Maximum ramp up in power per timestep [kW/timestep]
    max_p_in : float
        Maximum input power [kW]

    Returns
    -------
    None
    """
    parameters={
            'eff' : 60,             # thermolyzer effficiency [%]  
            'C_bio_h2' : 30,        # conversion factor from biomass to hydrogen [kg/kg] 
            'C_CO_2' : 10,          # absorption factor carbondioxide per h2 produced [kg/kg] 
            'C_Eelec_h2': 11.5,     # conversion factor electrical energy to hydrogen mass [kWh/kg]    
            'max_ramp_up' : 60,     # maximum ramp up in power per timestep [kW/timestep]  
            'max_p_in' : 10000        # maximum input power [kW]
            },
    inputs={
            'biomass_in' : 0,       # biomass input [kg/timestep]
            'flow2t' : 2300         # power input to the thermolyzer [kW]
            # 'water_in' : 0        # water input to the thermolzyer [L/timestep]
            },
    outputs={
            'h_gen' : 0,            # hydrogen generation [kg/timestep]
            'CO2_out' : 0           # CO2 output [kg/timestep]
            },
    states={}

    # other attributes
    time_step_size=1
    time=None
    hhv =  286.6                # higher heating value of hydrogen [kJ/mol]
    mmh2 = 2.02                 # molar mass hydrogen (H2) [gram/mol]


    def __init__(self, **kwargs):
        """
        Initialize the thermolyzer model with specified parameters.

        This method initializes a new thermolyzer instance with given parameters, setting up
        initial values for efficiency, conversion factors, ramp limits, and other operational
        parameters.

        Parameters
        ----------
        kwargs : dict
            Dictionary containing model parameters including:
            - eff: Thermolyzer efficiency as a percentage [%]
            - C_bio_h2: Conversion factor from biomass to hydrogen [-]
            - C_CO_2: Absorption factor carbondioxide per h2 produced [-]
            - C_Eelec_h2: Conversion factor electrical energy to hydrogen mass [kWh/kg]
            - max_ramp_up: Maximum ramp up in power per timestep [kW/timestep]
            - max_p_in: Maximum input power [kW]

        Returns
        -------
        None
        """
        super().__init__(**kwargs)
        self.eff = self._model.parameters.get('eff')
        self.C_bio_h2 = self._model.parameters.get('C_bio_h2')
        self.C_CO_2 = self._model.parameters.get('C_CO_2')
        self.C_Eelec_h2 = self._model.parameters.get('C_Eelec_h2')
        self.max_ramp_up = self._model.parameters.get('max_ramp_up')
        self.max_p_in = self._model.parameters.get('max_p_in')
        self.biomass_in = self._model.inputs.get('biomass_in', 0)  # Initialize biomass input to 0 if not provided
        self.flow2t = self._model.inputs.get('flow2t', 0)  # Initialize power input to 0 if not provided
        print("DEBUG: THIS IS PARAMTERS:", self._model.parameters)
        
        self.p_in_last = 0  # Indicator of the last power input initialized to be 0 

    def step(self, time: int, inputs: dict=None, max_advance: int=900) -> None:
        """
        Process one simulation step of the thermolyzer model.

        This method processes the inputs for one timestep and sets the model outputs and states
        accordingly.

        Parameters
        ----------
        time : int
            Current simulation time
        inputs : dict
            Dictionary containing input values, specifically:
            - biomass_in: Biomass input in kg/timestep
            - flow2t: Power input to the thermolyzer in kW
        max_advance : int, optional
            Maximum time step size in seconds (default 900)

        Returns
        -------
        int
            Next simulation time step
        """
        print("\nThermolyzer:")
        print("inputs (passed): ", inputs)
        print("inputs (internal): ", self._model.inputs)
        # get input data 
        input_data = self.unpack_inputs(inputs)
        self.biomass_in = input_data.get('biomass_in', self.biomass_in)  # Default to last value if not provided (most likely the initial value)
        self.flow2t = input_data.get('flow2t', self.flow2t)  # Default to last value if not provided (most likely the initial value)
        print("input data: ", input_data)

        current_time = time * self.time_resolution
        print('from Thermolyzer %%%%%%%%%%%', current_time)

        h_flow = self.generate(
            m_bio=self.biomass_in,
            flow2t=self.flow2t,
            max_advance = max_advance
            )
        h_gen = h_flow
        CO2_out = -h_gen * self.C_CO_2
        self.set_outputs({'h_gen': h_gen})
        self.set_outputs({'CO2_out': CO2_out})
        print("outputs:", self.outputs)
        return time + self._model.time_step_size
    
    def ramp_lim(self, p_in: float, max_advance: int) -> float:
        """
        Limits the thermolyzer input power based on ramp rate constraints.

        ...

        Parameters
        ----------
        p_in : float
            Desired power input to the thermolyzer [kW]
        max_advance : int
            Maximum time step size in seconds

        Returns
        -------
        float
            Adjusted power input after applying ramp rate constraints [kW]
        """
        # restrict the power input to not increase more than max_p_ramp_rate
        # compared to the last timestep
        p_change = p_in - self.p_in_last
        if abs(p_change) > self.max_ramp_up:
            if p_change > 0:
                print("DEBUG: p_change > 0")
                power_in = self.p_in_last + self.max_ramp_up
            else:
                print("DEBUG: p_change < 0")
                power_in = self.p_in_last - self.max_ramp_up
        else:
            print("DEBUG: p_change = max_ramp_up")
            power_in = p_in
        self.p_in_last = power_in
        return power_in
        

    def generate(self, m_bio: float, flow2t: float, max_advance: int = 900) -> float:
        """
        Generate hydrogen based on biomass and power input.

        This method calculates the hydrogen production based on the available biomass and 
        electrical power input, considering the efficiency and ramp rate constraints.

        Parameters
        ----------
        m_bio : float
            Biomass input in kg/timestep
        flow2t : float
            Power input to the thermolyzer in kW
        max_advance : int, optional
            Maximum time step size in seconds (default 900)

        Returns
        -------
        float
            Hydrogen production in kg/timestep
        """
        # TODO: add water dependency once the conversion factor is known
        # restrict the input power to be maximally max_p_in
        power_in = min(flow2t, self.max_p_in)
        # restrict input power with ramp limits
        power_in = self.ramp_lim(power_in, max_advance)
        # print("DEBUG:\n power_in after ramp", power_in)
        power_in = power_in * (self.eff / 100)
        # print("DEBUG:\n power_in after eff", power_in)
        # the production of hyrdogen is dependent on both the available biomass mass and the input power. Therfor:
        # calculate potential generation of h2 for both dependencies
        h_prod_p = power_in / self.C_Eelec_h2 / 3600 * self.time_resolution     # [kg/timestep]
        h_prod_m = m_bio / self.C_bio_h2                                        # [kg/timestep]
        print("DEBUG:\n h_prod_p:", h_prod_p, "\n h_prod_m:", h_prod_m)
        h_out = min(h_prod_p, h_prod_m)
        return h_out