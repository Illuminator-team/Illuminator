from illuminator.builder import IlluminatorModel, ModelConstructor

class Electrolyzer(ModelConstructor):
    parameters={
            'e_eff' : 70,       # electrolyzer effficiency [%]
            'max_p_in' : 10,    # maximum input power [kW]
            'max_p_ramp_rate' : 10   # maximum rampup power [kW/s]
            
    },
    inputs={
            # 'flow2e' : 0        # power flow to the electrolyzer [kW]
            'desired_out': 30,      # desired output flow of the electrolyzer [kg/h]

    },
    outputs={
            'h_gen' : 0,            # hydrogen generation [kg/timestep]
            'power_consumption' : 0    # power consumption of the electrolyzer [kW]
            # 'water_used' : 0    # water required for H2 prodcution [kg/timestep]
    },
    states={},


    # other attributes
    time=None

    def __init__(self, **kwargs) -> None:
        """
        Initialize the Valve model with the provided parameters.

        Parameters
        ----------
        kwargs : dict
            Additional keyword arguments to initialize the joint model,
            including joint efficiency.
        """
        super().__init__(**kwargs)    
        self.hhv =  286.6                # higher heating value of hydrogen [kJ/mol]
        self.mmh2 = 2.02                 # molar mass hydrogen (H2) [gram/mol]
        self.p_in_last = 0               # the initial power is initialised to 0 [kW]
        self.e_eff = self._model.parameters.get('e_eff') # electrolyzer efficiency [%]
        self.max_p_in = self._model.parameters.get('max_p_in')  # maximum input power [kW]
        self.max_p_ramp_rate = self._model.parameters.get('max_p_ramp_rate')  # maximum ramp up rate [kW/s]
        # self.flow2e = self._model.inputs.get('flow2e', 0)  # Initialize flow2e to 0 if not provided
        self.desired_out = self._model.inputs.get('desired_out', 0)  # Initialize desired_out to 0 if not provided
        


    def step(self, time, inputs, max_advance=1) -> None:
        # get input data 
        input_data = self.unpack_inputs(inputs)
        # flow2e = input_data.get('flow2e', self.flow2e)  # Default to 0 if not provided
        desired_out = input_data.get('desired_out', self.desired_out)  # Default to 0 if not provided

        # calculate generation provided the desired input power [kg/s] 
        # h_flow, residual_power = self.generate(flow2e=flow2e)
        h_flow, power_consumption = self.generate_setpoint(desired_out=desired_out)

        self.set_outputs({
            'h_gen': h_flow, 
            'power_consumption': power_consumption
        })
        
        return time + self._model.time_step_size
    
    def ramp_lim(self, flow2e):

        """
        Limits the input power by the maximimum ramp up limits.

        ...

        Parameters
        ----------
        flow2e : float
            Input power flow [kW]

        Returns
        -------
        power_in : float
            Input power after implemeting ramping limits [kW]
        """
        # restrict the power input to not increase more than max_p_ramp_rate
        # compared to the last timestep
        # TODO: check method of using paramters (self. or .get())

        seconds = self.time_step_size * self.time_resolution  # number of seconds in the timestep is the number of steps times the number of seconds per step

        p_change = flow2e - self.p_in_last
        ramp_limit = self.max_p_ramp_rate * seconds  # ramp limit in [kW] = [kW/s] * [s]

        # CHANGE IN POWER IS LARGER THAN RAMP LIMIT
        if abs(p_change) > ramp_limit:
            if p_change > 0: # ramping up
                power_in = self.p_in_last + self.max_p_ramp_rate * seconds  # [kW] = [kW] + ([kW/s] * [s])
            else: # ramping down
                power_in = self.p_in_last - self.max_p_ramp_rate * seconds

        # CHANGE IN POWER IS WITHIN RAMP LIMIT
        else:
            power_in = flow2e

        self.p_in_last = power_in
        return power_in
        

    def generate(self, flow2e):
        """
        Calculates the hydrogen produced per timestep taking the maximum electric power into account.

        ...

        Parameters
        ----------
        flow2e : float
            Input power flow [kW]
        eff : float
            Electrolyzer efficiency [%]
        hhv : float
            Higher heating value of hydrogen [kJ/mol] 
        mmh2 : float
            Molar mass of hydrogen [g/mol]

        Returns
        -------
        h_out : float
            Output flow of hyrdgen [kg/timestep]
        """        
        # restrict the input power to be maximally max_p_in
        flow2e = min(flow2e, self.max_p_in)
        power_in = self.ramp_lim(flow2e)
        h_out = (power_in*(self.e_eff/100) * self.mmh2) / self.hhv / 1000  # [kg/s]
        h_out = h_out * self.time_resolution  # Convert to kg/timestep (?TODO? times stepssize?)
        residual_power = flow2e - power_in  # residual power that is not used for H2 production [kW]

        return h_out, residual_power

    def kwh_to_kg(self, kwh):
        """
        Converts kWh to kg of hydrogen produced.

        ...

        Parameters
        ----------
        kwh : float
            Energy in kWh

        Returns
        -------
        kg : float
            Hydrogen produced in kg
        """
        energy_density = (self.hhv / self.mmh2) * 1000  # [kJ/kg] = ([kJ/mol] * [mol/g]) * 1000
        kg = (kwh * 3600) * 1/energy_density  # [kg] = (kJh/s * s/h) * [kg/kJ]
        return kg
    

    def kw_to_kg_per_h(self, power_kw: float) -> float:
        """
        Calculate hydrogen production rate (kg/h) from a given power (kW).

        Parameters
        ----------
        power_kw : float
            Electrical power in kilowatts.

        Returns
        -------
        kg_per_h : float
            Hydrogen production rate in kilograms per hour.
        """
        # convert molar mass to kg/mol
        mmh2_kg_per_mol = self.mmh2 / 1000.0

        # energy density in kJ per kg of H₂
        energy_density_kj_per_kg = self.hhv / mmh2_kg_per_mol

        # total energy per hour in kJ: (kW = kJ/s) × 3600 s/h
        kj_per_h = power_kw * 3600.0

        # mass flow = energy flow ÷ energy density
        kg_per_h = kj_per_h / energy_density_kj_per_kg

        return kg_per_h


    def generate_setpoint(self, desired_out):
        """
        Calculates the hydrogen produced per timestep taking the maximum electric power into account.

        ...

        Parameters
        ----------
        desired_out : float
            Desired output flow of hydrogen [kg/h]
        eff : float
            Electrolyzer efficiency [%]
        hhv : float
            Higher heating value of hydrogen [kJ/mol] 
        mmh2 : float
            Molar mass of hydrogen [g/mol]

        Returns
        -------
        h_out : float
            Output flow of hyrdgen [kg/timestep]
        """
        # [kWh] = [kJ/s] * 3600[s] = [kJ]
        # [kg] = [kJ/kg] * 1/[kJ]

        energy_density = 1000 * (self.hhv/self.mmh2)  # [kJ/kg] = 1000 * ([kJ/mol] * [mol/g])
        efficiency = self.e_eff / 100  # Convert efficiency to a fraction
        desired_out = desired_out / 3600  # Convert desired output from [kg/h] to [kg/s]

        power_needed = energy_density * desired_out / efficiency # [kW] = [kJ/s] = [kJ/kg] * [kg/s]

        # restrict the input power to be maximum input power
        flow2e = min(power_needed, self.max_p_in) # [kW]

        # restrict the input power to not increase more than max_p_ramp_rate
        power_in = self.ramp_lim(flow2e) # [kW]

        # calculate the hydrogen output based on the input power
        h_out = power_in * 1/energy_density * efficiency  # [kg/s] = [kJ/s] * [kg/kJ]

        # convert the output to kg/timestep
        h_out = h_out * self.time_step_size*self.time_resolution  # [kg/timestep] = [kg/s] * [s/timestep]
        power_consumption = power_in * self.time_step_size * self.time_resolution * 1/3600  # [kWh/timestep] = [kw] * [s/timestep] * [h/s]

        return h_out, power_consumption