# from illuminator.builder import ModelConstructor

# class Load(ModelConstructor):
#     """
#     Calculates total load demand based on number of houses and input load.

#     Parameters
#     ----------
#     houses : int
#         Number of houses that determine the total load demand
#     output_type : str
#         Type of output for consumption calculation ('energy' or 'power')

#     Inputs
#     ----------
#     load : float
#         Incoming energy or power demand per house in kW or kWh
    
#     Outputs
#     -------
#     load_dem : float
#         Total energy or power consumption for all houses (kWh) over the time step
#     consumption : float
#         Current energy or power consumption based on the number of houses and input load (kWh)
    
#     States
#     ------
#     time : int
#         Current simulation time in seconds
#     forecast : None
#         Placeholder for future load forecasting functionality
#     """

#     parameters={'houses': 1,  # number of houses that determine the total load demand
#                 'input_type': 'energy',  # type of input for load calculation ('energy' or 'power')
#                 'output_type': 'power',  # type of output for consumption calculation ('energy' or 'power')
#                 }
#     inputs={'load': 0}  # incoming energy or power demand per house kW
#     outputs={'load_dem': 0,  # total energy or power consumption for all houses (kWh) over the time step
#              'consumption': 0,  # Current energy or power consumption based on the number of houses and input load (kWh)
#              'load_signal': 0,
#              'load_battery': 0 
#              }
#     states={'time': None,
#             'forecast': None
#             }
#     time_step_size=1
#     time=None


#     def __init__(self, **kwargs) -> None:
#         """
#         Initialize Load model with given parameters.

#         Parameters
#         ----------
#         kwargs : dict
#             Dictionary containing model parameters and initial states
            
#         Returns
#         -------
#         None
#         """
#         super().__init__(**kwargs)
#         self.consumption = 0
#         self.houses = self._model.parameters.get('houses', 1)
#         self.input_type = self._model.parameters.get('input_type', 'power')
#         self.output_type = self._model.parameters.get('output_type', 'energy')
#         if self.input_type not in ['power', 'energy']:
#             raise ValueError(f"Invalid input_type: {self.input_type}. Must be 'power' or 'energy'.")
#         if self.output_type not in ['power', 'energy']:
#             raise ValueError(f"Invalid output_type: {self.output_type}. Must be 'power' or 'energy'.")


#     def step(self, time: int, inputs: dict=None, max_advance: int=900) -> None:
#         """
#         Performs a single simulation time step by calculating load demand.

#         Parameters
#         ----------
#         time : float
#             Current simulation time in seconds
#         inputs : dict
#             Dictionary containing input values including 'load'
#         max_advance : int, optional
#             Maximum time step advancement, defaults to 1
            
#         Returns
#         -------
#         float
#             Next simulation time step
#         """

#         input_data = self.unpack_inputs(inputs)
#         self.time = time

#         load_in = input_data.get('load', 0)
#         results = self.demand(load=load_in)
#         self.set_outputs(results)

#         return time + self._model.time_step_size


#     def demand(self, load:float) -> dict:
#         """
#         Calculates total load demand based on number of houses and input load.

#         Parameters
#         ----------
#         load : float
#             Input load per house in kW or kWh depending on output_type
            
#         Returns
#         -------
#         re_params : dict
#             Dictionary containing calculated load demand values
#         """
#         # incoming load is in kWh at every 15 min interval
#         # incoming value of load is in kWh
#         deltaTime = self.time_resolution * self.time_step_size / 60 / 60  # in case of 15 min interval, deltaTime = 0.25 h

#         if self.input_type == 'power':  # input load is in kW
#             if self.output_type == 'power':
#                 self.consumption = self.houses * load # kW
#             elif self.output_type == 'energy':
#                 self.consumption = self.houses * load * deltaTime  # kw -> kWh
#         elif self.input_type == 'energy':  # input load is in kW
#             if self.output_type == 'power':
#                 self.consumption = self.houses * load / deltaTime # kWh -> 
#             elif self.output_type == 'energy':
#                 self.consumption = self.houses * load # kWh

#         re_params = {'load_dem': self.consumption}
#         return re_params

from illuminator.builder import ModelConstructor

class Load(ModelConstructor):
    """
    Load model that sums all inputs defined in YAML (arbitrary names/amount).
    Example YAML:
      inputs:
        Load_1:
        Load_2:
        ...
    """

    parameters = {
        'houses': 1,              # optional scalar multiplier; set 1 to disable
        'input_type': 'power',    # 'power' (kW) or 'energy' (kWh)
        'output_type': 'power',   # 'power' or 'energy'
    }
    # No fixed inputs here — they come from YAML:
    inputs = {}
    outputs = {
        'load_dem': 0,
        'consumption': 0,
        'load_signal': 0,
        'load_battery': 0,
    }
    states = {'time': None, 'forecast': None}
    time_step_size = 1
    time = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.houses = self._model.parameters.get('houses', 1)
        self.input_type = self._model.parameters.get('input_type', 'power')
        self.output_type = self._model.parameters.get('output_type', 'power')
        if self.input_type not in ('power', 'energy'):
            raise ValueError("input_type must be 'power' or 'energy'")
        if self.output_type not in ('power', 'energy'):
            raise ValueError("output_type must be 'power' or 'energy'")

    def _sum_messages(self, obj) -> float:
        """Recursively sum any mosaik input message shape."""
        total = 0.0
        if obj is None:
            return 0.0
        if isinstance(obj, dict):
            if 'value' in obj:
                v = obj['value']
                if isinstance(v, (list, tuple)):
                    total += sum(float(x) for x in v if x is not None)
                elif v is not None:
                    total += float(v)
            else:
                for v in obj.values():
                    total += self._sum_messages(v)
        elif isinstance(obj, (list, tuple)):
            for v in obj:
                total += self._sum_messages(v)
        else:
            try:
                total += float(obj)
            except Exception:
                pass
        return total

    def step(self, time: int, inputs: dict = None, max_advance: int = 900):
        self.time = time

        # Take the inner dict for this entity (mosaik gives {eid: {...}})
        entity_inputs = next(iter(inputs.values()), {}) if inputs else {}

        # Sum all input pins you defined in YAML (Load_1, Load_2, …)
        total_in = 0.0
        for attr_name, messages in entity_inputs.items():
            total_in += self._sum_messages(messages)

        # Convert power/energy if requested
        delta_h = (self.time_resolution * self.time_step_size) / 3600.0
        if self.input_type == 'power' and self.output_type == 'energy':
            total_in *= delta_h
        elif self.input_type == 'energy' and self.output_type == 'power':
            total_in /= delta_h

        # Optional scaling by 'houses' (leave houses: 1 to disable)
        total_out = self.houses * total_in

        self.set_outputs({
            'load_dem': total_out,
            'consumption': total_out,
            'load_signal': total_out,
            'load_battery': total_out,
        })
        return time + self._model.time_step_size
