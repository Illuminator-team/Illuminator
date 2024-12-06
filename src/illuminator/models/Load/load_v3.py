from illuminator.builder import IlluminatorModel, ModelConstructor

# Define the model parameters, inputs, outputs...
load = IlluminatorModel(
    parameters={'houses': 1,  # number of houses that determine the total load demand
                'output_type': 'power',  # type of output for consumption calculation ('energy' or 'power')
                },
    inputs={'load': 0},  # incoming energy or power demand per house (kWh) for each time step (15 minutes)
    outputs={'load_dem': 0,  # total energy or power consumption for all houses (kWh) over the time step
             'consumption': 0,  # Current energy or power consumption based on the number of houses and input load (kWh)
            'time': None,  # Current simulation time step in seconds
            'forecast': None  # Forecasted load demand (if applicable, not defined in the code but mentioned in META)
             },
    states={'consumption': 0,
            'time': None,
            'forecast': None
            },
    time_step_size=1,
    time=None
)

# construct the model
class Load(ModelConstructor):
    def __init__(self, **kwargs) -> None:
        # TODO make a generalised way of doing this shit in the ModelConstructor __init__()
        super().__init__(**kwargs)
        self.houses = self._model.parameters.get('houses')
        self.output_type = self._model.parameters.get('output_type')


    def step(self, time, inputs) -> None:
        self.time = time
        # current_time = (self.start +
        #                 pd.Timedelta(time * self.time_resolution,
        #                              unit='seconds'))  # timedelta represents a duration of time
        current_time = time * self.time_resolution
        print('from load %%%%%%%%%%%', current_time)

        # for eid, attrs in inputs.items():

        #     for attr, vals in attrs.items():
        #         self._cache[eid] = self.entities.demand(list(vals.values())[0])
        
        input_data = self.unpack_inputs(inputs)
        eid = list(self.model_entities)[0]  # there is only one entity per simulator, so get the first entity

        self._cache = {}
        self._cache[eid] = self.demand(load=input_data['load'])

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

        if self.output_type == 'energy':
            self.consumption = (self.houses * load) # kWh
        elif self.output_type == 'power':
            self.consumption = (self.houses * load)/60*self.time_resolution # kWh

        re_params = {'load_dem': self.consumption}
        return re_params

if __name__ == '__main__':
    # Create a model by inheriting from ModelConstructor
    # and implementing the step method
    load_model = Load(load)