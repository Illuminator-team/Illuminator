import numpy as np
from illuminator.builder import ModelConstructor

# construct the model
class H2Controller2(ModelConstructor):
    """
    A class to represent a Controller model for a hybrid renewable energy system.
    This class provides methods to manage flows in and out of a buffer.

    Attributes
    parameters : dict
        Dictionary containing control parameters like battery and hydrogen storage limits, and fuel cell efficiency.
    inputs : dict
        Dictionary containing inputs like wind/solar generation, load demand, and storage states.
    outputs : dict
        Dictionary containing calculated outputs like power flows to battery/electrolyzer and hydrogen production.
    states : dict
        Dictionary containing the state variables of the system.
    time_step_size : int
        Time step size for the simulation.
    time : int or None
        Current simulation time.

    Methods
    __init__(**kwargs)
        Initializes the Controller model with the provided parameters.
    step(time, inputs, max_advance)
        Simulates one time step of the H2Controller2 model.
    control(demand1, demandt, thermolyzer_out, h2_soc1, h2_soc2)
        Manages hydrogen flows based on generation, demand and storage.
    """
    parameters={'dummy': 0}
    inputs={'demand1': 0,  # Demand for hydrogen from unit 1 [kg/timestep]
            'demand2': 0,  # Demand for hydrogen from unit 2 [kg/timestep]
            'thermolyzer_out': 0,  # Hydrogen output from the thermolyzer [kg/timestep]
            'buffer_available_h2': 0, # available h2 for discharge in buffer [kg]
            'buffer_free_capacity': 0 # h2 that can be stored in buffer before being full [kg]
            }
    outputs={'dump': 0,              # keeps track of shortage/overpoduction in the system [kg/timestep]
             'buffer_in': 0,        # input presented to the buffer [kg/timestep]
             'desired_out': 0       # desired output of the buffer [kg/timestep]
            }
    states={'valve1_ratio1': 0,  # fraction of hydrogen flow to valve 1 output 1 [%]
            'valve1_ratio2': 0,  # fraction of hydrogen flow to valve 1 output 2 [%]
            'valve1_ratio3': 0   # fraction of hydrogen flow to valve 1 output 3 [%]
            }

    # define other attributes
    time_step_size = 1
    time = None

    def __init__(self, **kwargs) -> None:
        """
        Initialize the Controller model with the provided parameters.

        Parameters
        ----------
        kwargs : dict
            Additional keyword arguments to initialize the controller model,
            including state of charge limits for battery and hydrogen storage,
            and fuel cell efficiency.
        """
        super().__init__(**kwargs)

    def step(self, time: int, inputs: dict=None, max_advance: int=900) -> None:  # step function always needs arguments self, time, inputs and max_advance. Max_advance needs an initial value.
        """
        Advances the simulation one time step.

        Parameters
        ----------
        time : int
            Current simulation time.
        inputs : dict, optional
            Dictionary containing input values:
            - demand1 (float): Demand for hydrogen from unit 1 [kg/timestep]
            - demand2 (float): Demand for hydrogen from unit 2 [kg/timestep]
            - thermolyzer_out (float): Hydrogen output from the thermolyzer [kg/timestep]
            - compressor_out (float): Hydrogen output from the compressor [kg/timestep]
            - h2_soc1 (float): Hydrogen storage 1 state of charge [%]
            - h2_soc2 (float): Hydrogen storage 2 state of charge [%]
        max_advance : int, optional
            Maximum time to advance. Defaults to 900.

        Returns
        -------
        int
            Next simulation time.
        """
        input_data = self.unpack_inputs(inputs)  # make input data easily accessible
        self.time = time
        self.current_time = time * self.time_resolution
        # print('from controller %%%%%%%%%%%', self.current_time)
        results = self.control(input_data['demand1'],
                                input_data['demand2'],
                                thermolyzer_out=input_data['thermolyzer_out'],
                                buffer_available_h2=input_data['buffer_available_h2'], 
                                buffer_free_capacity=input_data['buffer_free_capacity']
                                )
                                
        # print(f"DEBUG: results in h2_controller.py: {results}")
        outputs = {}
        outputs['dump'] = results.pop('dump')
        outputs['buffer_in'] = results.pop('buffer_in')
        outputs['desired_out'] = results.pop('desired_out')
        self.set_outputs(outputs)
        self.set_states(results)

        # return the time of the next step (time untill current information is valid)
        return time + self._model.time_step_size        

    def control(self, demand1: float, demand2: float, thermolyzer_out: float, buffer_available_h2: float, buffer_free_capacity: float) -> dict:
        """
        This function executes the control operation. Based on how full the hydrogen buffer is and the combination of 
        demand and production, it controls the buffer.

        Parameters
        ----------
        demand1 : float
            Demand [kg/timestep]
        demand2 : float
            Demand [kg/timestep]
        thermolyzer_out : float
            Production of the thermolyzer [kg/timestep]
        buffer_available_h2 : float
            Amount of hydrogen that can be discharged from the buffer [kg]
        buffer_free_capacity : float
            Amount of hydrogen that can be charged before reaching full soc [kg]

        Returns
        -------
        results : dict
            Dictionary containing parameters:
            - dump: over hydrogen in the system [kg/timestep]
            - valve1_ratio1: ratio of incoming hydrogen going to demand 1 [%] 
            - valve1_ratio2: ratio of incoming hydrogen going to demand 2 [%]
            - valve1_ratio3: unused [%]
            - buffer_in: hydrogen that appears at the input of the buffer [kg/timestep]
            - desired_out: amount of hydrogen demanded at the output of the buffer [kg/timestep]

        """
        # initialise all valves to zero
        valve1_ratio1 = 0
        valve1_ratio2 = 0
        valve1_ratio3 = 0
        dump = 0
        tot_demand = demand1 + demand2
        # print(f'DEBUG: This is tot_demand as seen from controller: {tot_demand}')
        if tot_demand > 0:  # avoid division by 0
            valve1_ratio1 = demand1 / tot_demand * 100
            valve1_ratio2 = demand2 / tot_demand * 100
        desired_out = tot_demand
        buffer_in = thermolyzer_out
        net_flow = buffer_in - desired_out  # pos for charging, neg for discharging

        if net_flow > buffer_free_capacity:
            dump = thermolyzer_out - buffer_free_capacity
            buffer_in -= dump   # what is not dumped goes into the buffer

        elif net_flow < -buffer_available_h2:
            # print(f"DEBUG: In controller: net_flow < -buffer_available_h2, namely buffer_available={buffer_available_h2}")
            desired_out = buffer_in + buffer_available_h2
            # desired_out = buffer_available_h2
                             
        # print(f'DEBUG: This is desired_out as seen from controller: {desired_out}')
        results = { 'dump': dump,
                    'valve1_ratio1': valve1_ratio1,
                    'valve1_ratio2': valve1_ratio2,
                    'valve1_ratio3': valve1_ratio3,
                    'buffer_in': buffer_in,
                    'desired_out': desired_out
                    }
        return results