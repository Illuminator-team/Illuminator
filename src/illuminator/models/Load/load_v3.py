from illuminator.builder import ModelConstructor

class Load(ModelConstructor):
    """
    Calculates total load demand based on number of houses and input load.

    Parameters
    ----------
    load : float
        Input load per house in kW or kWh depending on output_type
        
    Returns
    -------
    re_params : dict
        Dictionary containing calculated load demand values
    """

    parameters={'houses': 1,  # number of houses that determine the total load demand
                'output_type': 'power',  # type of output for consumption calculation ('energy' or 'power')
                }
    inputs={'load': 0}  # incoming energy or power demand per house kW
    outputs={'load_dem': 0,  # total energy or power consumption for all houses (kWh) over the time step
             'consumption': 0,  # Current energy or power consumption based on the number of houses and input load (kWh)
             }
    states={'time': None,
            'forecast': None
            }
    time_step_size=1
    time=None


    def __init__(self, **kwargs) -> None:
        """
        Initialize Load model with given parameters.

        Parameters
        ----------
        kwargs : dict
            Dictionary containing model parameters and initial states
            
        Returns
        -------
        None
        """
        super().__init__(**kwargs)
        self.consumption = 0


    def step(self, time: int, inputs: dict=None, max_advance: int=900) -> None:
        """
        Performs a single simulation time step by calculating load demand.

        Parameters
        ----------
        time : float
            Current simulation time in seconds
        inputs : dict
            Dictionary containing input values including 'load'
        max_advance : int, optional
            Maximum time step advancement, defaults to 1
            
        Returns
        -------
        float
            Next simulation time step
        """

        input_data = self.unpack_inputs(inputs)
        self.time = time

        load_in = input_data.get('load', 0)
        results = self.demand(load=load_in)
        self.set_outputs(results)

        return time + self._model.time_step_size


    def demand(self, load:float) -> dict:
        """
        Calculates total load demand based on number of houses and input load.

        Parameters
        ----------
        load : float
            Input load per house in kW or kWh depending on output_type
            
        Returns
        -------
        re_params : dict
            Dictionary containing calculated load demand values
        """
        # incoming load is in kWh at every 15 min interval
        # incoming value of load is in kWh
        houses = self._model.parameters.get('houses')
        output_type = self._model.parameters.get('output_type')
        deltaTime = self.time_resolution * self.time_step_size / 60 / 60

        if output_type == 'energy':
            self.consumption = houses * load # kW
        elif output_type == 'power':
            self.consumption = houses * load * deltaTime # kWh

        re_params = {'load_dem': self.consumption}
        return re_params
