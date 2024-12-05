"""
An example of creating a model for the illuminator.
The model is a simple adder that adds two inputs and 
stores the result in an output.
"""
from typing import List

from illuminator.builder import IlluminatorModel, ModelConstructor

# Define the model parameters, inputs, outputs...
adder = IlluminatorModel(
    parameters={"param1": "addition"},
    inputs={"in1": 10, "in2": 20},
    outputs={"out1": 0},
    states={"out1": 0},
    time_step_size=1,
    time=None
)

# construct the model
class Adder(ModelConstructor):

    def step(self, time, inputs, max_advance=900) -> None:
        print("\n adder:")
        print(f"inputs: {inputs}")
        print(f'internal inputs: {self._model.inputs}')
        for eid, attrs in inputs.items():
            # print(f"eid: {eid}, attrs:{attrs}")
            # print(f"self.model_entities: {self.model_entities}")
            model_instance = self.model_entities[eid]
            for inputname, value in inputs[eid].items():
                # print(f"inputname: {inputname}, value:{value}")
                # print(f"model_instance.inputs[inputname]: {model_instance.inputs[inputname]}")
                if len(value) > 1:
                    raise RuntimeError(f"Why are you passing multiple values {value}to a single input? ")
                else:
                    first_key = next(iter(value))
                    model_instance.inputs[inputname] = value[first_key]
                    # print(f"The dictionary value: {value[first_key]}")

        self._model.outputs["out1"] = self._model.inputs["in1"] + self._model.inputs["in2"] # TODO do we add values internally or based on the current inputs
        print("result:", self._model.outputs["out1"], '\n')

        return time + self._model.time_step_size

    
if __name__ == '__main__':
    # Create a model by inheriting from ModelConstructor
    # and implementing the step method
    adder_model = Adder(adder)

    print(adder_model.step(1))