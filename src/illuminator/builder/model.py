from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import illuminator.engine as engine
from mosaik_api_v3 import Simulator

class SimulatorType(Enum):
    TIME_BASED = 'time-based'
    EVENT_BASED = 'event-based'
    HYBRID = 'hybrid'

# TOOD: IMPORTANT 
# each model file must provide a way to run it remotely. In the current implementation,
# that is achieved by including a the folloowing code on the simulator file:
# def main():
#     mosaik_api.start_simulation(eboilerSim(), 'eboiler Simulator')
# if __name__ == "__main__":
#     main()

@dataclass
class IlluminatorModel():
    """ A dataclass for defining the properties of a model in the Illuminator.

    Attributes
    ----------

    parameters: dict
        Properties of the object being modeled, e.g. material the object is
        made of.
    inputs: dict
        One or more name: value pairs to be regarded as inputs to the model.
        Inputs allow users to connect a model to other models.
    outputs: dict
        One or more name: value pairs to be regarded as outputs of the model.
        Outputs allow users to connect a model to other models.
    states: dict
        One or more 'parameters, inputs or outputs' and their initial value
        that are of interest for monitoring or logging during a simulation.
    triggers: list
        A flag [input's or output's name] that causes the `step` method to
        be called.Only relevant when a model is part of an event-based or
        hybrid simulator.
    simulator_type: SimulatorType
        The type of simulator that the model belongs to.
    time_step_size: int
        The time of each simulation step in seconds. Default 900.
    time: int
        The current time of the simulation.
    model_type: str
        A name for the class of model that is being defined. Default 'Model'.
    """

    parameters: Dict = field(default_factory=dict)    
    inputs: Optional[Dict] = field(default_factory=dict) 
    outputs: Dict = field(default_factory=dict)
    states: Dict = field(default_factory=dict)
    triggers: Optional[Dict] = field(default_factory=list)
    simulator_type: SimulatorType = SimulatorType.TIME_BASED
    time_step_size: int = 1   # This is closely related to logic in the step method. 
    # Currently, all models have the same time step size (15 minutes). 
    # This is a global setting for the simulation, not a model-specific setting.
    time: Optional[datetime] = None  # Shouldn't be modified by the user.
    model_type: Optional[str] = "Model" 
    

    def __post_init__(self):
        self._validate_states()
        self._validate_triggers()
        # self.validate_simulator_type()
    
    @property
    def simulator_meta(self) -> dict:
        """Returns the metadata required by the mosaik API"""
        
        meta = {
            'type': self.simulator_type.value,
            'models': {
                self.model_type: { # This must be the name of he model 
                    'public': True,
                    'params': list(self.parameters.keys()),
                    'attrs': list(self.inputs.keys()) + list(self.outputs.keys())
                }
            }}
        return meta

    def _validate_states(self):
        """Check if items in 'states' are in parameters, inputs or outputs"""
        for state in self.states:
            if state not in self.parameters and state not in self.inputs and \
                    state not in self.outputs:
                raise ValueError(f"State: {state} must be either a parameter, "
                                 "an input or an output")

    def _validate_triggers(self):
        """Check if triggers are in inputs or outputs"""
        for trigger in self.triggers:
            if trigger not in self.inputs and trigger not in self.outputs:
                raise ValueError(f"Trigger: {trigger} must be either an input "
                                 "or an output")

    def _validate_simulator_type(self):
        """Check if triggers are defined for time-based and event-based
        simulations only
        """
        if self.simulator_type == SimulatorType.TIME_BASED and self.triggers:
            raise ValueError("Triggers are not allowed in time-based "
                             "simulators")

        if self.simulator_type == SimulatorType.EVENT_BASED and \
                not self.triggers:
            raise ValueError("Triggers are required in event-based simulators")


# COTINUE FROM HERE
# need to find a convenient an easy way to define new models
# Ideas:
# - add model definition as a method of the ModelConstructor class. will it work?

