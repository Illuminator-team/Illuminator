from illuminator.builder import ModelConstructor

# construct the model
class Controller_StoryMode(ModelConstructor):
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
    parameters={}
    inputs={'physical_connections': []}
    outputs={}
    states={'file_index_Load': 0}

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
        self.file_indeces = {'file_index_Load': 0}


    def step(self, time: int, inputs: dict=None, max_advance: int=900) -> None:  # step function always needs arguments self, time, inputs and max_advance. Max_advance needs an initial value.
        """
        Advances the simulation one time step.
        """
        input_data = self.unpack_inputs(inputs)  # make input data easily accessible
        self.time = time

        if time > 40:
            self.file_indeces['file_index_Load'] = 1
        else:
            self.file_indeces['file_index_Load'] = 0

        self.set_states(self.file_indeces)

        # return the time of the next step (time untill current information is valid)
        return time + self._model.time_step_size