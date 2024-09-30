from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime

class SimulatorType(Enum):
    TIME_BASED = 'time-based'
    EVENT_BASED = 'event-based'
    HYBRID = 'hybrid'


@dataclass
class ModelConstructor(ABC):
    """ 
    A abstract class for adding models to the Illuminator.
    ...

    Parameters
    ----------

    model_parameters: dict
        Properties of the object being modeled, e.g. material the object is made of
    inputs: dict
        One or more name:data_type pairs to be regarded as inputs to the model.
        Inputs allow users to connect a model to other models.
    outputs: dict
        One or more name:data_type pairs to be regarded as outputs of the model.
        Outputs allow users to connect a model to other models.
    states: dict
        One or more model_parameters, inputs or outputs and their initial value that are of 
        interest for monitoring or logging during a simulation.
    triggers: list
        A flag [input's or output's name] that causes the compute_step method to be called.
        Only relevant when a model is part of an event-based or hybrid simulator.
    public: bool
        ???

    Returns
    -------
    None

    Raises
    ------
    NotImplementedError
        If the compute_step method is not implemented

    Warining
        If triggers are defined for a time-based simulator. After that triggers will be ignored.

    """

    @property
    @abstractmethod
    def model_parameters(self) -> Dict: # properties of the object being modeled, e.g. material the object is made of
        pass

    @property
    @abstractmethod
    def inputs(self) -> Dict:
        # zero or many
        pass

    @property
    @abstractmethod
    def outputs(self) -> Dict:
        # zero or many
        pass

    @property
    @abstractmethod
    def states(self) -> Dict:
        pass

    @property
    def simulator_type(self) -> SimulatorType:
        return SimulatorType.HYBRID

    @property
    def triggers(self) -> List:
        return  [] # default value
    
    @property
    @abstractmethod
    def time_step_size(self) -> int:
        pass

    @property
    def time(self) -> int:
        return 1
    
    def __post_init__(self):
        # triggers are only relevant for event-based or hybrid simulators
        if self.simulator_type == SimulatorType.TIME_BASED and self.triggers is not None:
            raise Warning("Triggers are not relevant for time-based simulators, they will be ignored")
        
        def validate_time_is_positive(self, time: int) -> None:
            if time <= 1:
                raise ValueError("Time must be a positive integer graeter than 1")
        validate_time_is_positive(self.time_step_size)

        def validate_trigger(self, triggers: list[str]) -> None:
            if len(triggers) > 0:
                for t in triggers:
                    if t not in self.inputs or t not in self.outputs:
                        raise ValueError(f"{t} is not a valid trigger")
        
        validate_trigger(self.triggers)

    # public = True  #THIS is relevant only for META # TODO: when using type validation, attributes cannot be changed by the concrete class. We need
    # to find a way to validate this if that is a limiation of dataclasses


    def get_meta(self) -> Dict:
        """
        Returns the model meta data in MoSaik format
        """
        pass
        # TODO: this should be to call the mosaik_api method to create a simulator

    # TODO: this should be part of a test when registering a model in the library
    def validate_args(self, *args) -> None:
        """
        Validates the arguments passed to the compute_step method
        """
        for arg in args:
            if arg not in self.inputs or arg not in self.outputs or arg not in self.states:
                raise ValueError(f"{arg} is not a valid argument")

    @abstractmethod
    def step(self, *args) -> Any:
        """ 
        Defines the conputations that need to be performed in each 
        simulation step.
        Computations must be defined in terms of inputs, outputs and states. 
        """
        # THIS mostly SELF-CONTAINED. This is the method mostly define computatons based on the inputs, outputs and states

        # TODO: valid arguments are inputs, outputs, states,
        # that are defined by the concrete class. We need to write code 
        # to validate this.

        raise NotImplementedError


if __name__ == "__main__":

    # Example of  adding a simple battery model

    class Battery(ModelConstructor):
        """
        A simple battery model
        """

        def model_parameters(self) -> Dict:
            self.inputs = {
                'capacity': 100,  # defaults
                'voltage': 5
            }
        


    battery = Battery()

    print(battery.model_parameters, battery.triggers)
    print(battery.time_step, battery.time)

    print(battery.step(10, 10, 10, 5))