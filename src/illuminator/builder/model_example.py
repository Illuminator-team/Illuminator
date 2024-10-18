"""
This defines a new model
"""
from typing import Any

from illuminator.builder import ModelConstructor

class Adder(ModelConstructor):
    """
    A model that adds things up
    """

    # TODO: revisit the way this is implemented, so that
    # properties are set in the constructor
    @property
    def model_parameters(self):
        return  {
            "a": int,
            "b": int
        }
        
    @property
    def inputs(self):
        return {
            "input1": int,
            "input2": int
        }
    
    @property
    def outputs(self):
        return {
            "output1": int
        }
    
    def states(self):
        return {
            "output1": int
        }
    
    def simulator_type(self):
        return "time-based"
    
    def time_step_size(self):
        return 1
    
    def step(self) -> None:
       self.outputs["output"] = self.inputs["input1"] + self.inputs["input2"]
       return None # None is returned for consistency. What step must do is to compute values that
       # update the states and outputs of the model
    
if __name__ == "__main__":

    import dataclasses as dc
    model = Adder()
    print(model)

