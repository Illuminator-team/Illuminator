from illuminator.builder import ModelConstructor

class LoadHeatpump(ModelConstructor):
    """
    Heat pump load model for calculating and scaling demand based on number of houses.

    Takes heat pump load input data and scales it proportionally based on the ratio 
    between target and reference number of houses. Supports direct passthrough when
    house numbers match.

    Parameters
    ----------
    houses_case : int
        Target number of houses to scale demand for
    houses_data : int
        Reference number of houses in the input data
        
    Returns
    -------
    dict
        Dictionary containing scaled heat pump load values
    """

    parameters={'houses_case': 1, 
                'houses_data': None
                }
    inputs={'hp_load': 0}
    outputs={'load_HP': 0,
             }
    states={}
    time_step_size=1
    time=None


    def __init__(self, **kwargs) -> None:
        """
        Initialize heat pump load model with given parameters.

        Parameters
        ----------
        kwargs : dict
            
        Returns
        -------
        None
        """
        super().__init__(**kwargs)
        self.houses_case = self.parameters['houses_case']
        self.houses_data = self.parameters['houses_data']


    def step(self, time: int, inputs: dict=None, max_advance: int=900) -> None:
        """
        Performs a single simulation time step by calculating scaled heat pump load demand.

        Parameters
        ----------
        time : int
            Current simulation time in seconds
        inputs : dict
            Dictionary containing input values including heat pump load data
        max_advance : int, optional
            Maximum time step advancement in seconds, defaults to 900
            
        Returns
        -------
        int
            Next simulation time step in seconds
        """
        input_data = self.unpack_inputs(inputs)
        self.time = time

        load_in = input_data.get('hp_load', 0)
        results = self.demand(hp_load=load_in)
        self.set_outputs(results)

        return time + self._model.time_step_size


    def demand(self, hp_load:float) -> dict:
        """
        Calculates total heat pump load demand from input load and scales based on house ratio.

        Parameters
        ----------
        hp_load : float
            Input heat pump load in kW for reference number of houses
            
        Returns
        -------
        re_params : dict
            Dictionary containing calculated heat pump load value scaled to target houses
        """
        if self.houses_case == self.houses_data:
            consumption = hp_load
        else:
            consumption = hp_load * self.houses_case/self.houses_data # scaling if necessary
        re_params = {'load_HP': consumption}
        return re_params
