from abc import ABC, abstractmethod
from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class IlluminatorModel():
    """ A dataclass for defining the properties of a model in the Illuminator."""
    
    parameters: Dict = field(default_factory=dict)    
    inputs: Dict = field(default_factory=dict)
    outputs: Dict = field(default_factory=dict)
    states: Dict = field(default_factory=list)
    triggers: List = field(default_factory=list)

    def __post_init__(self):
        self.validate_states()

    def validate_states(self):
        """Check if items in 'states' are in parameters, inputs or outputs"""
        for state in self.states:
            if state not in self.parameters and state not in self.inputs and state not in self.outputs:
                raise ValueError(f"State: {state} must be either a parameter, an inputs or an output")
            
    


class ModelConstructor(ABC):

    def __init__(self, model: IlluminatorModel) -> None:
        self._model = model

    @abstractmethod
    def step(self) -> None:
        """Defines the computations that need to be performed in each simulation step"""
        pass




if __name__ == "__main__":

    # usage
    print("Modeling a battery")

    battery = IlluminatorModel(
        parameters={"material": "lithium"},
        inputs={"voltage":60},
        outputs={"voltage": 20},
        states={"voltage": 10}
    )


    
    class BatteryModel(ModelConstructor):

        def step(self) -> None:
            return self._model.inputs["voltage"] - self._model.outputs["voltage"]
    

    battery_model = BatteryModel(battery)

    battery.inputs["voltage"] = 300
    
    print(battery_model.step())
    pass