import datetime

class Multiplier:
    def __init__(self, inputs:dict={}, outputs:dict={}, parameters:dict={}, states:dict={}, step_size:int=1, time:datetime.datetime=None):
        self.inputs = inputs
        self.outputs = outputs
        self.parameters = parameters
        self.states = states
        self.step_size = step_size
        self.time = time

    def step(self):
        """
        A simple multiplier model.
        Every step, it multiplies its internal product (state) by a multiplier (parameter).
        The product is then set to "Out1" output.
        """
        self.states["Product"] = self.states["Product"] + self.parameters["Multiplier"]
        self.outputs["Out1"] = self.states["Product"]
        
