import warnings
from abc import ABC, abstractmethod


class IlluminatorModel(ABC): 
    """An interface for constructing new models"""
    
    @abstractmethod
    def _parameters(self) -> None:
        """Defines the parameters of the item being modeled"""
        pass

    @abstractmethod
    def add_inputs(self) -> None:
        """Adds inputs to the model"""
        pass
    
    @abstractmethod
    def add_outputs(self) -> None:
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


# creator
class Creator (ABC):
    """ A creator for the Illuminator models"""

    @abstractmethod
    def factory_method(self):
        pass

    def some_operation(self) -> str:

        model = self.factory_method()
        # add some operation
        return "some operation \n"


# Example of a concrete Creator
## Concrete Creators override the factory method in order to change the resulting
# product's type
class MosaikCreator(Creator): # the factory

    """ A model for the battery"""
    
    def factory_method(self) -> IlluminatorModel:
        # TODO: can this be use to return
        return MosaikCreator()
    

# Concrete Products provide various implementations of the Product interface.

class BatteryModel(IlluminatorModel): # Types of models
    """A model for the battery"""
    
    def __init__(self):
        self._parameters = {}
        self._inputs = {}
        self._outputs = {}
        self._states = []
    
    def add_parameters(self, params: dict = {}) -> None:
        self._parameters.update(params)
    
    def add_inputs(self, inputs: dict = {}) -> None:
        self._inputs.update(inputs)
    
    def add_outputs(self, outputs: dict = {}) -> None:
        self._outputs.update(outputs)
    
    def add_states(self, states: list = []) -> None:
        self._states.extend(states)
    
    def step(self) -> None:
        pass


if __name__ == '__main__':

    parms = {'p1': 1, 'p2': 2.0}
    ins = {'a': int, 'b': float}
    outs = {'c': int, 'd': float}
    states = ['a', 'g']

    def client_code(creator: Creator) -> None:
        print(f"Client: I'm not aware of the creator's class, but it still works.\n"
              f"{creator.some_operation()}", end="")

    client_code(MosaikCreator())