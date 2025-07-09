from illuminator.builder import IlluminatorModel, ModelConstructor
from numpy import inf
# from illuminator.models import Electrolyzer
# from illuminator.models import H2Buffer

class ZZE(ModelConstructor):
    parameters={
        ## buffer part ##
        'h2_soc_min': 0,            # Minimum state of charge of the hydrogen buffer before discharging stops [%]
        'h2_soc_max': 100,          # Maximum state of charge of the hydrogen buffer before charging stops [%]
        'h2_charge_eff': 100,       # Charge efficiency of the H2 buffer [%]
        'h2_discharge_eff': 100,    # Discharge efficiency of the H2 buffer [%]
        'max_flow_rate_in': 10,               # maximal flow in [kg/h]
        'min_flow_rate_in': 0,               # minimal flow in [kg/h]
        'max_flow_rate_out': 10,               # maximal flow out [kg/h]
        'min_flow_rate_out': 0,               # minimal flow out [kg/h]
        'h2_capacity_tot': 100,      # total capacity of the hydrogen buffer [kg]

        ## electrolyzer part ##
        'e_eff' : 70,       # electrolyzer effficiency [%]
        'max_p_in' : 10,    # maximum input power [kW]
        'max_p_ramp_rate' : 10   # maximum rampup power [kW/s]
            
    }
    inputs={
        ## buffer part ##
        'h2_in': 0,            # input to H2 buffer [kg/timestep]
        'desired_out': 0,   # demanded hydrogen output flow [kg/h]

        ## electrolyzer part ##
        # 'flow2e' : 0        # power flow to the electrolyzer [kW]
        'desired_out': 30,      # desired output flow of the electrolyzer [kg/h]
            

    }
    outputs={
        'h2_out': 0,       # flow out of the H2 buffer [kg/timestep]
        'actual_h2_in': 0,  # The input that is processed in the buffer [kg/timestep]
        'overflow': 0,  # Overflow of the buffer [kg/timestep]

        ## electrolyzer part ##
        'h_gen' : 0,            # hydrogen generation [kg/timestep]
        'power_consumption' : 0    # power consumption of the electrolyzer [kW]
        # 'water_used' : 0    # water required for H2 prodcution [kg/timestep]
    }
    states={
        'soc': 0,          # state of charge after operation in a timestep [%]
        'flag': 0,         # flag inidicating buffer status (1=fully charged, -1=full discharged, 0=available for control) [-]
        'available_h2': 0, # amount of hydrogen that is available for the output [kg/timestep]
        'free_capacity':0 # amount of hyrogen that can be inputted before being full [kg/timestep]
        }


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
        ## common part
        self.setpoint = self._model.inputs.get('setpoint', 0)  # Initialize desired_out to 0 if not provided

        ## Electrolyzer part
        self.hhv =  286.6                # higher heating value of hydrogen [kJ/mol]
        self.mmh2 = 2.02                 # molar mass hydrogen (H2) [gram/mol]
        self.p_in_last = 0               # the initial power is initialised to 0 [kW]
        self.e_eff = self._model.parameters.get('e_eff') # electrolyzer efficiency [%]
        self.max_p_in = self._model.parameters.get('max_p_in')  # maximum input power [kW] set to infinity to allow for any input power
        self.max_p_ramp_rate = self._model.parameters.get('max_p_in', inf)  # maximum ramp up rate [kW/s]

        self.max_p_out = self._model.parameters.get('max_p_out', inf)  # maximum output power [kW] set to infinity to allow for any output power
        self.max_flow_rate_out = self._model.parameters.get('max_flow_rate_out', inf)
        self.max_flow_rate_out = min(self.max_flow_rate_out, self.kw_to_kg_per_h(self.max_p_out))  # determine the limiting factor

        ## Buffer part
        self.h2_soc_min = self._model.parameters.get('h2_soc_min')
        self.h2_soc_max = self._model.parameters.get('h2_soc_max')
        self.h2_charge_eff = 1
        self.h2_discharge_eff = 1
        self.max_flow_rate_in = self._model.parameters.get('max_flow_rate_in', inf)
        self.min_flow_rate_in = self._model.parameters.get('min_flow_rate_in', 0)  # Default to 0 if not provided
        self.min_flow_rate_out = self._model.parameters.get('min_flow_rate_out', 0)  # Default to 0 if not provided
        self.h2_capacity_tot = self.kwh_to_kg(self._model.parameters.get('h2_capacity_tot'))
        self.soc = self._model.states.get('soc')    # total hydrogen capacity [kg]
        self.flag = self._model.states.get('flag')
        self.available_h2 = 0  # amount of hydrogen that is available for the output [kg/timestep]
        self.free_capacity = 0


    def step(self, time, inputs, max_advance=1) -> None:
        # get input data 
        input_data = self.unpack_inputs(inputs)
        
        # how much hydrogen to charge or discharge (positive = charge, negative = discharge)
        setpoint = input_data.get('setpoint', self.setpoint)  # Default to 0 if not provided

        # If setpoint is set to charge
        if setpoint > 0:
            h_flow, power_consumption = self.generate_setpoint(desired_out=setpoint) # calculate generation provided the desired input power [kg/s] 
            buffer_results = self.buffer_operation(h2_in=h_flow, desired_out=0)

        # If setpoint is set to discharge
        elif setpoint < 0:
            buffer_results = self.buffer_operation(h2_in=0, desired_out=abs(setpoint))
            power_consumption = 0  # no power consumption when discharging
        
        
        #TODO slow loss of hydrogen due to leakage, no charging or discharging ###

        h2_discharge_cap, h2_charge_cap = self.cap_calc()  # calculate the amount of hydrogen that can be charged and discharged

        self.set_states({
            'soc': self.soc,
            'flag': self.flag,
            'available_h2': self.kg_to_kwh(h2_discharge_cap),
            'free_capacity': self.kg_to_kwh(h2_charge_cap)
            })

        self.set_outputs({
            'power_consumption': power_consumption,  # power consumption of the electrolyzer [kW]
            'h2_out': buffer_results['h2_out'],
            'overflow': buffer_results['overflow']
            })

        return time + self._model.time_step_size


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
    

    def kg_to_kwh(self, kg):
        """
        Converts kg of hydrogen produced to kWh.

        ...

        Parameters
        ----------
        kg : float
            Hydrogen produced in kg

        Returns
        -------
        kwh : float
            Energy in kWh
        """
        energy_density = (self.hhv / self.mmh2) * 1000
        kwh = kg * energy_density / 3600
        return kwh
    

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


    ############# BUFFER FUNCTIONALITIES ################
    #                                                   #
    #                                                   #
    #####################################################
    def limit_input_flow(self, h2_in: float) -> float:
        """
        Limits the input flow to the buffer based on the maximum and minimum flow rates.

        Parameters
        ----------
        h2_in : float
            Input flow to the buffer [kg/timestep]

        Returns
        -------
        float
            Limited input flow [kg/timestep]
        """
        # h2_in = min(h2_in, self.max_flow_rate_in) # limit the input by the maximum output
        # h2_in = max(h2_in, self.min_flow_rate_in) # limit the input by the minimum output
        min_flow_rate_in = self.min_flow_rate_in * self.time_step_size*self.time_resolution/3600  # Convert from kg/h to kg/timestep
        max_flow_rate_in = self.max_flow_rate_in * self.time_step_size*self.time_resolution/3600  # Convert from kg/h to kg/timestep
        if h2_in < min_flow_rate_in:
            raise ValueError(f"H2Buffer error: Input flow {h2_in} is below the minimum flow rate {min_flow_rate_in}.")
        elif h2_in > max_flow_rate_in:
            raise ValueError(f"H2Buffer error: Input flow {h2_in} exceeds the maximum flow rate {max_flow_rate_in}.")
        
        return h2_in
    
    def buffer_operation(self, h2_in:float, desired_out:float) -> dict:
        """
        Control for the buffer (physical). Outputs the actual flow.
        ...

        Parameters
        ----------
        h2_in : float
            Input to the buffer [kg/timestep]
        desired_out : float
            Desired output flow [kg/timestep]
        Returns
        -------
        result : dict
            Collection of parameters and their respective values
        """
        # print(f'DEBUG: This is desireed_out as viewed from operation: {desired_out}')
        h_per_step =  self.time_step_size*self.time_resolution/3600
        h2_out = 0  # initialize to 0 
        h2_in = self.limit_input_flow(h2_in)  # limit the input flow to the maximum input flow
        overflow = 0  # initialize overflow to 0

        # print(f'DEBUG: This is h2_in as viewed from operation: {h2_in}')
        desired_out = desired_out * h_per_step  # convert from kg/h to kg/timestep
        desired_out = min(desired_out, self.max_flow_rate_out*h_per_step) # limit the output by the maximum output
        if desired_out > 0:
            desired_out = max(desired_out, self.min_flow_rate_out*h_per_step) # limit the output by the minimum output

        net_h2 = h2_in - desired_out
        # print(f'DEBUG: This is net_h2 as viewed from operation: {net_h2} (in = {h2_in}, des_out={desired_out})')

        # calculate remaining charge capacity and discharge capacity based on the current state of charge
        h2_charge_cap, h2_discharge_cap = self.cap_calc()

        # CHARGING
        if net_h2 > 0:
            if net_h2 > h2_charge_cap:  # if the buffer cannot take all the input
                h2_in = h2_charge_cap
                overflow = net_h2 - h2_in  # calculate overflow
                self.soc = self.h2_soc_max
                self.flag = 1

            else:  # if the buffer can take all the input
                h2_in = net_h2
                self.soc = self.soc + (h2_in * (self.h2_charge_eff))/self.h2_capacity_tot * 100
                self.flag = 0
            h2_out = desired_out  # we can output the demand because we are net charging (net = in-out)
        
        # DISCHARGING
        elif net_h2 < 0:
            if abs(net_h2) > h2_discharge_cap:  # if the buffer cannot discharge all the desired output:
                h2_out = h2_discharge_cap + h2_in  # output is the maximum discharge capacity plus the input
                self.soc = self.h2_soc_min
                self.flag = -1
            else: # if the buffer can discharge all the desired output
                h2_out = desired_out
                self.soc = self.soc - (-net_h2 / (self.h2_discharge_eff))/self.h2_capacity_tot * 100
                self.flag = 0
        
        # NO NET FLOW
        else:
            if desired_out > 0:
                h2_out = h2_in
        
        results = {'h2_out': h2_out,
                   'actual_h2_in': h2_in,
                   'overflow': overflow}  # include overflow in results
        return results

    def cap_calc(self):
        """
        Function to determine the amount of h2 that can still be stored or discharged.
        ...

        Parameters
        ----------
        h2_in : float
            Input to the buffer [kg/timestep]
        desired_out : float
            Desired output flow [kg/timestep]
        Returns
        -------
        result : dict
            Collection of parameters and their respective values
        """
        h2_charge_soc = (self.h2_soc_max - self.soc) / (self.h2_charge_eff) 
        # print(f"\nDEBUG: \n THIS IS SOC: {self.soc} \n THIS IS h2_soc_max: {self.h2_soc_max} \n THIS IS discharge eff: {self.h2_charge_eff}\nTHIS IS h2_charge_soc in cap_calc: {h2_charge_soc}\n")
        h2_charge_cap = h2_charge_soc / 100 * self.h2_capacity_tot    # amount of H2 that can be charged (from external pov)
        h2_discharge_soc = (self.soc - self.h2_soc_min) * (self.h2_discharge_eff)
        h2_discharge_cap = h2_discharge_soc / 100 * self.h2_capacity_tot  # amount of H2 that can be discharged (from external pov)

        return h2_charge_cap, h2_discharge_cap