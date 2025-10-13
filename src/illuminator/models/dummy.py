from illuminator.builder import ModelConstructor
import mosaik_api_v3 as mosaik_api

# construct the model
class Dummy(ModelConstructor):
    """
    Dummy model class for demonstration and testing purposes.

    This class serves as a template for implementing simulation models within the Illuminator framework.
    It defines example parameters, inputs, outputs, and states, and can be extended for custom behavior.

    Attributes
    ----------
    parameters : dict
        Dictionary of model parameters.
    inputs : dict
        Dictionary of model inputs.
    outputs : dict
        Dictionary of model outputs.
    states : dict
        Dictionary of internal model states.
    time_step_size : int
        Simulation time step size.

    Returns
    -------
    None
    """
    parameters={'param1': 0,  # example parameter
                'param2': 0,  # example parameter
                }
    inputs={'in1': 20,  # example input
            'in2': 20  # example input
            }
    outputs={'out1': 0,  # example output
             'out2': 0  # example output
             }
    states={'state1': 0,  # example state
            'state2': 0  # example state
        }
    time_step_size=1
    time=None


    def init(self, *args, **kwargs):
        """
        Initialize the Dummy model with specified parameters.

        This method sets up the Dummy model instance using provided keyword arguments,
        initializing parameters, states, and other configuration values.

        Parameters
        ----------
        *args : tuple
            Positional arguments for model initialization.
        **kwargs : dict
            Keyword arguments containing model parameters such as:

        Returns
        -------
        None
        """
        result = super().init(*args, **kwargs)
        # self.out1 = self.parameters.get('out1', 0)
        # self.out2 = self.parameters.get('out2', 0)
        self.state1 = self.parameters.get('param1', 0)
        print("Initialized Dummy with state1:", self.state1)
        # self.state2 = self.states.get('state2', 0)
        return result



    def step(self, time: int, inputs: dict={}, max_advance: int=900) -> None:
        """
        Executes a single simulation step for the Dummy model.

        This method processes the provided inputs for the current timestep, updates internal states,
        and prepares outputs. It is called by the simulation framework at each simulation tick.

        Parameters
        ----------
        time : int
            Current simulation time step.
        inputs : dict, optional
            Dictionary containing input values for the model.
        max_advance : int, optional
            Maximum allowed time step advancement in seconds (default is 900).

        Returns
        -------
        int
            The next simulation time step.
        """
        input_data = self.unpack_inputs(inputs)

        if 'in1' in input_data:
            self.state1 = input_data['in1']

        
        # self.set_states({'soc': self.soc, 'flag': self.flag, 'mod': self.mod}) # set the state of charge and remove it from the results at the same time
        #self.set_outputs({'out1': self.out1, 'out2': self.out2})
        self.set_states({'state1': self.state1})
        #self.set_states({'state1': 0.6})

        return time + self._model.time_step_size


if __name__ == '__main__':
    mosaik_api.start_simulation(Dummy(), 'Dummy Simulator')