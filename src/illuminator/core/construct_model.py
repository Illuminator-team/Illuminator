from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from mosaik_api import Simulator

class SimulatorType(Enum):
    TIME_BASED = 'time-based'
    EVENT_BASED = 'event-based'
    HYBRID = 'hybrid'

# NOTE: I have also inherited from the mosaik_api.Simulator class to integrate this model
# This seems naïve to me. Lots of redundancy with defining which methods are mandatory.
# As for the: the models created seem to have a wide variety of attributes and parameters that are defined.
# In addition, the naming convection of the methods created in them is also non-existant
@dataclass
class IlluminatorModel(Simulator, ABC):
    """ 
    A common interface for adding energy models to the Illuminator.
    This class combines the creation of model and simulators for the Mosaik engine.

    ...

    Parameters
    ----------
    simulator_type: SimulatorType.TIME_BASED
        Defines how the simulator is advanced through time and whether its attributes are persistent in time or transient
    model_name: str
        The name of the model
    public: bool
        Determines whether a model can be instantiated by a user 
    parameters: list 
        Variables which values can be set when instantiating the model (can this be always considered inputs?)
    attrs: list 
        Model properties that can be read from (can these be always considered outputs?)
    trigger: list 
        Attribute names that cause the simulator to be stepped when another simulator provides output which is connected to one of those.
        Empty if no triggers.
    inputs: list
        ???
    outputs: list
        ???
    states: list
        ???
    """

    # TODO:the ideal solution provides a single interface for creating a model and its simulator

    ### meta data ###
    model_name: str
    parameters: list # variables which values can be set when instantiating the model (can this be always considered inputs?)
    attrs: list  # model properties that can be read from (can these be always considered outputs?)
    trigger: list

    inputs: list
    outputs: list
    states: list

    simulator_type: SimulatorType = SimulatorType.TIME_BASED
    public: bool = True
    #################

    @classmethod
    def __test__(cls, subclass):
        return hasattr(subclass, "__init__")

    def __post_init__(self):
        """
        Post-init method which creates and initializes the metadata used by mosaik_api
        """
        META = {
            'type': self.simulator_type,
            'models': {
                self.model_name: {
                    'public': self.public,
                    'params': self.parameters,
                    'attrs': self.attrs, 
                    'trigger': self.trigger
                },
            },
        }
        super().__init__(META)
    
    @abstractmethod
    def init(self, sid, time_resolution, *args):
        """ Initialize the simulator with the ID `sid` and pass the `time_resolution` and additional parameters sent by mosaik. """
        raise NotImplementedError

    @abstractmethod
    def create(self, num, model, *args):
        """ Create `num` instances of `model` using the provided additional arguments """
        raise NotImplementedError

    @abstractmethod
    def step(self, time, inputs, max_advance):
        """ 
        Perform the next simulation step from time `time` using input values
        from `inputs` and return the new simulation time (the time at which
        `step()` should be called again) 
        """
        raise NotImplementedError

    @abstractmethod
    def get_data(self, outputs):
        """ Return the data for the requested outputs """
        raise NotImplementedError