"""
An example of creating a model for the illuminator
"""

from illuminator.builder import IlluminatorModel, ModelConstructor

# step 1: define model properties
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
print(battery_model)

# step 4: properties can be overriden
battery.inputs["voltage"] = 300

# step 5: run the model
print(battery_model.step())
pass


# # New PV model
# import pandas as pd
# import itertools

# pv_adapter = IlluminatorModel(
#     parameters={"panel_data": None,
#                 'm_tilt': None,
#                 'm_az': None,
#                 'cap': None,
#                 'sim_start': None,
#                 'output_type': None
#                 },
#     inputs={
#         'G_Gh': None,
#         'G_Dh': None,
#         'G_Bn': None,
#         'Ta': None,
#         'hs': None,
#         'FF': None,
#         'Az': None
#         },

#     outputs={"pv_gen": None, "total_irr": None},
#     states={"voltage": 10}
# )


# class NewPvAdapter(ModelConstructor):

#     def step(self, time, inputs) -> None:
#          # in this method, we call the python file at every data interval and perform the calculations.
#         current_time = (self.start + pd.Timedelta(time * self.time_resolution,
#                                                   unit='seconds'))  # timedelta represents a duration of time
#         print('from pv %%%%%%%%%', current_time)
#         # print('#inouts: ', inputs)
#         for eid, attrs in inputs.items():
#             # print('#eid: ', eid)
#             # print('#attrs: ', attrs)
#             # and relate it with the information in mosaik document.
#             v = []  # we create this empty list to hold all the input values we want to give since we have more than 2
#             for attr, vals in attrs.items():

#                 # print('#attr: ', attr)
#                 # print('#vals: ', vals)
#                 # inputs is a dictionary, which contains another dictionary.
#                 # value of U is a list. we need to combine all the values into a single list. But is we just simply
#                 #   append them in v, we have a nested list, hence just 1 list. that creates a problem as it just
#                 #   gives all 7 values to only sun_az in the python model and we get an error that other 6 values are missing.
#                 u = list(vals.values())
#                 # print('#u: ', u)
#                 v.append(u)  # we append every value of u to v from this command.
#             # print('#v: ', v)

#             # the following code helps us to convert the nested list into a simple plain list and we can use that simply
#             v_merged = list(itertools.chain(*v))
#             # print('#v_merged: ', v_merged)
#             self._cache[eid] = self.model_entities[eid].connect(v_merged[0], v_merged[1], v_merged[2], v_merged[3],
#                                                           v_merged[4], v_merged[5], v_merged[6]) # PV1
#             # print(self._cache)
#             # print('# cache[eid]: ', self._cache[eid])
#     # the following code desnt work because it just put one value 7 times :/! Dumb move
#                     # self._cache[eid] = self.entities[eid].connect(u, u, u, u, u, u, u)
#         return None