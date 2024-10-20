
from abc import ABC, abstractmethod


class ModelFactory(ABC):
    """ factory method pattern """

    @abstractmethod
    def factory_method(self):
        pass

    def some_operation(self) -> str:

        model = self.factory_method()
        # add some operation
        return "some operation \n"


# Model interface

class IlluminatorModel(ABC):
    """A common interface for all products"""
    

    def __init__(self, parameters: dict, inputs: dict, outputs: dict):
        self.parameters = parameters
        self.inputs = inputs
        self.outputs = outputs
        
    @abstractmethod
    def parameters(self) -> None:
        pass

    @abstractmethod
    def inputs(self) -> None:
        pass

    @abstractmethod 
    def outputs(self) -> None:
        pass

    @abstractmethod
    def step(self) -> None:
        pass

    def __str__(self):
        return self.__dict__.__str__()


class BatteryModel(IlluminatorModel):
    """A model for the battery"""
    
    def __init__(self):
        super().__init__(parameters={'a': 1},
                          inputs= {'in': 2}, 
                          outputs= {'out': 3})
    
    def step(self) -> None:
        """Do something with the inputs and parameters"""
        self._o1 = self._a + self._p1
        self._o2 = self._b + self._p2
        return None
    


if __name__ == "__main__":
    bat = BatteryModel() 
    bat.parameters(1, 2.0)
    print(bat.parameters)