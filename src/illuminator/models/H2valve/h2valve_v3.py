from illuminator.builder import ModelConstructor

# construct the model
class H2Valve(ModelConstructor):
    """
    A class to represent a Valve model for controlling hydrogen flow in a system.
    This class provides methods to manage the flow of hydrogen through the valve.

    Attributes
    ----------
    parameters : dict
        Dictionary containing valve parameters like efficiency.
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
    calc_flow(h2_in, ratio1, ratio2, ratio3)
        Calculates the flow of hydrogen through the valve based on the input flow and fraction.
    """
    parameters={'valve_eff': 100#,   # efficicency of the valve [%]
                #'max_flow': 0,      # maximum flow rate of the valve [kg/timestep]
                }
    inputs={'h2_in': 0,              # h2 input
            'ratio1' : 0,            # fraction of the flow that is allowed to pass through output 1 [%]
            'ratio2' : 0,            # fraction of the flow that is allowed to pass through output 2 [%]
            'ratio3' : 0             # fraction of the flow that is allowed to pass through output 3 [%]
            }
    outputs={'out1': 0,             # h2 output 1
             'out2': 0,             # h2 output 2
             'out3': 0              # h2 output 3
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
            Additional keyword arguments to initialize the valve model,
            including valve efficiency.
        """
        super().__init__(**kwargs)
        self.valve_eff = self.parameters['valve_eff']
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
        print(f"DEBUG: This is input data: {input_data}")
        results = self.calc_flow(h2_in=input_data['h2_in'], 
                                 ratio1=input_data['ratio1'],
                                 ratio2=input_data['ratio2'],
                                 ratio3=input_data['ratio3']
                                 )
        self.set_outputs(results)

        return time + self.time_step_size
    


    def calc_flow(self, h2_in: float, ratio1: float, ratio2: float, ratio3: float) -> dict:
        """
        Calculate the flow through the valve.

        Parameters
        ----------
        h2_in : float
            Hydrogen input flow rate.
        ratio1 : float
            Fraction of the flow that is allowed to pass through output 1.
        ratio2 : float
            Fraction of the flow that is allowed to pass through output 2.
        ratio3 : float
            Fraction of the flow that is allowed to pass through output 3.

        Returns
        -------
        dict
            Dictionary containing the calculated outputs like hydrogen flow rates through outputs 1 and 2.
        """
        tot_out = h2_in * self.valve_eff / 100
        out1 = ratio1 / 100 * tot_out
        out2 = ratio2 / 100 * tot_out
        out3 = ratio3 / 100 * tot_out
        result = {'out1': out1, 'out2': out2, 'out3': out3}
        return result
        
