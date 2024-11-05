import datetime

class Adder:
    def __init__(self, inputs:dict={}, outputs:dict={}, parameters:dict={}, states:dict={}, step_size:int=1, time:datetime.datetime=None):
        self.inputs = inputs
        self.outputs = outputs
        self.parameters = parameters
        self.states = states
        self.step_size = step_size
        self.time = time

    def step(self):
        """
        A simple adder model.
        The output "Out1" is the sum of inputs "In1" and "In2".
        """
        self.outputs["Out1"] = self.inputs["In1"] + self.inputs["In2"]