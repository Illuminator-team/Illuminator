from illuminator.builder import IlluminatorModel, ModelConstructor

# construct the model
class Modelname(ModelConstructor):

    # Define the model parameters, inputs, outputs...
    # all parameters will be directly available as attributes
    parameters={'param1': 1,
                'param2': 'value2'
                }
    inputs={'in1': 0
            }
    outputs={'out1': 0
             }
    states={'out1': 0
            }
    
    # define other attributes
    time_step_size=1
    time=None

    # define step function
    def step(self, time, inputs, max_advance=1) -> None:  # step function always needs arguments self, time, inputs and max_advance. Max_advance needs an initial value.


        input_data = self.unpack_inputs(inputs)  # make input data easily accessible
        self.time = time
        eid = list(self.model_entities)[0]  # there is only one entity per simulator, so get the first entity


        # example logic, sets "out1" to be the result of adding input "in1" and parameter "param1"
        self._model.outputs["out1"] = input_data['in1'] + self.param1  


        # return the time of the next step (time untill current information is valid)
        return time + self._model.time_step_size


