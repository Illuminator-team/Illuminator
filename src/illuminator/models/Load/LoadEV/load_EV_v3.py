from illuminator.builder import ModelConstructor

class LoadEV(ModelConstructor):
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

    parameters={'houses_case': None,  # number of EVs you want to model
                'houses_data': None,  # number of EVs for which the profile is for
                }
    inputs={'power': 0,
             'n': 0,  # # n is number of EVs charging at a certain point in time (its in the database but unused for now)
            }
    outputs={'load_EV': 0,  #
             }
    states={}
    time_step_size=1
    time=None


    def __init__(self, **kwargs) -> None:
        """
        Initialize Load model with given parameters.

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
        Performs a single simulation time step by calculating EV load demand.

        Parameters
        ----------
        time : float
            Current simulation time in seconds
        inputs : dict
            Dictionary containing input values including 'power' and 'n'
        max_advance : int, optional
            Maximum time step advancement, defaults to 900
            
        Returns
        -------
        float
            Next simulation time step
        """

        input_data = self.unpack_inputs(inputs)
        self.time = time

        load_in = input_data.get('power', 0)
        n = input_data.get('n', 0)
        results = self.demand(power=load_in, n=n)
        self.set_outputs({'load_EV': results['load_EV']})

        return time + self._model.time_step_size


    def demand(self, power:float, n:int) -> dict:
        """
        Calculates total EV load demand based on power per EV and number of EVs.

        Parameters
        ----------
        power : float
            Power consumption per EV in kWh per 15-min interval
        n : int
            Number of EVs charging at current time step
            
        Returns
        -------
        re_params : dict
            Dictionary containing EV load demand and number of EVs
        """
        # incoming load is in kWh at every 15 min interval
        # incoming value of load is in kWh
        if self.houses_case == self.houses_data:
            consumption = power
        else:
            consumption = power * self.houses_case/self.houses_data # scaling if necessary
        re_params = {'load_EV': consumption, 'n': n}
        return re_params
