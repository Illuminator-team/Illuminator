from illuminator.builder import ModelConstructor
import numpy as np

class EV2(ModelConstructor):
    """
    A class to represent an Electric Vehicle (EV) charging model.
    This class provides methods to simulate the charging process of an EV battery.

    Attributes
    ----------
    parameters : dict
        Dictionary containing EV parameters such as end phases of charging, maximum power, and battery capacity.
    inputs : dict
        Dictionary containing input variables like available power for charging.
    outputs : dict
        Dictionary containing calculated outputs like power demand during charging.
    states : dict
        Dictionary containing the state variables of the EV model, such as state of charge (SOC) and desired SOC.
    time_step_size : int
        Time step size for the simulation.
    time : int or None
        Current simulation time.

    Methods
    -------
    step(time, inputs, max_advance=900)
        Simulates one time step of the EV charging model.
    charge(available_power, max_advance)
        Implements the charging curve and calculates the power demand based on available power and battery state.
    """
    parameters={'end_initial_phase': 0,     # soc at which the mid-phase starts [%]
                'end_mid_phase': 0,         # soc at which the final-phase starts [%]
                'max_power': 0,             # Max power from the charger [kW]
                'battery_cap': 0,           # capacity of the battery car [kWh]
                'fast': False}              # Whether to use the opwer curve or not [bool]   

    inputs={'load_in': 0}                   # incomming power [kW]
    outputs={'demand': 0,                   # power used by the charger per timestep [kW]
            'presence': 0}                  # 1 for EV present, 0 for not present
    states={'soc': 0,                       # state of charge after operation in a timestep [%]
            'desired_soc': 0}               # soc that the car battery should have at the end of charging cycle [%] 

             
            
    
    # define other attributes
    time_step_size = 1
    time = None
    
    def __init__(self, **kwargs) -> None:
        """
        Initialize the EV model with the provided parameters.

        Parameters
        ----------
        kwargs : dict
            Additional keyword arguments to initialize the model.
        """
        super().__init__(**kwargs)
        self.end_initial_phase = self._model.parameters.get('end_initial_phase')
        self.fast = self._model.parameters.get('fast')
        self.end_mid_phase = self._model.parameters.get('end_mid_phase')
        self.max_power = self._model.parameters.get('max_power')
        self.battery_cap = self._model.parameters.get('battery_cap')
        self.soc = self._model.states.get('soc')
        self.desired_soc = self._model.states.get('desired_soc')
        # self.presence = self._model.states.get('presence')

       

    def step(self, time: int, inputs: dict=None, max_advance: int = 900) -> None:
        """
        Simulates one time step of the EV model.

        This method processes the inputs for one timestep, updates the state of charge (SOC)
        based on the charging process, and sets the model outputs accordingly.

        Parameters
        ----------
        time : int
            Current simulation time
        inputs : dict
            Dictionary containing input values, specifically:
            - available_power: Power available for charging [kW]
        max_advance : int, optional
            Maximum time step size in seconds (default 900)

        Returns
        -------
        int
            Next simulation time step
        """
        
        self.time = time
        input_data = self.unpack_inputs(inputs)
        # print("DEBUG: timestep when entering step():", self.timestep)
        
        load_in = input_data.get('load_in')
        self.presence = input_data.get('presence')
        # self.set_outputs({'demand': demand})
        demand, self.soc = self.charge()
        self.set_outputs({'demand': demand})
        print(f"self.soc at time {time} = {self.soc}")
        self.set_states({'soc': self.soc})
        
        # print("DEBUG: self.time in step():", self.time)       
        return time + self._model.time_step_size
    

    def charge(self):     
        # Only follow curve when the EV is present
        # print(f"DEBUG at time: {self.time}\n-self.start_charge = {self.start_charge}\n-self.presence = {self.presence}\n-self.soc = {self.soc}\n-self.desired_soc = {self.desired_soc}")
        if self.presence == 1 and self.soc < self.desired_soc:
            # print('DEBUG: self.start_charge == self.time at time:', self.time)
            if self.fast is False:
                
                energy_needed = (self.desired_soc - self.soc)/100 * self.battery_cap
                if energy_needed < self.max_power * 1/4:
                    demand = energy_needed / (1/4)
                    self.soc = self.desired_soc
                else:
                    demand = self.max_power
                    energy_plus = demand * 1/4 # 15min timestep
                    self.soc += energy_plus/self.battery_cap *100
                
                
            else:
            # implement charging curve
            # needs to be corrected 
                if 0 <= self.soc < self.end_initial_phase:  # initial phase
                    p_in = self.max_power/(self.end_initial_phase - 0) * self.soc
                elif self.end_initial_phase <= self.soc < self.end_mid_phase:   # mid phase
                    p_in = self.max_power*(0.9 -1)/(self.end_initial_phase-self.end_mid_phase) * self.soc
                else:   # final phase
                    p_in = (0 - self.max_power*0.9)/(100-self.end_mid_phase) * self.soc
        else:
            # p_in = 0
            demand = 0 
        return demand, self.soc

        # # power input is limited by the chargong curve or the available power
        # p_in = min(available_power, p_in)
        
        # energy_to_fill = self.battery_cap*(self.desired_soc - self.soc)/100
        # energy_plus = p_in * hours

        # # if the input power overcharges the battery, the demand is limited to charge battery to 100%
        # if energy_plus > energy_to_fill:
        #     # demand = energy_to_fill / hours
        #     self.soc = 100
        # else:   
        #     # demand = p_in
        #     self.soc += self.soc + energy_plus/self.battery_cap
        # return

        

    
