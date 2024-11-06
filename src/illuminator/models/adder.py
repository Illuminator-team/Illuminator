"""
An example of creating a model for the illuminator.
The model is a simple adder that adds two inputs and 
stores the result in an output.
"""
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

    def step(self, time) -> None:
        self._model.outputs["out1"] = self._model.inputs["in1"] + self._model.inputs["in2"]
        print("result:", self._model.outputs["out1"])

        return time + self._model.time_step_size

    # todo: adopt get_data() as defined by Mosaik

if __name__ == '__main__':
    # Create a model by inheriting from ModelConstructor
    # and implementing the step method
    adder_model = Adder(adder)

    print(adder_model.step(1))