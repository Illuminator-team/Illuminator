from illuminator.builder import ModelConstructor

# construct the model
class Controller_T1(ModelConstructor):
    """
    Controller for managing power flows between renewable generation, load, and battery storage.
    
    This controller determines how power should be distributed between renewable sources (wind, solar),
    load demands, and battery storage. It implements basic control logic for battery charging and
    discharging based on state of charge limits and power constraints.

    Parameters
    ----------
    soc_min : float
        Minimum state of charge of the battery before discharging stops (%)
    soc_max : float
        Maximum state of charge of the battery before charging stops (%)
    max_p : float
        Maximum power to/from the battery (kW)
    battery_active : bool
        Flag to enable/disable battery operation
    
    Inputs
    ----------
    wind_gen : float
        Wind power generation (kW)
    pv_gen : float
        Solar power generation (kW)
    load_dem : float
        Electrical load demand (kW)
    soc : float
        State of charge of the battery (%)

    Outputs
    ----------
    flow2b : float 
        Power flow to/from battery (kW, positive for charging, negative for discharging)
    res_load : float
        Residual load after renewable generation (kW)
    dump : float
        Excess power that cannot be stored or used (kW)
    
    States
    ----------
    None
        
    """
    parameters={'soc_min': 0,  # Minimum state of charge of the battery before discharging stops
                'soc_max': 100,  # Maximum state of charge of the battery before charging stops
                'max_p': 100,  # Maximum power to/from the battery
                'battery_active': True
                }
    inputs={'wind_gen': 0,  # Wind power generation
            'pv_gen': 0,  # Solar power generation
            'load_dem': 0,  # Electrical load demand
            'soc': 0  # State of charge of the battery
            }
    outputs={'flow2b': 0,  # Power flow to/from battery (positive for charging, negative for discharging)
             'res_load': 0,
             'dump': 0  # Excess power that cannot be stored or used
             }
    states={}

    # define other attributes
    time_step_size = 1
    time = None


    def __init__(self, **kwargs) -> None:
        """
        Initialize the Controller model with the provided parameters.

        Parameters
        ----------
        kwargs
        """
        super().__init__(**kwargs)
        self.soc_min = self.parameters['soc_min']  # Minumum state of charge of the battery before discharging stops (%)
        self.soc_max = self.parameters['soc_max']  # Maximum state of charge of the battery before charging stops (%)
        self.max_p = self.parameters['max_p']  # Maximum power to/from the battery [kW]
        self.battery_active = self.parameters['battery_active']
        self.flow_b = 0  # Internal state representing the power flow to/from battery
        self.dump = 0  # Internal state representing excess power
        self.res_load = 0  # Internal state representing the residual load




    # define step function
    def step(self, time: int, inputs: dict=None, max_advance: int=900) -> None:  # step function always needs arguments self, time, inputs and max_advance. Max_advance needs an initial value.
        """
        Advances the simulation one time step.

        Args:
            time (int): Current simulation time
            inputs (dict): Dictionary containing input values:
            - wind_gen (float): Wind power generation [kW]
            - pv_gen (float): Solar power generation [kW]
            - load_dem (float): Load demand [kW]
            - soc (float): Battery state of charge [%]
            max_advance (int, optional): Maximum time to advance in seconds. Defaults to 900.

        Returns:
            int: Next simulation time step
        """
        input_data = self.unpack_inputs(inputs)  # make input data easily accessible
        self.time = time

        if self.battery_active:
            results = self.control(
            wind_gen=input_data['wind_gen'],
            pv_gen=input_data['pv_gen'],
            load_dem=input_data['load_dem'],
            soc=input_data['soc']
            )

        else:
            results = self.control(
                wind_gen=input_data['wind_gen'],
                pv_gen=input_data['pv_gen'],
                load_dem=input_data['load_dem']
            )

        self.set_outputs(results)

        # return the time of the next step (time untill current information is valid)
        return time + self._model.time_step_size


    def control(self, wind_gen, pv_gen, load_dem, soc = None):
        """
        Controls power flows based on generation, demand and storage states.

        Args:
            wind_gen (float): Wind power generation [kW]
            pv_gen (float): Solar power generation [kW]
            load_dem (float): Load demand [kW]
            soc (float): Battery state of charge [%]

        Returns:
            dict: Dictionary containing:
            - flow2b (float): Power flow to/from battery [kW]
            - res_load (float): Residual load [kW]
            - dump (float): Excess power [kW]
        """
        #reset flow2b
        self.flow_b = 0
        # print('Load dem: ' + str(load_dem))
        # print('pv: ' + str(pv_gen))
        # print('wind: ' + str(wind_gen))

        self.res_load = load_dem - wind_gen - pv_gen # kW

        if self.battery_active == True:
            if self.res_load > 0:
                # demand not satisfied -> discharge battery if possible
                if soc > self.soc_min:  # checking if soc is above minimum
                    # print('Discharge Battery')
                    max_discharge = (soc-self.soc_min)/100 * self.max_p
                    # print(f'max discharge: {max_discharge}')
                    # print(f'res load: {self.res_load}')
                    self.flow_b = -min(self.res_load, max_discharge)
                    # print ('Flow Bat: '  + str(self.flow_b))
                    #self.soc_b = self.soc_b + self.flow_b soc is not updated in controller
                          
            elif self.res_load < 0:
            
                if soc < self.soc_max:
                    # print('Charge Battery')
                    max_flow2b = ((self.soc_max-soc)/100) * self.max_p  # Energy flow in kW
                    self.flow_b = min((-self.res_load), max_flow2b)
                    # print ('Flow Bat: '  + str(self.flow_b))
                    # print('Excess generation that cannot be stored: ' + str(-self.res_load-self.flow_b))

            else:  # res.load == 0
                # print('No Residual Load, RES production exactly covers demand')
                self.flow_b = 0
                #demand_res = residual_load

            #update residual load with battery discharge/charge
            #self.res_load = self.res_load + self.flow_b
            self.dump = -(self.res_load + self.flow_b)

            re_params = {'flow2b': self.flow_b,'res_load': self.res_load,'dump': self.dump}
        else:
            re_params = {'res_load': self.res_load,'dump': self.dump}
        return re_params