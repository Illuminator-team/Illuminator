from illuminator.builder import ModelConstructor

class GridConnection(ModelConstructor):
    """
    Grid connection model that monitors power flows and sets warning flags for grid congestion.
    
    This model tracks power flows through a grid connection point and sets warning flags when
    pre-defined capacity limits are exceeded. It uses tolerance and critical thresholds as 
    percentages of the total connection capacity.

    Parameters
    ----------
    connection_capacity : float
        Maximum power capacity of the grid connection (kW)
    tolerance_limit : float
        Threshold for warning flag as fraction of connection capacity (e.g. 0.8 = 80%)
    critical_limit : float
        Threshold for critical flag as fraction of connection capacity (e.g. 0.9 = 90%)
    
    Inputs
    ----------
    dump : float
        Power flow through grid connection (kW, negative for export)
    
    Outputs
    ----------
    None

    States
    ----------
    flag_critical : int
        Flag indicating critical limit exceeded (1) or not (0)
    flag_warning : int
        Flag indicating warning limit exceeded (1) or not (0)
    """

    parameters={'connection_capacity': None,  #
                'tolerance_limit': None,  #
                'critical_limit': None
                }
    inputs={'dump': 0}  #
    outputs={}
    states={'flag_critical': None,
            'flag_warning': None
            }
    time_step_size=1
    time=None


    def __init__(self, **kwargs) -> None:
        """
        Initialize grid connection model with capacity and limit parameters.

        Parameters
        ----------
        kwargs : dict
            Dictionary containing connection_capacity, tolerance_limit,
            
        Returns
        -------
        None
        """
        super().__init__(**kwargs)
        self.connection_capacity = self.parameters['connection_capacity']
        self.tolerance_limit = self.parameters['tolerance_limit']
        self.critical_limit = self.parameters['critical_limit']


    def step(self, time: int, inputs: dict=None, max_advance: int=900) -> None:
        """
        Performs a single simulation time step by checking grid connection limits.

        Parameters
        ----------
        time : float
            Current simulation time in seconds
        inputs : dict
            Dictionary containing input values including 'dump' (power flow to grid)
        max_advance : int, optional
            Maximum time step advancement, defaults to 900
            
        Returns
        -------
        float
            Next simulation time step
        """

        input_data = self.unpack_inputs(inputs)
        self.time = time

        dump = input_data.get('dump', 0)
        results = self.check_limits(dump=dump)
        self.set_states(results)

        return time + self._model.time_step_size


    def check_limits(self, dump) -> dict:
        """
        Checks if power flow exceeds grid connection limits and sets warning flags.

        Parameters
        ----------
        dump : float
            Power flow to the grid in kW (negative values for export)
            
        Returns
        -------
        re_params : dict
            Dictionary containing warning flag states
        """
        #dump = power to the grid in kW

        if (-dump >= (self.critical_limit * self.connection_capacity) or
                dump <= -(self.critical_limit * self.connection_capacity)):
            flag_critical = 1
            flag_warning = 1
        elif (-dump >= (self.tolerance_limit * self.connection_capacity) or
              dump <= -(self.tolerance_limit * self.connection_capacity)):
            flag_critical = 0
            flag_warning = 1
        else:
            flag_critical = 0
            flag_warning = 0
        re_params = {'flag_critical': flag_critical, 'flag_warning': flag_warning}
        return re_params
