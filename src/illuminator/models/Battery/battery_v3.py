from illuminator.builder import ModelConstructor

# Define the model parameters, inputs, outputs...
# TODO: Currently if a value or category isn't defined in the yaml
# # it doesn't default to the ones below, it simply doesn't run. <- check if this is still the case

# construct the model
class Battery(ModelConstructor):
    """
    Battery model class for simulating battery charging and discharging behavior.

    This class implements a battery model that can simulate charging and discharging cycles,
    track state of charge, and manage power flows while respecting battery constraints.

    Parameters
    ----------
    max_p : float
        Maximum charging power limit in kW
    min_p : float  
        Maximum discharging power limit in kW
    max_energy : float
        Maximum energy storage capacity in kWh
    charge_efficiency : float
        Battery charging efficiency in %
    discharge_efficiency : float
        Battery discharging efficiency in %
    soc_min : float
        Minimum allowable state of charge in %
    soc_max : float
        Maximum allowable state of charge in %

    Returns
    -------
    None
    """
    parameters={'max_p': 150,  # maximum charging power limit (kW)
                'min_p': 250,  # maximum discharging power limit (kW)
                'max_energy': 50,  # maximum energy storage capacity of the battery (kWh)
                'charge_efficiency': 90,  # efficiency of charging the battery (%)
                'discharge_efficiency': 90,  # efficiency of discharging the battery (%)
                'soc_min': 3,  # minimum allowable state of charge for the battery (%)
                'soc_max': 80,  # maximum allowable state of charge for the battery (%)
                #'resolution': 1  # time resolution for simulation steps (seconds)
                }
    inputs={'flow2b': 0,  # power flow to/from the battery. Positive for charging, negative for discharging (kW)
            }
    outputs={'p_out': 20,  # output power from the battery after discharge/charge decision (Kw)
             'p_in': 20,  # input power to the battery (kW)
             }
    states={'mod': 0, # operation mode: 0=no action, 1=charge, -1=discharge
            'soc': 0,  # updated state of charge after battery operation (%)
            'flag': -1  # flag indicating battery status: 1=fully charged, -1=fully discharged, 0=available for control
        }
    time_step_size=1
    time=None


    def __init__(self, **kwargs):
        """
        Initialize the battery model with specified parameters.

        This method initializes a new battery instance with given parameters, setting up
        initial values for state of charge, efficiency, power limits, and other operational
        parameters.

        Parameters
        ----------
        kwargs : dict
            Dictionary containing model parameters including:
            - charge_efficiency: Battery charging efficiency (%)
            - discharge_efficiency: Battery discharging efficiency (%)
            - max_p: Maximum charging power limit (kW)
            - min_p: Maximum discharging power limit (kW)
            - max_energy: Maximum energy storage capacity (kWh)
            - soc_min: Minimum allowable state of charge (%)
            - soc_max: Maximum allowable state of charge (%)

        Returns
        -------
        None
        """
        super().__init__(**kwargs)
        self.soc = self._model.states.get('soc')
        self.flag = self._model.states.get('flag')
        self.mod = self._model.states.get('mod')
        self.charge_efficiency = self._model.parameters.get('charge_efficiency')/100
        self.discharge_efficiency = self._model.parameters.get('discharge_efficiency')/100
        self.max_p = self._model.parameters.get('max_p')
        self.min_p = self._model.parameters.get('min_p')
        self.max_energy = self._model.parameters.get('max_energy')
        self.soc_min = self._model.parameters.get('soc_min')
        self.soc_max = self._model.parameters.get('soc_max')
        self.powerout = 0



    def step(self, time: int, inputs: dict=None, max_advance: int=900) -> None:
        """
        Process one simulation step of the battery model.

        This method processes the inputs for one timestep, updates the battery state based on
        the requested power flow, and sets the model outputs and states accordingly.

        Parameters
        ----------
        time : int
            Current simulation time
        inputs : dict
            Dictionary containing input values, specifically:
            - flow2b: Power flow to/from battery (positive=charging, negative=discharging) in kW
        max_advance : int, optional
            Maximum time step size in seconds (default 900)

        Returns
        -------
        int
            Next simulation time step
        """
        input_data = self.unpack_inputs(inputs)

        results = self.output_power(input_data['flow2b']) # In this model, the input should come from the controller

        self.soc = results.pop('soc')
        self.flag = results.pop('flag')
        self.mod = results.pop('mod')
        self.set_states({'soc': self.soc, 'flag': self.flag, 'mod': self.mod}) # set the state of charge and remove it from the results at the same time
        self.set_outputs(results)

        return time + self._model.time_step_size


    # this method is called from the output_power method when conditions are met.
    def discharge_battery(self, flow2b:int) -> dict:  #flow2b is in kw
        """
        Discharge the battery, calculate the state of charge and return parameter information.
        Discharge the battery, calculate the state of charge and return parameter information.

        This method discharges the battery based on the requested power flow, updates the state of 
        charge (SOC), and returns a dictionary containing the battery's operational parameters.

        Parameters
        ----------
        flow2b : int
            Power flow requested from the battery (negative value) in kW
        
        Returns
        -------
        re_params : dict
            Collection of parameters and their respective values:
            - p_out: Output power from the battery after discharge decision (kW)
            - p_in: Input power to the battery (kW)
            - soc: Updated state of charge after battery operation (%)
            - mod: Operation mode: 0=no action, 1=charge, -1=discharge
            - flag: Flag indicating battery status: 1=fully charged, -1=fully discharged, 0=available for control
            Collection of parameters and their respective values:
            - p_out: Output power from the battery after discharge decision (kW)
            - p_in: Input power to the battery (kW)
            - soc: Updated state of charge after battery operation (%)
            - mod: Operation mode: 0=no action, 1=charge, -1=discharge
            - flag: Flag indicating battery status: 1=fully charged, -1=fully discharged, 0=available for control
        """
        hours = self.time_resolution / 60 / 60
        flow = max(self.min_p, flow2b)
        if (flow < 0):
            energy2discharge = flow * hours / self.discharge_efficiency  # (-ve)
            energy_capacity = ((self.soc_min - self.soc) / 100) * self.max_energy
            if self.soc <= self.soc_min:
                self.flag = -1
                self.powerout = 0
            else:
                if energy2discharge > energy_capacity:
                    # more than enough energy to discharge
                    # Check if minimum energy of the battery is reached -> Adjust power if necessary
                    self.soc = self.soc + (energy2discharge / self.max_energy * 100)
                    self.powerout = flow
                    self.flag = 0  # Set flag as ready to discharge or charge

                else:  # Fully-discharge Case
                    self.powerout = energy_capacity * self.discharge_efficiency / hours  # Can only discharge remaining capacity, but even less because of inefficiency
                    # warn('\n Home Battery is fully discharged!! Cannot deliver more energy!')
                    self.soc = self.soc_min
                    self.flag = -1  # Set flag as 1 to show fully discharged state
        self.soc = round(self.soc, 3)
        re_params = {'p_out': self.powerout,
                        # 'energy_drain': output_show,
                        # 'energy_consumed': 0,
                        'p_in': flow,
                        'soc': self.soc,
                        'mod': -1,
                        'flag': self.flag}
                        #'i_soc': self.i_soc}

        # here we are returning the values of these parameters which will be needed by another python model
        return re_params


    def charge_battery(self, flow2b:int) -> dict:
        
        hours = self.time_resolution / 60 / 60
        flow = min(self.max_p, flow2b)
        if (flow > 0):
            energy2charge = flow * hours * self.charge_efficiency  # (-ve)
            energy_capacity = ((self.soc_max - self.soc) / 100) * self.max_energy
            if self.soc >= self.soc_max:
                self.flag = 1
                self.powerout = 0
            else:
                if energy2charge <= energy_capacity:
                    self.soc = self.soc + (energy2charge / self.max_energy * 100)
                    self.powerout = flow
                    self.flag = 0  # Set flag as ready to discharge or charge

                else:  # Fully-charge Case
                    self.powerout = energy_capacity / self.charge_efficiency / hours  # you can only charge the remaining capacity, but it would cost more because of inefficiency
                    # warn('\n Home Battery is fully discharged!! Cannot deliver more energy!')
                    self.soc = self.soc_max
                    self.flag = 1  # Set flag as 1 to show fully discharged state
        self.soc = round(self.soc, 3)
        re_params = {'p_out': self.powerout,
                        # 'energy_consumed': output_show,
                        # 'energy_drain': 0,
                        'p_in': flow,
                        'soc': self.soc,
                        'mod': 1,
                        'flag': self.flag}

        return re_params


    # this method is like a controller which calls a method depending on the condition.
    # first, this is checked. As per the p_ask and soc, everything happens.
    # p_ask and soc are the parameters whos values we have to provide when we want to create an object of this class. i.e,
    # this method is like a controller which calls a method depending on the condition.
    # first, this is checked. As per the p_ask and soc, everything happens.
    # p_ask and soc are the parameters whos values we have to provide when we want to create an object of this class. i.e,
    # when we want to make a battery model.
    def output_power(self, flow2b:int) -> dict:#charging power: positive; discharging power:negative
        """
        Determine the battery operation mode and power output based on the requested power flow.

        This method controls the battery's operation by determining whether to charge, discharge,
        or maintain the current state based on the requested power flow and the battery's 
        state of charge (SOC).
        Determine the battery operation mode and power output based on the requested power flow.

        This method controls the battery's operation by determining whether to charge, discharge,
        or maintain the current state based on the requested power flow and the battery's 
        state of charge (SOC).

        Parameters
        ----------
        flow2b : int
            Power flow requested to/from the battery. Positive for charging, negative for discharging (kW)
            Power flow requested to/from the battery. Positive for charging, negative for discharging (kW)

        Returns
        -------
        re_params : dict
            Dictionary containing the battery's operational parameters:
            - p_out: Output power after charge/discharge decision (kW)
            - p_in: Input power to the battery (kW)  
            - soc: Updated state of charge (%)
            - mod: Operation mode (0=no action, 1=charge, -1=discharge)
            - flag: Battery status (1=fully charged, -1=fully discharged, 0=available)
        """
        # conditions start:
        if flow2b == 0:  # i.e when there isn't a demand of power at all,

            # soc can never exceed the limit so when it is equal to the max, we tell it is completely charged
            if self.soc >= self.soc_max:
                self.flag = 1  # meaning battery object we created is fully charged

            # soc can never exceed the limit so when it is equal to the min, we tell it is completely discharged
            elif self.soc <= self.soc_min:
                self.flag = -1

            # if the soc is between the min and max values, it is ready to be discharged or charged as per the situation
            else:
                self.flag = 0  # meaning it is available to operate.

            # here we are sending the current state of the battery
            re_params={'p_out': 0,
                       # 'energy_drain': 0,
                       # 'energy_consumed': 0,
                       'p_in': 0,
                        'soc': self.soc,
                        'mod': 0,
                        'flag': self.flag}
        else:
            # if the p_ask is a -ve value, it means battery needs to discharge.
            if flow2b < 0:  #discharge

                # Can the battery discharge or not depends on the current state of the battery for which we call the
                # method discharge_battery. If the p_ask < 0 condition is met, the program directly goes the method.
                re_params = self.discharge_battery(flow2b)

            # other option is for p_ask to be > 0 which means we need to charge.
            else:

                # Can the battery charge depends on the current state of the battery for which we call the
                # method charge_battery. If the p_ask > 0 condition is met, the program directly goes the method.
                re_params = self.charge_battery(flow2b)


        return re_params