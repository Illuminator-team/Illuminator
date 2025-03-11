from illuminator.builder import ModelConstructor
import numpy as np

class H2Buffer(ModelConstructor):
    """
    A class to represent an H2 Buffer model.
    This class provides methods to simulate the hydrogen flow through the buffer.

    Attributes
    ----------
    parameters : dict
        Dictionary containing buffer parameters such as minimum and maximum state of charge, charge and discharge efficiency, and total capacity.
    inputs : dict
        Dictionary containing input variables like flow to the hydrogen buffer.
    outputs : dict
        Dictionary containing calculated outputs like flow into and out of the buffer, state of charge, operating mode, and buffer status flag.
    states : dict
        Dictionary containing the state variables of the buffer model.
    time_step_size : int
        Time step size for the simulation.
    time : int or None
        Current simulation time.

    Methods
    -------
    step(time, inputs, max_advance=1)
        Simulates one time step of the hydrogen buffer model.
    operation(h2_in, desired_out)
        Physically limits the in and outflow of hydrogen based on the design parameters
    cap_calc()
        Calculates the amount of hydrogen that can be charged ad discharged from the buffers models (external pov)
    """
    parameters={'h2_soc_min': 0,            # Minimum state of charge of the hydrogen buffer before discharging stops [%]
                'h2_soc_max': 100,          # Maximum state of charge of the hydrogen buffer before charging stops [%]
                'h2_charge_eff': 100,       # Charge efficiency of the H2 buffer [%]
                'h2_discharge_eff': 100,    # Discharge efficiency of the H2 buffer [%]
                'max_h2': 10,               # maximal flow (?) [kg/timestep]
                'min_h2': 10,               # minimal flow (?) [kg/timestep]
                'h2_capacity_tot': 100      # total capacity of the hydrogen buffer [kg]
                }
    inputs={'h2_in': 0,            # input to H2 buffer [kg/timestep]
            'desired_out': 0   # demanded hydrogen output flow [kg/timestep]
            }
    outputs={'h2_out': 0,       # flow out of the H2 buffer [kg/timestep]
             'actual_h2_in': 0  # The input that is processed in the buffer [kg/timestep]
             }
    states={ 'soc': 0,          # state of charge after operation in a timestep [%]
             'flag': 0,         # flag inidicating buffer status (1=fully charged, -1=full discharged, 0=available for control) [-]
             'available_h2': 0, # amount of hydrogen that is available for the output [kg/timestep]
             'free_capacity':0 # amount of hyrogen that can be inputted before being full [kg/timestep]
            }
    
    # define other attributes
    time_step_size = 1
    time = None
    
    def __init__(self, **kwargs) -> None:
        """
        Initialize the H2 buffer model with the provided parameters.

        Parameters
        ----------
        kwargs : dict
            Additional keyword arguments to initialize the model.
        """
        super().__init__(**kwargs)
        self.h2_soc_min = self._model.parameters.get('h2_soc_min')
        self.h2_soc_max = self._model.parameters.get('h2_soc_max')
        self.h2_charge_eff = self._model.parameters.get('h2_charge_eff')/100
        self.h2_discharge_eff = self._model.parameters.get('h2_discharge_eff')/100
        self.max_h2 = self._model.parameters.get('max_h2')
        self.min_h2 = self._model.parameters.get('min_h2')
        self.h2_capacity_tot = self._model.parameters.get('h2_capacity_tot')
        self.soc = self._model.states.get('soc')
        self.flag = self._model.states.get('flag')
        self.h2_charge_cap = self._model.states.get('available_h2')
        self.h2_discharge_cap = self._model.states.get('free_capacity')
        self.cap_calc()

    def step(self, time: int, inputs: dict=None, max_advance: int = 900) -> None:
        """
        Simulates one time step of the hydrogen buffer model.

        This method processes the inputs for one timestep, updates the hydrogen buffer state based on
        the hydrogen flow, and sets the model outputs accordingly.

        Parameters
        ----------
        time : int
            Current simulation time
        inputs : dict
            Dictionary containing input values, specifically:
            - h2_in: Hydrogen flow that appears to the input of the buffer [kg/timestep]
            - desired_out: The desired output flow of the buffer [kg/timestep]
        max_advance : int, optional
            Maximum time step size (default 900)

        Returns
        -------
        int
            Next simulation time step
        """
        input_data = self.unpack_inputs(inputs)

        # current_time = time * self.time_resolution
        # print(f'Buffertime: {current_time}')
        results = self.operation(input_data['h2_in'], input_data['desired_out'])

        self.set_outputs({'h2_out': results['h2_out'], 'actual_h2_in': results['actual_h2_in']})
        self.set_states({'soc': self.soc, 'flag': self.flag,'available_h2': self.h2_discharge_cap, 'free_capacity': self.h2_charge_cap})

        return time + self._model.time_step_size
    
    def operation(self, h2_in:float, desired_out:float) -> dict:
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
        h2_out = 0  # initialize to 0 
        h2_in = min(h2_in, self.max_h2) # limit the input by the maximum output
        # print(f'DEBUG: This is h2_in as viewed from operation: {h2_in}')
        desired_out = min(desired_out, self.max_h2) # limit the output by the maximum output
        net_h2 = h2_in - desired_out
        # print(f'DEBUG: This is net_h2 as viewed from operation: {net_h2} (in = {h2_in}, des_out={desired_out})')
        if net_h2 > 0:
            if net_h2 > self.h2_charge_cap:
                h2_in = self.h2_charge_cap
                self.soc = self.h2_soc_max
                self.flag = 1
            else:
                h2_in = net_h2
                self.soc = self.soc + (h2_in * (self.h2_charge_eff))/self.h2_capacity_tot * 100
                self.flag = 0
            h2_out = desired_out
        elif net_h2 < 0:
            if abs(net_h2) > self.h2_discharge_cap:
                # print(f'DEBUG: abs(net_h2) > self.h2_discharge_cap')
                h2_out = self.h2_discharge_cap
                # print(f'DEBUG: soc = {self.soc}, discharge_cap = {self.h2_discharge_cap}')
                self.soc = self.h2_soc_min
                self.flag = -1
            else:
                # print("This case:\n")
                h2_out = desired_out
                # print(f'h2_out={h2_out}\nsoc before: {self.soc}\ndischarhe eff={self.h2_discharge_eff}\ncap={self.h2_capacity_tot}')
                self.soc = self.soc - (-net_h2 / (self.h2_discharge_eff))/self.h2_capacity_tot * 100
                self.flag = 0
        else:
            if desired_out > 0:
                h2_out = h2_in
        # print(f'DEBUG: This is soc as viewed from operation: {self.soc}')   
        # print(f'DEBUG: This is h2_out as viewed from operation: {h2_out}\n\n')
        self.cap_calc()
        results = {'h2_out': h2_out,
                   'actual_h2_in': h2_in}
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
        self.h2_charge_cap = h2_charge_soc / 100 * self.h2_capacity_tot    # amount of H2 that can be charged (from external pov)
        h2_discharge_soc = (self.soc - self.h2_soc_min) * (self.h2_discharge_eff)
        self.h2_discharge_cap = h2_discharge_soc / 100 * self.h2_capacity_tot  # amount of H2 that can be discharged (from external pov)
    

        
    