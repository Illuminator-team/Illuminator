from illuminator.builder import ModelConstructor

# construct the model
class ControllerT3Congestion(ModelConstructor):
    """
    Controller for managing power flows between renewable generation, load, battery storage, and electrified assets.
    
    This controller determines power distribution between renewable sources (wind, solar), load demands,
    battery storage, and electrified assets like EVs and heat pumps. It implements control logic for battery 
    charging/discharging and load shifting to manage grid congestion.

    Parameters
    ----------
    soc_min : float
        Minimum state of charge of the battery before discharging stops (%)
    soc_max : float
        Maximum state of charge of the battery before charging stops (%)
    max_p : float
        Maximum power to/from the battery (kW)
    gridconnect_ctrl : float
        Grid connection capacity limit (kW)
    battery_active : bool
        Flag to enable/disable battery operation
    elec_assets : bool
        Flag to enable/disable electrified assets
    load_shift_active : bool
        Flag to enable/disable load shifting during congestion warnings
    
    Inputs
    ----------
    wind_gen : float
        Wind power generation (kW)
    pv_gen : float
        Solar power generation (kW)
    load_dem : float
        Base electrical load demand (kW)
    soc : float
        State of charge of the battery (%)
    load_EV : float
        Electric vehicle load demand (kW)
    load_HP : float
        Heat pump load demand (kW)
    flag_warning : int
        Warning flag for grid congestion

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
    limit_grid_connect : float
        Grid connection limit for congestion management (kW)
    """
    parameters={'soc_min': 0,  # Minimum state of charge of the battery before discharging stops
                'soc_max': 100,  # Maximum state of charge of the battery before charging stops
                'max_p': 100,  # Maximum power to/from the battery
                'gridconnect_ctrl': 15,  #kW connection capacity
                'battery_active': True,
                'elec_assets': True,
                'load_shift_active': True # if true the controller shifts the load after receiving a flag warning
                }
    inputs={'wind_gen': 0,  # Wind power generation
            'pv_gen': 0,  # Solar power generation
            'load_dem': 0,  # Electrical load demand
            'soc': 0,  # State of charge of the battery
            'load_EV': 0,  
            'load_HP': 0,
            'flag_warning': None
            }
    outputs={'flow2b': 0,  # Power flow to/from battery (positive for charging, negative for discharging)
             'res_load': 0,
             'dump': 0  # Excess power that cannot be stored or used
             }
    states={'limit_grid_connect': None}

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
        self.battery_active = self.parameters['battery_active']
        self.elec_assets = self.parameters['elec_assets'] # True if electrified assets
        self.load_shift_active = self.parameters['load_shift_active']
        self.flow_b = 0  # Internal state representing the power flow to/from battery
        self.dump = 0  # Internal state representing excess power
        self.res_load = 0  # Internal state representing the residual load
        self.gridconnect_ctrl = self.parameters['gridconnect_ctrl']
        self.load_shift = 0

        if self.gridconnect_ctrl is not None:
            self.limit_grid_connect = self.gridconnect_ctrl * 0.7
            print('connection limit_:' + str(self.limit_grid_connect))
        else:
            raise ValueError("gridconnect_ctrl must be specified in parameters")       


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
            - load_EV (float): Electric vehicle load demand [kW]
            - load_HP (float): Heat pump load demand [kW]
            - flag_warning (int): Warning flag for grid congestion
            max_advance (int, optional): Maximum time to advance in seconds. Defaults to 900.

        Returns:
            int: Next simulation time step
        """
        input_data = self.unpack_inputs(inputs)  # make input data easily accessible
        self.time = time

        if self.elec_assets:
            results = self.control(
                wind_gen=input_data['wind_gen'],
                pv_gen=input_data['pv_gen'],
                load_dem=input_data['load_dem'],
                soc=input_data['soc'],
                load_EV=input_data['load_EV'],
                load_HP=input_data['load_HP'],
                flag_warning=input_data['flag_warning']
                )
        else:
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
        print('flag warning: ' + str(flag_warning))
        print('Load dem: ' + str(load_dem))
        print('pv: ' + str(pv_gen))
        print('wind: ' + str(wind_gen))

        # still need to include how load_shift gets added if flag does not give warning

        if load_EV is not None:
            if load_HP is not None:
                self.res_load = load_dem + load_EV + load_HP - wind_gen - pv_gen  # kW


            else:
                self.res_load = load_dem + load_EV - wind_gen - pv_gen


        elif load_HP is not None:
            self.res_load = load_dem + load_HP - wind_gen - pv_gen

        else:
            self.res_load = load_dem - wind_gen - pv_gen  # kW

        if self.load_shift_active == True:

            if self.res_load < self.limit_grid_connect:
                extra_load_allowed = min(self.limit_grid_connect-self.res_load,self.limit_grid_connect)
                additional_load = min(extra_load_allowed, self.load_shift)
                print('additional load: ' + str(additional_load))
                self.res_load = self.res_load + additional_load
                self.load_shift -= additional_load

        if self.battery_active:
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

            else: # in the case self.res_load == 0
                print('No Residual Load, RES production exactly covers demand')
                self.flow_b = 0
                # demand_res = residual_load

            # update residual load with battery discharge/charge
            # self.res_load = self.res_load + self.flow_b
            self.dump = -(self.res_load + self.flow_b)
        else:
            self.dump = - self.res_load

        if self.load_shift_active == True and flag_warning == 1:
            print('enter flag condition')
            overload = (-self.dump) - self.limit_grid_connect
            self.load_shift += min(overload, load_HP + load_EV)
            print('load_not_yet: ' + str(self.load_shift))
            if overload > 0:
                print('update dump')
                self.dump = -self.limit_grid_connect

        print('residual load: ' + str(self.res_load))
        print('battery flow: ' + str(self.flow_b))
        print('dump: ' + str(self.dump))
        # if self.bat_active == 1:
        re_params = {'flow2b': self.flow_b, 'res_load': self.res_load, 'dump': self.dump}
        # else:
        # re_params = {'res_load': self.res_load,'dump': self.dump}
        return re_params
