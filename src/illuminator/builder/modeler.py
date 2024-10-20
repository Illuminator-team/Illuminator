

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class IlluminatorModel():
    
    parameters: Dict = field(default_factory=dict)    
    inputs: Dict = field(default_factory=dict)
    outputs: Dict = field(default_factory=dict)
    states: Dict = field(default_factory=list)



class ModelConstructor(ABC):

    def __init__(self, model: IlluminatorModel) -> None:
        self._model = model

    @abstractmethod
    def step(self) -> None:
        """Defines the computations that need to be performed in each simulation step"""
        pass






class Battery(IlluminatorModel):
    """
    A model for the battery
    """
    def __init__(self):
        self._inputs = {
            "input1": 10,
            "input2": 20
        }

    @property
    def parameters(self) -> Dict:
        return {
            "a": 12,
            "b": "hello"
        }
    
    @property # enables inputs can be called as a property in 'step' method
    def inputs(self) -> Dict:
        return self._inputs
    
    @inputs.setter 
    def inputs(self, new_inputs: Dict) -> None:
        self._inputs = new_inputs
    
    def step(self) -> Any:
        return self.inputs["input1"] + self.inputs["input2"]
    


if __name__ == "__main__":

    # usage
    print("Modeling a battery")

    bat = Battery()
    print(bat.parameters)
    print(bat.step())

    bat.inputs = {"input1": 100, "input2": 200}
    print(bat.inputs)
    print(bat.step())

    pass