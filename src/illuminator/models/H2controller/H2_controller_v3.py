from illuminator.builder import ModelConstructor

# construct the model
class H2Controller(ModelConstructor):
    """
    A class to represent a Controller model for a hybrid renewable energy system.
    This class provides methods to manage power flows between renewable sources, battery storage, and hydrogen systems.

    Attributes
    parameters : dict
        Dictionary containing control parameters like battery and hydrogen storage limits, and fuel cell efficiency.
    inputs : dict
        Dictionary containing inputs like wind/solar generation, load demand, and storage states.
    outputs : dict
        Dictionary containing calculated outputs like power flows to battery/electrolyzer and hydrogen production.
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
    control(wind_gen, pv_gen, load_dem, soc, h2_soc)
        Manages power flows based on generation, demand and storage states.
    """
    parameters={}
    inputs={'demand1': 0,  # Demand for hydrogen from unit 1 [kg/timestep]
            'demand2': 0,  # Demand for hydrogen from unit 2 [kg/timestep]
            'thermolyzer_out': 0,  # Hydrogen output from the thermolyzer [kg/timestep]
            'compressor_out': 0,  # Hydrogen output from the compressor [kg/timestep]
            'h2_soc1': 0,  # Hydrogen storage 1 state of charge [%]
            'h2_soc2': 0,  # Hydrogen storage 2 state of charge [%]
            }
    outputs={'flow2h2storage1': 0,  # hydrogen flow to hydrogen storage 1 (neg or pos) [kg/timestep]
            'flow2h2storage2': 0,  # hydrogen flow to hydrogen storage 2 (neg or pos) [kg/timestep]
            'valve1_ratio1': 0,  # fraction of hydrogen flow to valve 1 output 1 [%]
            'valve1_ratio2': 0,  # fraction of hydrogen flow to valve 1 output 2 [%]
            'valve2_ratio1': 0,  # fraction of hydrogen flow to valve 2 output 1 [%]
            'valve2_ratio2': 0,  # fraction of hydrogen flow to valve 2 output 2 [%]
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
            including state of charge limits for battery and hydrogen storage,
            and fuel cell efficiency.
        """
        super().__init__(**kwargs)
        


    # define step function
    def step(self, time: int, inputs: dict=None, max_advance: int=900) -> None:  # step function always needs arguments self, time, inputs and max_advance. Max_advance needs an initial value.
        """
        Advances the simulation one time step.
        Args:
            time (float): Current simulation time
            inputs (dict): Dictionary containing input values:
            - wind_gen (float): Wind power generation [kW]
            - pv_gen (float): Solar power generation [kW]
            - load_dem (float): Load demand [kW]
            - soc (float): Battery state of charge [%]
            - h2_soc (float): Hydrogen storage state of charge [%]
            max_advance (int, optional): Maximum time to advance. Defaults to 1.
        Returns:
            float: Next simulation time
        """
        input_data = self.unpack_inputs(inputs)  # make input data easily accessible
        self.time = time
        input_data = self.unpack_inputs(inputs)
        current_time = time * self.time_resolution
        print('from controller %%%%%%%%%%%', current_time)

        results = self.control(demand1=input_data['demand1'],
                                 demand2=input_data['demand2'],
                                 thermolyzer_out=input_data['thermolyzer_out'],
                                 compressor_out=input_data['compressor_out'],
                                 h2_soc1=input_data['h2_soc1'],
                                 h2_soc2=input_data['h2_soc2']
                                )

        self.set_outputs(results)

        # return the time of the next step (time untill current information is valid)
        return time + self._model.time_step_size


    def control(self, demand1: float, demand2: float, thermolyzer_out: float, compressor_out: float, h2_soc1: float, h2_soc2: float) -> dict:
        """
        Checks the state of power flow based on wind and solar energy generation compared to demand,
        and manages power distribution between battery and hydrogen storage systems.

        Parameters
        ----------
        wind_gen : float
            Wind power generation in kilowatts (kW)
        pv_gen : float 
            Solar (photovoltaic) power generation in kilowatts (kW)
        load_dem : float
            Electrical load demand in kilowatts (kW)
        soc : int
            Battery state of charge as a percentage (0-100%)
        h2_soc : int
            Hydrogen storage state of charge as a percentage (0-100%)
        
        Returns
        -------
        re_params : dict
            Dictionary containing power flow parameters:
            - flow2b: Power flow to/from battery (kW)
            - flow2e: Power flow to electrolyzer (kW)
            - dump: Excess power dumped (kW)
            - h2_out: Hydrogen output from fuel cell (kW)
        """
        flow = wind_gen + pv_gen - load_dem  # kW

        if flow < 0:  # means that the demand is not completely met and we need support from battery and fuel cell
            if soc > self.soc_min:  # checking if soc is above minimum. It can be == to soc_max as well.
                self.flow_b = flow
                self.flow_e = 0
                self.h_out = 0

            elif soc <= self.soc_min:
                self.flow_b = 0
                q = 39.4
                self.h_out = (flow / q) / self.fc_eff

                print('Battery Discharged')


        elif flow > 0:  # means we have over generation and we want to utilize it for charging battery and storing hydrogen
            if soc < self.soc_max:
                self.flow_b = flow
                self.flow_e = 0
                self.h_out = 0
            elif soc == self.soc_max:
                self.flow_b = 0
                if h2_soc < self.h2_soc_max:
                    self.flow_e = flow
                    self.dump = 0
                    self.h_out = 0
                elif h2_soc == self.h2_soc_max:
                    self.flow_e = 0
                    self.dump = flow
                    self.h_out = 0

        re_params = {'flow2b': self.flow_b, 'flow2e': self.flow_e, 'dump': self.dump, 'h2_out':self.h_out}
        return re_params
