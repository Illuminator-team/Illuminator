"""
An example of creating a model for the illuminator
"""
from illuminator.builder import IlluminatorModel, ModelConstructor

# step 1: defin model properties
battery = IlluminatorModel(
    parameters={"material": "lithium"},
    inputs={"voltage": 60},
    outputs={"voltage": 20},
    states={"voltage": 10}
)


# step 2: create a model by inheriting from ModelConstructor
# and implementing the step method
class BatteryModel(ModelConstructor):

    def step(self) -> None:
        return self._model.inputs["voltage"] - self._model.outputs["voltage"]


# step 3: create an instance of the model
battery_model = BatteryModel(battery)

# step 3: properties can be overriden
battery.inputs["voltage"] = 300

# step 4: run the model
print(battery_model.step())
pass
