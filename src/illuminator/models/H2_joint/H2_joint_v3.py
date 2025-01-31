from illuminator.builder import ModelConstructor

# construct the model
class H2Joint(ModelConstructor):
    """
    A class to represent a Valve model for controlling hydrogen flow in a system.
    This class provides methods to manage the flow of hydrogen through the joint.

    Attributes
    ----------
    parameters : dict
        Dictionary containing joint parameters like efficiency.
    inputs : dict
        Dictionary containing inputs like hydrogen input flow and fraction of flow allowed through output 1.
    outputs : dict
        Dictionary containing calculated outputs like hydrogen flow rates through outputs 1 and 2.
    states : dict
        Dictionary containing the state variables of the system.
    time_step_size : int
        Time step size for the simulation.
    time : int or None
        Current simulation time.

    Methods
    -------
    __init__(**kwargs)
        Initializes the Valve model with the provided parameters.
    step(time, inputs, max_advance)
        Simulates one time step of the Valve model.
    calc_flow(h2_in, frac)
        Calculates the flow of hydrogen through the joint based on the input flow and fraction.
    """
    parameters={'joint_eff': 100#,   # efficicency of the joint [%]
                #'max_flow': 0,      # maximum flow rate of the joint [kg/timestep]
                }
    inputs={'h2_in_1': 0,              # h2 input 1
            'h2_in_2': 0               # h2 input 2
            }
    outputs={'out': 0                  # h2 output
             }
    states={}

    # define other attributes
    time_step_size = 1
    time = None

    def __init__(self, **kwargs) -> None:
        """
        Initialize the Valve model with the provided parameters.

        Parameters
        ----------
        kwargs : dict
            Additional keyword arguments to initialize the joint model,
            including joint efficiency.
        """
        super().__init__(**kwargs)
        self.joint_eff = self.parameters['joint_eff']
        # self.max_flow = self.parameters['max_flow']

    def step(self, time: int, inputs: dict=None, max_advance: int=900) -> None:
        """
        Simulates one time step of the Valve model.

        Parameters
        ----------
        time : int
            Current simulation time.
        inputs : dict
            Dictionary containing inputs like wind/solar generation, load demand, and storage states.
        max_advance : int
            Maximum time step size for the simulation.
        """
        input_data = self.unpack_inputs(inputs)
        self.time = time

        result = self.calc_flow(h2_in_1=input_data['h2_in_1'],
                                h2_in_2=input_data['h2_in_2']
                            )
        self.set_outputs(result['out'])

        return time + self.time_step_size

    def calc_flow(self, h2_in_1: float, h2_in_2: float) -> dict:
        """
        Calculate the flow through the joint.

        Parameters
        ----------
        h2_in_1 : float
            Hydrogen input flow from input 1.
        h2_in_2 : float
            Hydrogen input flow from input 2.
        frac : float
            Fraction of the flow that is allowed to pass through output 1.

        Returns
        -------
        dict
            Dictionary containing the calculated outputs like hydrogen output flow.
        """
        out = (h2_in_1 + h2_in_2) * self.joint_eff / 100
        return out
