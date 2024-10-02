from abc import ABC, abstractmethod
import dataclasses

dataclasses
class Simulation(ABC):
    inputs = []
    outputs = []

    @abstractmethod
    def compute(self):
        """Method to be implemented by each new simulation"""
        pass

# User must implement a new simulation by inheriting from the base class.
class NewSimulation(Simulation):
    inputs = [1, 2]
    outputs = [3, 4]

    def compute(self):
        # Define how this particular simulation works
        return self.inputs[0] + self.inputs[1] * self.outputs[0] + self.outputs[1]

# Instantiate a new simulation
sim = NewSimulation()
print(sim.inputs)
result = sim.compute()
print(result)