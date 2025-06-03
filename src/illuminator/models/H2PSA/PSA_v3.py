from illuminator.builder import ModelConstructor
import numpy as np

class H2PSA(ModelConstructor):
    """
    A Pressure Swing Adsorption (PSA) model for hydrogen purification.

    This model simulates the operation of a hydrogen PSA unit, applying a specified
    efficiency to the incoming hydrogen stream to determine the purified hydrogen output.

    Parameters
    ----------
    efficiency : float
        Efficiency of the PSA unit as a percentage [%].

    Inputs
    ----------
    h2_in : float
        Hydrogen flow entering the PSA [kg/timestep].

    Outputs
    ----------
    h2_out : float
        Purified hydrogen flow leaving the PSA [kg/timestep].

    States
    ----------
    (none)
    """
    parameters={'efficiency': 100,  # Efficiency of the PSA [%]
                }
    inputs={'h2_in': 0,            # Hydrogen incomming to PSA [kg/timestep]
            }
    outputs={'h2_out': 0,       # flow out of the H2 buffer [kg/timestep]
             }
    states={}
    
    # define other attributes
    time_step_size = 1
    time = None
    
    def __init__(self, **kwargs) -> None:
        """
        Initialize the H2 PSA model.

        Parameters
        ----------
        **kwargs : dict, optional
            Additional keyword arguments passed to the parent ModelConstructor.
        """
        super().__init__(**kwargs)
        self.h2_in = self._model.inputs.get('h2_in', 0)  # Initialize hydrogen input to 0 if not provided
        self.h2_out = 0
        self.efficiency = self._model.parameters.get('efficiency', 100)


    def step(self, time: int, inputs: dict = {}, max_advance: int = 900) -> None:
        """
        Advance the H2 PSA model by one simulation time step.

        Processes the input hydrogen flow for the current timestep, applies the PSA efficiency,
        updates the output flow, and sets the model outputs.

        Parameters
        ----------
        time : int
            Current simulation time.
        inputs : dict, optional
            Dictionary containing input values:
            - h2_in (float): Hydrogen flow entering the PSA [kg/timestep].
        max_advance : int, optional
            Maximum time step size (default is 900).

        Returns
        -------
        int
            Next simulation time step.
        """
        input_data = self.unpack_inputs(inputs)
        self.h2_in = input_data.get('h2_in', self.h2_in) # Default to initial value if not provided
        self.h2_out = self.h2_in * (self.efficiency / 100)  # Calculate the output flow based on efficiency
        self.set_outputs({'h2_out': self.h2_out})
        # self.set_states()

        return time + self._model.time_step_size

        
    