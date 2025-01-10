from illuminator.builder import IlluminatorModel, ModelConstructor

# Define the model parameters, inputs, outputs...
load = IlluminatorModel(
    parameters={'houses': 1,  # number of houses that determine the total load demand
                'output_type': 'power',  # type of output for consumption calculation ('energy' or 'power')
                },
    inputs={'load': 0},  # incoming energy or power demand per house kW
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

## TODO MODEL DOES NOT MAKE SENSE (INPUTS AND OUTPUTS ARE NOT CERRECTLY DOCUMENTED AND CALCULATED)
class Load(ModelConstructor):
    parameters={'houses': 1,  # number of houses that determine the total load demand
                'output_type': 'power',  # type of output for consumption calculation ('energy' or 'power')
                }
    inputs={'load': 0}  # incoming energy or power demand per house kW
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


    def step(self, time, inputs, max_advance=1) -> None:
        # TODO all step definitions should have max_advance!

        input_data = self.unpack_inputs(inputs)
        self.time = time
        # current_time = (self.start +
        #                 pd.Timedelta(time * self.time_resolution,
        #                              unit='seconds'))  # timedelta represents a duration of time
        current_time = time * self.time_resolution
        print('from load %%%%%%%%%%%', current_time)

        # for eid, attrs in inputs.items():

        #     for attr, vals in attrs.items():
        #         self._cache[eid] = self.entities.demand(list(vals.values())[0])
        
        eid = list(self.model_entities)[0]  # there is only one entity per simulator, so get the first entity

        # self._cache = {}
        # self._cache[eid]
        load_in = input_data.get('load', 0)
        results = self.demand(load=load_in)
        self.set_outputs(results)
        # self._model.outputs['load_dem'] = results['load_dem']
        # self._model.outputs['consumption'] = results['load_dem']

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
        deltaTime = self.time_resolution * self.time_step_size / 60 / 60

        if output_type == 'energy':
            self.consumption = (houses * load) # kW
        elif output_type == 'power':
            self.consumption = (houses * load) * deltaTime # kWh

        re_params = {'load_dem': self.consumption}
        return re_params

if __name__ == '__main__':
    # Create a model by inheriting from ModelConstructor
    # and implementing the step method
    load_model = Load(load)