import warnings
from abc import ABC, abstractmethod

class ModelConstructor(ABC):
    """A interface for constructing new models"""
 
    @property
    @abstractmethod
    def model(self) -> None:
        """Model object"""
        pass

    @abstractmethod
    def define_parameters(self) -> None:
        """Defines the parameters of the item being modeled"""
        pass

    @abstractmethod
    def define_inputs(self) -> None:
        """Adds inputs to the model"""
        pass
    
    @abstractmethod
    def define_outputs(self) -> None:
        """Adds outputs to the model"""
        pass
    
    @abstractmethod
    def add_states(self) -> None:
        """Defines the states of the model"""
        pass
    
    @abstractmethod
    def step(self) -> None:
        """Computations that will be performed in each simulation step"""
        pass


class IlluminatorConstructor(ModelConstructor):
    """A builder for Illuminator models"""

    def __init__(self):
        self.reset() # ensure the model is reset before starting

    def reset(self) -> None:
        self._model = IlluminatorModel()

    @property
    def model(self) -> None:
        # Concrete Builders are supposed to provide their own methods for
        # retrieving results
        model = self._model
        self.reset()
        return model
    
    def define_parameters(self, params: dict = {}) -> None:
        self._model.add_parameters(params)

    def define_inputs(self, inputs: dict = {}) -> None:
        self._model.add_inputs(inputs)

    def define_outputs(self, outputs: dict = {}) -> None:
        self._model.add_outputs(outputs)

    def add_states(self, states: dict = {}) -> None:
        self._model.set_states(states)

    def step(self, **kwargs) -> None:
        # NOTE: maybe this should be a abstract method, or a function must be passed as argument
        self._model.compute(**kwargs)

    def __str__(self) -> str:
        return f'IlluminatorConstructor: {self._model}'


class IlluminatorModel:
    """A model for the Illuminator"""

    def __init__(self):
        self._parameters = {}
        self._inputs = {}
        self._outputs = {}
        self._states = []

    def add_parameters(self, params: dict) -> None:
        self._parameters.update(params)

    def add_inputs(self, inputs: dict) -> None:
        self._inputs.update(inputs)

    def add_outputs(self, outputs: dict) -> None:
        self._outputs.update(outputs)

    def set_states(self, states: list) -> None:
        for state in states:
            # valid states must be in the inputs, outputs or parameters
            valid_states = list(self._inputs.keys()) + list(self._outputs.keys()) + list(self._parameters.keys())
            if state not in valid_states:
                warnings.warn(f'State: {state} is not defined in this model. Valid states must be define in parameters, inputs or outputs.', UserWarning)
        self._states.extend(states)

    def __str__(self) -> str:
        return f'IlluminatorModel: {self._parameters}, {self._inputs}, {self._outputs}, {self._states}'

    def compute(self, **kwargs) -> None:
        # NOTE: maybe this should be a abstract method, or a function must be passed as argument
        return 'Computing...'
    
        
if __name__ == '__main__':

    parms = {'p1': 1, 'p2': 2.0}
    ins = {'a': int, 'b': float}
    outs = {'c': int, 'd': float}
    states = ['a', 'g']
    
    builder = IlluminatorConstructor()

    builder.define_parameters(parms)
    builder.define_inputs(ins)
    builder.define_outputs(outs)
    builder.add_states(states)

    print(builder)
