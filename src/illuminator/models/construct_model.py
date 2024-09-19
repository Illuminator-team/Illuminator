from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

META = {
    'type': 'time-based',
    'models': {
        'SSM_Example': {
            'public': True,
            'params': ['soc', 'capacity'], # declare what attributes in the model can be written to
            'attrs': ['requested_power_flow', 'effective_power_flow', 'soc'], # declare what attributes in the model can be read from
        },
    },
}

class SimulatorType(Enum):
    TIME_BASED = 'time-based'
    EVENT_BASED = 'event-based'
    HYBRID = 'hybrid'


@dataclass
class IlluminatorModel(ABC):
    """ A common interface for adding energy models to the Illuminator.
    This class combines the creation of model and simulators for the 
    Mosaik engine.

    Parameters:
    """

    # TODO:the ideal solution provides a single interface for creating a model and its simulator
    
    # meta
    model_name: str 
    inputs: list
    outputs: list
    parameters: list # variables which values can be set when instantiating the model (can this be always considered inputs?)
    states: list
    simulator_type: SimulatorType = SimulatorType.TIME_BASED
    public: bool = True
    attrs: list  # model properties that can be read from (can these be always considered outputs?)


    @abstractmethod
    def create(self, *args):
        """ Create a new model instance. """
        pass
    
    
    @abstractmethod
    def step(self):
        """ Define the model step function. """
        pass

    @abstractmethod
    def ge_data(self):
        """ Get data from the model. """
        pass