class ModelConstructor(ABC, Simulator):
    """A common interface for constructing models in the Illuminator"""

    def __init__(self, **kwargs) -> None:
        #model: IlluminatorModel
        model_vals = engine.current_model
        model = IlluminatorModel(
                parameters=model_vals.get('parameters', self.parameters), # get the yaml values or the default from the model
                inputs=model_vals.get('inputs', self.inputs),
                outputs=model_vals.get('outputs', self.outputs),
                states=model_vals.get('states', self.states),
                model_type=model_vals.get('type', {}),
                time_step_size=model_vals.get('time_step_size', self.time_step_size)
            )
        super().__init__(meta=model.simulator_meta)
        self._model = model
        self.model_entities = {}
        self.time = 0  # time is an interger wihout a unit

    @abstractmethod
    def step(self, time:int, inputs:dict=None, max_advance:int=None) -> int:
        """Defines the computations that need to be performed in each
        simulation step

        Parameters
        ----------
        time: int
            The current time of the simulation.
        inputs: dict
            The inputs to the model.
        max_advance: int
            Time until the simulator can safely advance its internal time without creating a causality error.
            Optional in most cases.


        Returns
        -------
        int
            The new time of the simulation.

        """
        pass

    def init(self, sid, time_resolution=1, **sim_params):  # can be use to update model parameters set in __init__
        # TODO: from engine.py, time_resolution is never passed

        print(f"running extra init")
        # This is the standard Mosaik init method signature
        self.sid = sid
        self.time_resolution = time_resolution

        # This bit of code is unused.
        # Assuming sim_params is structured as {'sim_params': {model_name: model_data}}
        sim_params = sim_params.get('sim_params', {})
        if len(sim_params) != 1:
            raise ValueError("Expected sim_params to contain exactly one model.")

        # # Extract the model_name and model_data
        # self.model_name, self.model_data = next(iter(sim_params.items()))
        # self.model = self.load_model_class(self.model_data['model_path'], self.model_data['model_type'])
        return self._model.simulator_meta
    
    def create(self, num:int, model:str, **model_params) -> List[dict]: # This change is mandatory. It MUST contain num and model as parameters otherwise it receives an incorrect number of parameters
        """Creates an instance of the model"""
        new_entities = [] # See below why this was created
        for i in range(num): # this seems ok
            eid = f"{self._model.simulator_type.value}_{i}" # this seems ok
            self.model_entities[eid] = self._model # this seems fine
        # return list(self.model_entities.keys()) # I removed this bit for now. Create is expected to return a list of dictionaries
            new_entities.append({'eid': eid, 'type': model})  # So basically, like this. Later on we can look into other alternatives if needed.
        return new_entities
    
    def current_time(self): 
        """Returns the current time of the simulation"""
        pass
        # TODO: implement this method

    def get_data(self, outputs) -> Dict: # TODO remove the print statements here
        """Expose model outputs and states to the simulation environment
        
        Returns
        -------
        Dict
            A dictionary of model outputs and states.
        """
        data = {}
        # print(f"Here are your outputs: {outputs}")
        # for eid, attrs in self._model.outputs.items():
        for eid, attrs in outputs.items():
            # print(f"eid: {eid}, attrs:{attrs}")
            # print(f"self.model_entities: {self.model_entities}")
            model_instance = self.model_entities[eid]
            data[eid] = {}
            for attr in attrs:
                if attr in model_instance.outputs:
                    data[eid][attr] = model_instance.outputs[attr]
                else:
                    data[eid][attr] = model_instance.states[attr]
            # print(f"data: {data}")
        return data


    def unpack_inputs(self, inputs):
        data = {}
        for attrs in inputs.values():
            for attr, sources in attrs.items():
                values = list(sources.values())  # we expect each attribute to just have one sources (only one connection per input)
                if len(values) > 1:
                    raise RuntimeError(f"Why are you passing multiple values {value}to a single input? ")
                data[attr] = values[0]
        return data

if __name__ == "__main__":

    pass