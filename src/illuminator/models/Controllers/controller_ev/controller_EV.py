from illuminator.builder import ModelConstructor

# construct the model
class ControllerEV(ModelConstructor):
    """
    A class to represent a Controller model for a renewable energy system.
    This class provides methods to manage power flows between renewable sources, 
    battery storage and electrical loads, with congestion management capabilities.

    Attributes
    parameters : dict
        Dictionary containing control parameters:
        - soc_min: Minimum state of charge of the battery (%)
        - soc_max: Maximum state of charge of the battery (%)
        - max_p: Maximum power to/from the battery (kW)
        - gridconnect_ctrl: Maximum grid connection capacity (kW)
    inputs : dict
        Dictionary containing inputs:
        - wind_gen: Wind power generation (kW)
        - pv_gen: Solar power generation (kW)
        - load_dem: Electrical load demand (kW)
        - soc: State of charge of the battery (%)
        - load_EV: Electric vehicle load demand (kW)
        - load_HP: Heat pump load demand (kW)
        - flag_warning: Warning flag for grid congestion
        - limit_grid_connect: Grid connection limit
    outputs : dict
        Dictionary containing calculated outputs:
        - flow2b: Power flow to/from battery (kW)
        - res_load: Residual load (kW)
        - dump: Excess power that cannot be stored (kW)
    states : dict
        Dictionary containing the state variables of the system.
    time_step_size : int
        Time step size for the simulation.
    time : int or None
        Current simulation time.

    Methods
    __init__(**kwargs)
        Initializes the Controller model with the provided parameters.
    step(time, inputs, max_advance)
        Simulates one time step of the Controller model.
    control(wind_gen, pv_gen, load_dem, soc, load_EV, load_HP, flag_warning)
        Manages power flows based on generation, demand, storage states and grid congestion.
    """
    parameters={'soc_min': 0,  # Minimum state of charge of the battery before discharging stops
                'soc_max': 100,  # Maximum state of charge of the battery before charging stops
                'max_p': 100  # Maximum power to/from the battery
                }
    inputs={'wind_gen': 0,  # Wind power generation
            'pv_gen': 0,  # Solar power generation
            'load_dem': 0,  # Electrical load demand
            'soc': 0,  # State of charge of the battery
            'load_EV': 0
            }
    outputs={'flow2b': 0,  # Power flow to/from battery (positive for charging, negative for discharging)
             'dump': 0,  # Excess power that cannot be stored or used
             'res_load': 0
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
        kwargs : dict
            Additional keyword arguments to initialize the controller model,
        """
        super().__init__(**kwargs)
        self.soc_min = self.parameters['soc_min']  # Minumum state of charge of the battery before discharging stops (%)
        self.soc_max = self.parameters['soc_max']  # Maximum state of charge of the battery before charging stops (%)
        self.max_p = self.parameters['max_p']  # Maximum power to/from the battery [kW]


        self.flow_b = 0  # Internal state representing the power flow to/from battery
        self.dump = 0  # Internal state representing excess power
        self.res_load = 0  # Internal state representing the residual load



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
            - load_EV (float): Electric vehicle load demand [kW]
            - load_HP (float): Heat pump load demand [kW]
            - flag_warning (int): Warning flag for grid congestion
            max_advance (int, optional): Maximum time to advance in seconds. Defaults to 900.

        Returns:
            int: Next simulation time step
        """
        input_data = self.unpack_inputs(inputs)  # make input data easily accessible
        self.time = time

        # print("DEBUG:", input_data)
        results = self.control(
            wind_gen=input_data['wind_gen'],
            pv_gen=input_data['pv_gen'],
            load_dem=input_data['load_dem'],
            soc=input_data['soc'],
            load_EV=input_data['load_EV'])
            
        self.set_outputs(results)

        # return the time of the next step (time untill current information is valid)
        return time + self._model.time_step_size

    def control(self, wind_gen, pv_gen, load_dem, soc=None, load_EV=None, load_HP=None, flag_warning = None):
        """
        Controls power flows based on generation, demand and storage states.

        Args:
            wind_gen (float): Wind power generation [kW]
            pv_gen (float): Solar power generation [kW]
            load_dem (float): Load demand [kW]
            soc (float): Battery state of charge [%]
            load_EV (float, optional): Electric vehicle load demand [kW]
            load_HP (float, optional): Heat pump load demand [kW]
            flag_warning (int, optional): Warning flag for grid congestion

        Returns:
            dict: Dictionary containing:
            - flow2b (float): Power flow to/from battery [kW]
            - res_load (float): Residual load [kW]
            - dump (float): Excess power [kW]
        """
        # reset flow2b
        self.flow_b = 0

        self.res_load = load_dem + load_EV - wind_gen - pv_gen  # kW

        if self.res_load > 0:
            # demand not satisfied -> discharge battery if possible
            if soc > self.soc_min:  # checking if soc is above minimum
                print('Discharge Battery')
                max_discharge = (soc - self.soc_min) / 100 * self.max_p
                print(f'max discharge: {max_discharge}')
                print(f'res load: {self.res_load}')
                self.flow_b = -min(self.res_load, max_discharge)
                print('Flow Bat: ' + str(self.flow_b))
                # self.soc_b = self.soc_b + self.flow_b soc is not updated in controller

        elif self.res_load < 0:
            if soc < self.soc_max:
                print('Charge Battery')
                max_flow2b = ((self.soc_max - soc) / 100) * self.max_p  # Energy flow in kW
                self.flow_b = min((-self.res_load), max_flow2b)
                print('Flow Bat: ' + str(self.flow_b))
                print('Excess generation that cannot be stored: ' + str(-self.res_load - self.flow_b))

        else:
            print('No Residual Load, RES production exactly covers demand')
            self.flow_b = 0
            self.dump = 0
            # demand_res = residual_load

        self.dump = -(self.res_load + self.flow_b)

        re_params = {'flow2b': self.flow_b, 'res_load': self.res_load, 'dump': self.dump}

        return re_params
