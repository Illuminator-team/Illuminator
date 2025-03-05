import numpy as np
from illuminator.builder import ModelConstructor

# construct the model
class H2Controller(ModelConstructor):
    """
    A class to represent a Controller model for a hybrid renewable energy system.
    This class provides methods to manage power flows between renewable sources, battery storage, and hydrogen systems.

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
        Simulates one time step of the H2Controller model.
    control(demand1, demandt, thermolyzer_out, h2_soc1, h2_soc2)
        Manages hydrogen flows based on generation, demand and storage.
    store_rest(rest, valve1_ratio1, valve1_ratio3, available_storage1, available_storage2, thermolyzer_out)
        Stores the excess hydrogen.
    """
    parameters={'size_storage1': 0,
                'size_storage2': 0,    
                }
    inputs={'demand1': 0,  # Demand for hydrogen from unit 1 [kg/timestep]
            'demand2': 0,  # Demand for hydrogen from unit 2 [kg/timestep]
            'thermolyzer_out': 0,  # Hydrogen output from the thermolyzer [kg/timestep]
            'h2_soc': 0,  # Hydrogen buffer 1 state of charge [%]
            }
    outputs={'flow2h2storage1': 0,  # hydrogen flow to hydrogen storage 1 (neg or pos) [kg/timestep]
             'dump': 0              # keeps track of shortage/overpoduction in the system [kg/timestep]
            }
    states={'valve1_ratio1': 0,  # fraction of hydrogen flow to valve 1 output 1 [%]
            'valve1_ratio2': 0,  # fraction of hydrogen flow to valve 1 output 2 [%]
            'valve1_ratio3': 0  # fraction of hydrogen flow to valve 1 output 3 [%]
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
        self.size_storage1 = self.parameters['size_storage1']
        self.size_storage2 = self.parameters['size_storage2']
        self.dump = 0

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
        print('from controller %%%%%%%%%%%', self.current_time)
        results = self.control(input_data['demand1'],
                                input_data['demand2'],
                                 thermolyzer_out=input_data['thermolyzer_out'],
                                 h2_soc=input_data['h2_soc']
                                )
        # print(f"DEBUG: results in h2_controller.py: {results}")
        outputs = {}
        outputs['flow2h2storage1'] = results.pop('flow2h2storage1')
        outputs['flow2h2storage2'] = results.pop('flow2h2storage2')
        outputs['dump'] = results.pop('dump')
        self.set_outputs(outputs)
        self.set_states(results)

        # return the time of the next step (time untill current information is valid)
        return time + self._model.time_step_size        

    def control(self, demand1: float, demand2: float, thermolyzer_out: float, h2_soc1: float, h2_soc2: float) -> dict:
        """
        This function executes the control operation. It prioritises direct supply from the 
        thermolzyer and adapts the valve ratios accordingly. In case the storages must be used, 
        they are discharges in such a way that they are equally exploited, again, adapting the 
        valves accordingly. When there is a surplus of hydrogen the two storages are charged to 
        have the same soc.

        Parameters
        ----------
        demand1 : float
            Demand at low pressure [kg/timestep]
        demand2 : float
            Demand at high pressure [kg/timestep]
        thermolyzer_out : float
            Production of the thermolyzer [kg/timestep]
        h2_soc1 : float
            State of charge of low pressure storage [%]
        h2_soc2 : float
            State of charge of high pressure storage [%]

        Returns
        -------
        results : dict
            Dictionary containing parameters:
            - flow2h2storage1: flow required as discharge from the low pressure storage [kg/timestep]
            - flow2h2storage2: flow required as discharge from the high pressure storage [kg/timestep]
            - dump: over- or underproduced hydrogen in the system [kg/timestep]
            - valve1_ratio1: ratio of incoming hydrogen to thermolyzer storage1 [%]
            - valve1_ratio2: ratio of incoming hydrogen to thermolyzer demand1 [%]
            - valve1_ratio3: ratio of incoming hydrogen from thermolyzer to the compressor [%]
        """
        # initialise all valves to zero
        valve1_ratio1 = 0
        valve1_ratio2 = 0
        valve1_ratio3 = 0
        
        tot_demand = demand1 + demand2
        valve1_ratio1 = demand1 / tot_demand
        valve1_ratio2 = demand2 / tot_demand
        
        desired_out = tot_demand
        

        results = { 'dump': self.dump,
                    'valve1_ratio1': valve1_ratio1,
                    'valve1_ratio2': valve1_ratio2,
                    'valve1_ratio3': valve1_ratio3
                    }
        return results