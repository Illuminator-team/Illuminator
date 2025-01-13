from illuminator.builder import IlluminatorModel, ModelConstructor

class Load(ModelConstructor):
    parameters={'houses': 1,  # number of houses that determine the total load demand
                'output_type': 'power',  # type of output for consumption calculation ('energy' or 'power')
                }
    inputs={'load': 0}  # incoming energy or power demand per house (kWh) for each time step (15 minutes)
    outputs={'load_dem': 0,  # total energy or power consumption for all houses (kWh) over the time step
             'consumption': 0,  # Current energy or power consumption based on the number of houses and input load (kWh)
            'time': None,  # Current simulation time step in seconds
            'forecast': None  # Forecasted load demand (if applicable, not defined in the code but mentioned in META)
             }
    states={'consumption': 0,
            'time': None,
            'forecast': None
            }
    time_step_size=1
    time=None
    

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


    def step(self, time, inputs, max_advance=1) -> None:
        input_data = self.unpack_inputs(inputs)
        self.time = time

        load_in = input_data.get('load', 0)
        results = self.demand(load=load_in)
        self.set_outputs(results)

        return time + self._model.time_step_size
    

    def demand(self, load:float) -> dict:
        """
        Performs calculations of load and returns the selected parameters

        ...

        Parameters
        ----------
        load : float
            Incoming load in kWh at every 15 min interval
            
        Returns
        -------
        re_params : dict
            Collection of parameters and their respective values
        """
        # incoming load is in kWh at every 15 min interval
        # incoming value of load is in kWh
        houses = self._model.parameters.get('houses')
        output_type = self._model.parameters.get('output_type')

        if output_type == 'energy':
            self.consumption = (houses * load) # kWh
        elif output_type == 'power':
            self.consumption = (houses * load)/60*self.time_step_size # kWh

        re_params = {'load_dem': self.consumption}
        return re_params