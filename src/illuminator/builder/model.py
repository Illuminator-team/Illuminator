from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class SimulatorType(Enum):
    TIME_BASED = 'time-based'
    EVENT_BASED = 'event-based'
    HYBRID = 'hybrid'








@dataclass
class IlluminatorModel():
    """ A dataclass for defining the properties of a model in the Illuminator.

    Attributes
    ----------

    parameters: dict
        Properties of the object being modeled, e.g. material the object is
        made of.
    inputs: dict
        One or more name:value pairs to be regarded as inputs to the model.
        Inputs allow users to connect a model to other models.
    outputs: dict
        One or more name:value pairs to be regarded as outputs of the model.
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
        The time step size for the simulator.
    time: int
        The current time of the simulation.
    """

    parameters: Dict = field(default_factory=dict)    
    inputs: Optional[Dict] = field(default_factory=dict) 
    outputs: Dict = field(default_factory=dict)
    states: Dict = field(default_factory=dict)
    triggers: Optional[Dict] = field(default_factory=list)
    # simulator_type: SimulatorType = SimulatorType.TIME_BASED
    time_step_size: int = 15   # This is closely related to logic in the step method. Currently, all models have the same time step size (15 minutes). This is a global setting for the simulation, not a model-specific setting.
    time: Optional[datetime] = None  # Shouldn't be modified by the user.
    

    def __post_init__(self):
        self.validate_states()
        self.validate_triggers()
        # self.validate_simulator_type()
    
    @property
    def simulator_meta(self) -> dict:
        """Returns the metadata required by the mosaik API"""
        
        meta = {
            'type': self.simulator_type.value,
            'models': {
                'Model': {
                    'public': True,
                    'params': list(self.parameters.keys()),
                    'attrs': list(self.outputs.keys())
                }
            }}
        return meta

    def validate_states(self):
        """Check if items in 'states' are in parameters, inputs or outputs"""
        for state in self.states:
            if state not in self.parameters and state not in self.inputs and \
                    state not in self.outputs:
                raise ValueError(f"State: {state} must be either a parameter, "
                                 "an input or an output")

    def validate_triggers(self):
        """Check if triggers are in inputs or outputs"""
        for trigger in self.triggers:
            if trigger not in self.inputs and trigger not in self.outputs:
                raise ValueError(f"Trigger: {trigger} must be either an input "
                                 "or an output")

    def validate_simulator_type(self):
        """Check if triggers are defined for time-based and event-based
        simulations only
        """
        if self.simulator_type == SimulatorType.TIME_BASED and self.triggers:
            raise ValueError("Triggers are not allowed in time-based "
                             "simulators")

        if self.simulator_type == SimulatorType.EVENT_BASED and \
                not self.triggers:
            raise ValueError("Triggers are required in event-based simulators")



class ModelConstructor(ABC):
    """A common interface for constructing models in the Illuminator"""

    def __init__(self, model: IlluminatorModel) -> None:
        self._model = model
        self.model_entities = {}
        self._cache = {}

    @abstractmethod
    def step(self) -> None:
        """Defines the computations that need to be performed in each
        simulation step
        """
        pass

    
    def create(self, num: int) -> List:
        """Creates an instance of the model"""
        for i in range(num):
            eid = f"{self._model.simulator_type.value}_{i}"
            self.model_entities[eid] = self._model
        return list(self.model_entities.keys())
    
    def current_time(self): 
        """Returns the current time of the simulation"""
        pass
        # TODO: implement this method





if __name__ == "__main__":

    pass