from illuminator.builder import ModelConstructor

class GridConnection(ModelConstructor):
    # """
    # Grid connection model that monitors power flows and sets warning flags for grid congestion.
    
    # This model tracks power flows through a grid connection point and sets warning flags when
    # pre-defined capacity limits are exceeded. It uses tolerance and critical thresholds as 
    # percentages of the total connection capacity.

    # Parameters
    # ----------
    # connection_capacity : float
    #     Maximum power capacity of the grid connection (kW)
    # tolerance_limit : float
    #     Threshold for warning flag as fraction of connection capacity (e.g. 0.8 = 80%)
    # critical_limit : float
    #     Threshold for critical flag as fraction of connection capacity (e.g. 0.9 = 90%)
    
    # Inputs
    # ----------
    # dump : float
    #     Power flow through grid connection (kW, negative for export)
    
    # Outputs
    # ----------
    # None

    # States
    # ----------
    # flag_critical : int
    #     Flag indicating critical limit exceeded (1) or not (0)
    # flag_warning : int
    #     Flag indicating warning limit exceeded (1) or not (0)
    # """

    # parameters={'connection_capacity': None,  #
    #             'tolerance_limit': None,  #
    #             'critical_limit': None
    #             }
    # inputs={'dump': 0}  #
    # outputs={}
    # states={'flag_critical': None,
    #         'flag_warning': None
    #         }
    # time_step_size=1
    # time=None


    # def __init__(self, **kwargs) -> None:
    #     """
    #     Initialize grid connection model with capacity and limit parameters.

    #     Parameters
    #     ----------
    #     kwargs : dict
    #         Dictionary containing connection_capacity, tolerance_limit,
            
    #     Returns
    #     -------
    #     None
    #     """
    #     super().__init__(**kwargs)
    #     self.connection_capacity = self.parameters['connection_capacity']
    #     self.tolerance_limit = self.parameters['tolerance_limit']
    #     self.critical_limit = self.parameters['critical_limit']


    # def step(self, time: int, inputs: dict=None, max_advance: int=900) -> None:
    #     """
    #     Performs a single simulation time step by checking grid connection limits.

    #     Parameters
    #     ----------
    #     time : float
    #         Current simulation time in seconds
    #     inputs : dict
    #         Dictionary containing input values including 'dump' (power flow to grid)
    #     max_advance : int, optional
    #         Maximum time step advancement, defaults to 900
            
    #     Returns
    #     -------
    #     float
    #         Next simulation time step
    #     """

    #     input_data = self.unpack_inputs(inputs)
    #     self.time = time

    #     dump = input_data.get('dump', 0)
    #     results = self.check_limits(dump=dump)
    #     self.set_states(results)

    #     return time + self._model.time_step_size


    # def check_limits(self, dump) -> dict:
    #     """
    #     Checks if power flow exceeds grid connection limits and sets warning flags.

    #     Parameters
    #     ----------
    #     dump : float
    #         Power flow to the grid in kW (negative values for export)
            
    #     Returns
    #     -------
    #     re_params : dict
    #         Dictionary containing warning flag states
    #     """
    #     #dump = power to the grid in kW

    #     if (-dump >= (self.critical_limit * self.connection_capacity) or
    #             dump <= -(self.critical_limit * self.connection_capacity)):
    #         flag_critical = 1
    #         flag_warning = 1
    #     elif (-dump >= (self.tolerance_limit * self.connection_capacity) or
    #           dump <= -(self.tolerance_limit * self.connection_capacity)):
    #         flag_critical = 0
    #         flag_warning = 1
    #     else:
    #         flag_critical = 0
    #         flag_warning = 0
    #     re_params = {'flag_critical': flag_critical, 'flag_warning': flag_warning}
    #     return re_params

    parameters = {
        'connection_capacity': 15,  # kW
        'tolerance_limit': 0.8,     # -
        'critical_limit': 0.9       # -
    }
    inputs = {
        'load_dem': 0,            # kW
        'pv_gen': 0,              # kW
        'flow2b':0,
        'flow2e_grid': 0,
        'eflow2c': 0,              # kW (electrolyser consumption)
        'p_out_fuelcell_grid': 0       # kW (fuel cell generation)
    }
    outputs = {
        'grid_flow': 0            # kW (positive = import, negative = export)
    }
    states = {
        'flag_critical': 0,
        'flag_warning': 0
    }
    time_step_size = 1
    time = None

    def __init__(self, **kwargs) -> None:
        """
        Initialize grid connection model with parameters for connection capacity and limits.

        Parameters
        ----------
        kwargs : dict
            Dictionary containing model parameters.
        """
        super().__init__(**kwargs)
        self.connection_capacity = self._model.parameters.get('connection_capacity')
        self.tolerance_limit = self._model.parameters.get('tolerance_limit')
        self.critical_limit = self._model.parameters.get('critical_limit')
        self.flag_critical = self._model.states.get('flag_critical')
        self.flag_warning = self._model.states.get('flag_warning')

    def step(self, time: int, inputs: dict = None, max_advance: int = 900):
        input_data = self.unpack_inputs(inputs)
        load = input_data['load_dem']
        pv = input_data['pv_gen']
        flow2b = input_data['flow2b']
        flow2e = input_data['flow2e_grid']
        flow2c = input_data['eflow2c']  # ecompressor consumption
        fc = input_data['p_out_fuelcell_grid']

        grid_flow = load - pv - flow2e - fc - flow2b - flow2c  # 0.235W for Balance of Plant (BoP) added

        crit_thres = self.parameters['connection_capacity'] * self.parameters['critical_limit']
        warn_thres = self.parameters['connection_capacity'] * self.parameters['tolerance_limit']

        abs_flow = abs(grid_flow)
        flag_critical = 1 if abs_flow >= crit_thres else 0
        flag_warning = 1 if abs_flow >= warn_thres else 0

        self.set_outputs({'grid_flow': round(grid_flow, 3)})
        self.set_states({'flag_critical': flag_critical, 'flag_warning': flag_warning})

        return time + self._model.time_step_size