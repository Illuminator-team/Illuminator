from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from mosaik_api import Simulator
from typing import List, Dict, Optional, Any

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

    """

    # When useing dataclasses, these become instance attributes 
    # they are part of the __init__ method
    model_parameters = {} # properties of the object being modeled, e.g. material the object is made of
    inputs= {} # zero or many
    outputs= {} # zero or many
    states= {} # zero or many

    # TODO: add validation for triggers, it should be a list of strings, and trigger must be in inputs or outputs(?)
    triggers= []

    # TODO: add validation for time_step, it should be a positive integer and not zero
    time_step = 1 
    time = None
    public = True  # TODO: when using type validation, attributes cannot be changed by the concrete class. We need
    # to find a way to validate this if that is a limiation of dataclasses

    def __post_init__(self):
        """
        This method will be called after the instance has been created
        """
        self.step_function = self.compute_step

    def get_meta(self) -> Dict:
        """
        Returns the model meta data in MoSaik format
        """
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
    def compute_step(self, *args) -> Any:
        """ 
        Defines the conputations that need to be performed in each 
        simulation step.
        Computations must be defined in terms of inputs, outputs and states. 
        """

        

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

        model_parameters = {
            'capacity': 1000,
            'voltage': 12
        }

        inputs = {
            'incoming_power': float
        }

        outputs = {
            'outgoing_power': float
        }

        time_step = 1
        time = 100

        states = {
            'current_charge': 10
        }
        
        def compute_step(self, current_charge, incoming_power, outgoing_power, voltage) -> None:
            """
            Updates the current capacity of the battery
            """

            self.states['current_charge'] = current_charge + (incoming_power - outgoing_power)/100

            return self.time + self.time_step
            

    battery = Battery()

    print(battery.model_parameters, battery.triggers)
    print(battery.time_step, battery.time)

    print(battery.compute_step(10, 10, 10, 5))