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
        Simulates one time step of the Controller model.
    control(wind_gen, pv_gen, load_dem, soc, h2_soc)
        Manages power flows based on generation, demand and storage states.
    """
    parameters={'size_storage1': 0,
                'size_storage2': 0,
                
                }
    inputs={'demand1': 0,  # Demand for hydrogen from unit 1 [kg/timestep]
            'demand2': 0,  # Demand for hydrogen from unit 2 [kg/timestep]
            'thermolyzer_out': 0,  # Hydrogen output from the thermolyzer [kg/timestep]
            # 'compressor_out': 0,  # Hydrogen output from the compressor [kg/timestep]
            'h2_soc1': 0,  # Hydrogen storage 1 state of charge [%]
            'h2_soc2': 0,  # Hydrogen storage 2 state of charge [%]
            }
    outputs={'flow2h2storage1': 0,  # hydrogen flow to hydrogen storage 1 (neg or pos) [kg/timestep]
             'flow2h2storage2': 0,  # hydrogen flow to hydrogen storage 2 (neg or pos) [kg/timestep]
             'dump': 0              # keeps track of shortage/overpoduction in the system [kg/timestep]
            }
    states={'valve1_ratio1': 0,  # fraction of hydrogen flow to valve 1 output 1 [%]
            'valve1_ratio2': 0,  # fraction of hydrogen flow to valve 1 output 2 [%]
            'valve1_ratio3': 0,  # fraction of hydrogen flow to valve 1 output 3 [%]
            'valve2_ratio1': 0,  # fraction of hydrogen flow to valve 2 output 1 [%]
            'valve2_ratio2': 0,  # fraction of hydrogen flow to valve 2 output 2 [%]
            'valve2_ratio3': 0   # fraction of hydrogen flow to valve 2 output 3 [%]
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

    # define step function
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

        results = self.control(demand1=input_data['demand1'],
                                 demand2=input_data['demand2'],
                                 thermolyzer_out=input_data['thermolyzer_out'],
                                 # compressor_out=input_data['compressor_out'],
                                 h2_soc1=input_data['h2_soc1'],
                                 h2_soc2=input_data['h2_soc2']
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
        Checks the state of power flow based on wind and solar energy generation compared to demand,
        and manages power distribution between battery and hydrogen storage systems.

        Parameters
        ----------
        wind_gen : float
            Wind power generation in kilowatts (kW)
        pv_gen : float 
            Solar (photovoltaic) power generation in kilowatts (kW)
        load_dem : float
            Electrical load demand in kilowatts (kW)
        soc : int
            Battery state of charge as a percentage (0-100%)
        h2_soc : int
            Hydrogen storage state of charge as a percentage (0-100%)
        
        Returns
        -------
        re_params : dict
            Dictionary containing power flow parameters:
            - flow2b: Power flow to/from battery (kW)
            - flow2e: Power flow to electrolyzer (kW)
            - dump: Excess power dumped (kW)
            - h2_out: Hydrogen output from fuel cell (kW)
        """

        # initialise all valves to zero
        valve1_ratio1 = 0
        valve1_ratio2 = 0
        valve1_ratio3 = 0
        valve2_ratio1 = 0
        valve2_ratio2 = 0
        valve2_ratio3 = 0

        self.dump = 0
        rest = 0
        flow2h2storage1 = 0
        flow2h2storage2 = 0
        available_storage1 = self.size_storage1 * h2_soc1 / 100
        available_storage2 = self.size_storage2 * h2_soc2 / 100
        if demand1 > 0 and demand2 > 0:  # if there is demand from both units
            tot_demand = demand1 + demand2

            # # initial setting for the valve for hyrdogen distribution
            # valve1_ratio2 = demand1 / tot_demand * 100 if tot_demand > 0 else 0
            # valve1_ratio3 = demand2 / tot_demand * 100 if tot_demand > 0 else 0

            # demand1_remaining = demand1 - valve1_ratio2 / 100 * thermolyzer_out
            # demand2_remaining = demand2 - valve1_ratio3 / 100 * thermolyzer_out

            # spread storage help over both storages (spread shortage)
            tot_shortage = max(0, (tot_demand - thermolyzer_out))
            short_per_storage = tot_shortage / 2
            
            # theoretical optimal flows after the storages have been used equally (can be negative)
            df1 = np.clip(demand1 - short_per_storage, 0, thermolyzer_out)      # desired flow from valve 1 to the first subsystem
            df2 = np.clip(demand2 - short_per_storage, 0, thermolyzer_out)      # desired flow from valve 1 to the second subsystem

            # initial guess for the valve ratios considering both storages have enough hydrogen or there is no shortage
            if thermolyzer_out > 0:
                valve1_ratio2 = df1 / thermolyzer_out * 100
                valve1_ratio3 = df2 / thermolyzer_out * 100
            short1 = max(0, demand1 - valve1_ratio2 / 100 * thermolyzer_out)
            short2 = max(0, demand2 - valve1_ratio3 / 100 * thermolyzer_out)
            
            
            if short1 > available_storage1:
                # print(f"\n DEBUG: the following is true: short1 > available_storage1 \n")
                if available_storage2 > short2:
                    if available_storage2 > tot_shortage - available_storage1:
                        delta_valve = min((short1 - available_storage1) / thermolyzer_out * 100, 100 - valve1_ratio2, 100 - valve1_ratio3)
                    else:
                        delta_valve = (available_storage2 - short2) / thermolyzer_out *100
                    valve1_ratio2 += delta_valve
                    valve1_ratio3 -= delta_valve
            
            if short2 > available_storage2:
                # print(f"\n DEBUG: the following is true: short2 > available_storage2 \n")
                if available_storage1 > short1:
                    if available_storage1 > tot_shortage - available_storage2:
                        delta_valve = min((short2 - available_storage2 / thermolyzer_out, 100 - valve1_ratio2, 100 - valve1_ratio3))
                    else:
                        delta_valve = (available_storage1 - short1) / thermolyzer_out * 100
                    valve1_ratio2 -= delta_valve
                    valve1_ratio3 += delta_valve
            if available_storage1 >= demand1 - thermolyzer_out * valve1_ratio2/100:
                flow2h2storage1 = -max(demand1 - thermolyzer_out * valve1_ratio2/100, 0)
            else:
                flow2h2storage1 = -available_storage1
            if available_storage2 >= demand2 - thermolyzer_out * valve1_ratio3/100:
                flow2h2storage2 = -max(demand2 - thermolyzer_out * valve1_ratio3/100, 0)
            else:
                flow2h2storage2 = -available_storage2

            # print(f"DEBUG: \n-THIS IS flow2h2storage1: {flow2h2storage1}\n-THIS IS flow2h2storage2:{flow2h2storage2}")

            # if short_per_storage > 0:   # if there is a shortage
            #     if available_storage1 < short_per_storage:
            #         if available_storage2 > 2 * short_per_storage - available_storage1:
            #             delta_valve = (short_per_storage - available_storage1) / thermolyzer_out * 100
            #             valve1_ratio2 += delta_valve
            #             valve1_ratio3 -= delta_valve 
            #         else:
            #             raise ValueError('Not enough hydrogen in both storages to meet the demand')
            #     if available_storage2 < short_per_storage:
            #         if available_storage1 > 2 * short_per_storage - available_storage2:
            #             delta_valve = (short_per_storage - available_storage2) / thermolyzer_out * 100
            #             valve1_ratio2 -= delta_valve
            #             valve1_ratio3 += delta_valve
            #         else:
            #             raise ValueError('Not enough hydrogen in both storages to meet the demand')
            
            if thermolyzer_out > tot_demand:    # overproduction
                rest = thermolyzer_out - tot_demand
                valve1_ratio1, valve1_ratio3 = self.store_rest(rest, valve1_ratio1, valve1_ratio3, available_storage1, available_storage2, thermolyzer_out)
                # valve1_ratio2 -= (valve1_ratio1 + valve1_ratio3)
                valve2_ratio1 = demand2 / ((valve1_ratio3 / 100) * thermolyzer_out) * 100
                valve2_ratio2 = 100 - valve2_ratio1
            else:
                valve2_ratio1 = 100

        elif demand1 > 0 and demand2 <= 0: # if there is demand from unit 1 only
            valve1_ratio2 = 100
            valve2_ratio1 = 100
            if thermolyzer_out > demand1:
                rest = thermolyzer_out - demand1
                valve1_ratio1, valve1_ratio3 = self.store_rest(rest, valve1_ratio1, valve1_ratio3, available_storage1, available_storage2, thermolyzer_out)
                # print(f"DEBUG: these are ratio1 and 3 in demand1: {valve1_ratio1}, {valve1_ratio3}")
                valve1_ratio2 -= (valve1_ratio1 + valve1_ratio3)
                valve2_ratio2 = 100
            else:
                if available_storage1 >= -(thermolyzer_out - demand1):
                    flow2h2storage1 = thermolyzer_out - demand1
                else:
                    flow2h2storage1 = -available_storage1
                    # raise ValueError('Not enough hydrogen in storage1 to meet the demand')
                

        elif demand1 <= 0 and demand2 > 0:  # if there is demand from unit 2 only
            if thermolyzer_out > demand2:
                valve1_ratio3 = demand2 / thermolyzer_out * 100
                # print(f"DEBUG: This is ratio 3 b4 rest calc: {valve1_ratio3}")
                rest = thermolyzer_out - demand2
                valve1_ratio1, valve1_ratio3 = self.store_rest(rest, valve1_ratio1, valve1_ratio3, available_storage1, available_storage2, thermolyzer_out)
                # print(f"DEBUG: these are ratio1, 2, and 3 in demand2: {valve1_ratio1}, {valve1_ratio2}, {valve1_ratio3}")
                # valve1_ratio3 -= (valve1_ratio2 + valve1_ratio3)
                valve2_ratio1 = demand2 / ((valve1_ratio3 / 100) * thermolyzer_out) * 100
                valve2_ratio2 = 100 - valve2_ratio1
            else:
                valve1_ratio3 = 100
                valve2_ratio1 = 100
                if available_storage2 >= -(thermolyzer_out - demand2):
                    flow2h2storage2 = (thermolyzer_out - demand2)
                else:
                    flow2h2storage2 = -available_storage2
                    # raise ValueError('Not enough hydrogen in storage2 to meet the demand')
                

        else: # if there is no demand
            rest = thermolyzer_out
            valve1_ratio1, valve1_ratio3 = self.store_rest(rest, valve1_ratio1, valve1_ratio3, available_storage1, available_storage2, thermolyzer_out)
            valve2_ratio2 = 100

        # print(f"DEBUG: \n -THIS IS flow2h2storage1:{flow2h2storage1} \n -THIS IS flow2h2storage2: {flow2h2storage2} \n -THIS IS available_storage1: {available_storage1} \n --THIS IS available_storage2: {available_storage2}")

        
        if flow2h2storage1 < 0:
            # shortage in storage1
            self.dump += min((valve1_ratio2 / 100 * thermolyzer_out - flow2h2storage1) - demand1, 0)
            print(f"DEBUG: AT TIME {self.current_time} in flow2h2storage1 <= 0:\n dump = {self.dump}")
        
        if available_storage1 + valve1_ratio1/100 * thermolyzer_out > self.size_storage1:
            print(f"DEBUG: availablestorage1:{available_storage1}\n v1r1:{valve1_ratio1},\nsize{self.size_storage1}, \n dump_before:{self.dump}")
            self.dump += available_storage1 + valve1_ratio1/100 * thermolyzer_out - self.size_storage1
            print(f"DEBUG: AT TIME {self.current_time} in overflow1:\n dump = {self.dump}")
     
        if flow2h2storage2 < 0:
            # shortage in storage2
            print(f"-v1r3={valve1_ratio3}\n-v2r1={valve2_ratio1}\n-thermolyzer_out={thermolyzer_out}\n-flow2h2storage2={flow2h2storage2}\n-demand2={demand2}")
            self.dump += min((valve1_ratio3/100 * valve2_ratio1/100 * thermolyzer_out - flow2h2storage2) - demand2, 0)
            print(f"DEBUG: AT TIME {self.current_time} in flow2h2storage2 <= 0:\n dump = {self.dump}")

        if available_storage2 + valve1_ratio3/100 * valve2_ratio2/100 * thermolyzer_out > self.size_storage2:
            self.dump += (available_storage2 + valve1_ratio3/100 * valve2_ratio2/100 * thermolyzer_out - self.size_storage2)
            print(f"DEBUG: AT TIME {self.current_time} in overflow2:\n dump = {self.dump}")

        results = {'flow2h2storage1': flow2h2storage1,
                    'flow2h2storage2': flow2h2storage2,
                    'dump': self.dump,
                    'valve1_ratio1': valve1_ratio1,
                    'valve1_ratio2': valve1_ratio2,
                    'valve1_ratio3': valve1_ratio3,
                    'valve2_ratio1': valve2_ratio1,
                    'valve2_ratio2': valve2_ratio2,
                    'valve2_ratio3': valve2_ratio3
                    }
        return results
            
    
    def store_rest(self, rest, valve1_ratio1, valve1_ratio3, available_storage1, available_storage2, thermolyzer_out):
        delta_storage = abs(available_storage1 - available_storage2)
        if available_storage1 > available_storage2: # if storage1 has more hydrogen than storage2
            if rest < delta_storage:                # push all to storage2
                f2s1 = 0
                f2s2 = rest
            else:                                   # resolve difference
                f2s1 = (rest - delta_storage) / 2 
                f2s2 = (rest + delta_storage) / 2
        elif available_storage1 < available_storage2:   # if storage2 has more hydrogen than storage1
            if rest < delta_storage:                    # push all to storage1
                f2s1 = rest
                f2s2 = 0
            else:                                       # resolve difference
                f2s1 = (rest + delta_storage) / 2
                f2s2 = (rest - delta_storage) / 2
        else:   # divide equally
            f2s1 = rest / 2
            f2s2 = rest / 2

        d_valve1_ratio1 = f2s1 / thermolyzer_out * 100 # the additional percentage of hydrogen flow to storage1
        d_valve1_ratio3 = f2s2 / thermolyzer_out * 100 # the additional percentage of hydrogen flow to storage2
        
        valve1_ratio1 += d_valve1_ratio1
        valve1_ratio3 += d_valve1_ratio3

        # if available_storage1 + f2s1 > self.size_storage1:
        #     self.dump += available_storage1 + f2s1 - self.size_storage1
        # if available_storage2 + f2s2 > self.size_storage2:
        #     self.dump += available_storage2 + f2s2 - self.size_storage2
        return valve1_ratio1, valve1_ratio3

    # def control(self, demand1: float, demand2: float, thermolyzer_out: float, compressor_out: float, h2_soc1: float, h2_soc2: float) -> dict:
    #     """
    #     Checks the state of power flow based on wind and solar energy generation compared to demand,
    #     and manages power distribution between battery and hydrogen storage systems.

    #     Parameters
    #     ----------
    #     wind_gen : float
    #         Wind power generation in kilowatts (kW)
    #     pv_gen : float 
    #         Solar (photovoltaic) power generation in kilowatts (kW)
    #     load_dem : float
    #         Electrical load demand in kilowatts (kW)
    #     soc : int
    #         Battery state of charge as a percentage (0-100%)
    #     h2_soc : int
    #         Hydrogen storage state of charge as a percentage (0-100%)
        
    #     Returns
    #     -------
    #     re_params : dict
    #         Dictionary containing power flow parameters:
    #         - flow2b: Power flow to/from battery (kW)
    #         - flow2e: Power flow to electrolyzer (kW)
    #         - dump: Excess power dumped (kW)
    #         - h2_out: Hydrogen output from fuel cell (kW)
    #     """

    #     # initialise all valves to zero
    #     valve1_ratio1 = 0
    #     valve1_ratio2 = 0
    #     valve1_ratio3 = 0
    #     valve2_ratio1 = 0
    #     valve2_ratio2 = 0
    #     valve2_ratio3 = 0
    #     rest = 0
    #     flow2h2storage1 = 0
    #     flow2h2storage2 = 0

    #     if demand1 > 0 and demand2 > 0:  # if there is demand from both units
    #         tot_demand = demand1 + demand2

    #         # # initial setting for the valve for hyrdogen distribution
    #         # valve1_ratio2 = demand1 / tot_demand * 100 if tot_demand > 0 else 0
    #         # valve1_ratio3 = demand2 / tot_demand * 100 if tot_demand > 0 else 0

    #         # demand1_remaining = demand1 - valve1_ratio2 / 100 * thermolyzer_out
    #         # demand2_remaining = demand2 - valve1_ratio3 / 100 * thermolyzer_out

    #         # spread storage help over both storages (spread shortage)
    #         tot_shortage = max(0, (tot_demand - thermolyzer_out))
    #         short_per_storage = tot_shortage / 2
            
    #         df1 = demand1 - short_per_storage    # desired flow from valve 1 to the first subsystem
    #         df2 = demand2 - short_per_storage    # desired flow from valve 1 to the second subsystem

    #         # initial guess for the valve ratios considering both storages have enough hydrogen or there is no shortage
    #         valve1_ratio2 = df1 / thermolyzer_out * 100 if thermolyzer_out > 0 else 0
    #         valve1_ratio3 = df2 / thermolyzer_out * 100 if thermolyzer_out > 0 else 0

    #         if short_per_storage > 0:   # if there is a shortage
    #             if available_storage1 < short_per_storage:
    #                 if available_storage2 > 2 * short_per_storage - available_storage1:
    #                     delta_valve = (short_per_storage - available_storage1) / thermolyzer_out * 100
    #                     valve1_ratio2 += delta_valve
    #                     valve1_ratio3 -= delta_valve 
    #                 else:
    #                     raise ValueError('Not enough hydrogen in both storages to meet the demand')
    #             if available_storage2 < short_per_storage:
    #                 if available_storage1 > 2 * short_per_storage - available_storage2:
    #                     delta_valve = (short_per_storage - available_storage2) / thermolyzer_out * 100
    #                     valve1_ratio2 -= delta_valve
    #                     valve1_ratio3 += delta_valve
    #                 else:
    #                     raise ValueError('Not enough hydrogen in both storages to meet the demand')
            
    #         if thermolyzer_out > tot_demand:    # overproduction
    #             rest = thermolyzer_out - tot_demand
    #             valve1_ratio1, valve1_ratio3 = self.store_rest(rest, valve1_ratio1, valve1_ratio3)
    #             valve1_ratio2 -= (valve1_ratio1 + valve1_ratio3)
    #             valve2_ratio1 = demand2 / ((valve1_ratio3 / 100) * thermolyzer_out) * 100
    #             valve2_ratio2 = 100 - valve2_ratio1
    #         else: # demand is exactyl the same as the output of the thermolyzer
    #             rest = 0

    #     elif demand1 > 0 and demand2 <= 0: # if there is demand from unit 1 only
    #         valve1_ratio2 = 100
    #         if thermolyzer_out > demand1:
    #             rest = thermolyzer_out - demand1
    #             valve1_ratio1, valve1_ratio3 = self.store_rest(rest)
    #             valve1_ratio2 -= (valve1_ratio1 + valve1_ratio3)
    #             valve2_ratio2 = 100
    #         else:
    #             if available_storage1 >= thermolyzer_out - demand1:
    #                 flow2h2storage1 = -(thermolyzer_out - demand1)
    #             else:
    #                 raise ValueError('Not enough hydrogen in storage1 to meet the demand')
    #             rest = 0

    #     elif demand1 <= 0 and demand2 > 0:  # if there is demand from unit 2 only
    #         valve1_ratio3 = 100
    #         if thermolyzer_out > demand2:
    #             rest = thermolyzer_out - demand2
    #             valve1_ratio1, valve1_ratio3 = self.store_rest(rest, valve1_ratio1, valve1_ratio3)
    #             valve1_ratio1 -= (valve1_ratio2 + valve1_ratio3)
    #             valve2_ratio2 = 100
    #         else:
    #             if available_storage2 >= thermolyzer_out - demand2:
    #                 flow2h2storage2 = -(thermolyzer_out - demand2)
    #             else:
    #                 raise ValueError('Not enough hydrogen in storage2 to meet the demand')
    #             rest = 0

    #     else: # if there is no demand
    #         self.store_rest(thermolyzer_out)
    #         valve2_ratio2 = 100

    #     results = {'flow2h2storage1': flow2h2storage1,
    #                 'flow2h2storage2': flow2h2storage2,
    #                 'valve1_ratio1': valve1_ratio1,
    #                 'valve1_ratio2': valve1_ratio2,
    #                 'valve1_ratio3': valve1_ratio3,
    #                 'valve2_ratio1': valve2_ratio1,
    #                 'valve2_ratio2': valve2_ratio2,
    #                 'valve2_ratio3': valve2_ratio3
    #                 }
    #     return results
            

    # def store_rest(self, rest, valve1_ratio1, valve1_ratio3, available_storage1, available_storage2):
    #     delta_storage = abs(available_storage1 - available_storage2)
    #     if available_storage1 > available_storage2: # if storage1 has more hydrogen than storage2
    #         if rest < delta_storage:                # push all to storage2
    #             f2s1 = 0
    #             f2s2 = rest
    #         else:                                   # resolve difference
    #             f2s1 = (rest - delta_storage) / 2 
    #             f2s2 = (rest + delta_storage) / 2
    #     elif available_storage1 < available_storage2:   # if storage2 has more hydrogen than storage1
    #         if rest < delta_storage:                    # push all to storage1
    #             f2s1 = rest
    #             f2s2 = 0
    #         else:                                       # resolve difference
    #             f2s1 = (rest + delta_storage) / 2
    #             f2s2 = (rest - delta_storage) / 2
    #     else:   # divide equally
    #         f2s1 = rest / 2
    #         f2s2 = rest / 2

    #     d_valve1_ratio1 = f2s1 / thermolyzer_out * 100 # the additional percentage of hydrogen flow to storage1
    #     d_valve1_ratio3 = f2s2 / thermolyzer_out * 100 # the additional percentage of hydrogen flow to storage2

    #     # check if the new valve ratio =< 100 and if not adjust distribution
    #     if valve1_ratio1 + d_valve1_ratio1 > 100:
    #         surplus = valve1_ratio1 + d_valve1_ratio1 - 100
    #         valve1_ratio1 = 100
    #         if valve1_ratio3 + d_valve1_ratio3 + surplus > 100:
    #             valve1_ratio3 = 100
    #         else:
    #             valve1_ratio3 += (d_valve1_ratio3 + surplus)
    #     else:
    #         valve1_ratio1 += d_valve1_ratio1
        
    #     if valve1_ratio3 + d_valve1_ratio3 > 100:
    #         surplus = valve1_ratio3 + d_valve1_ratio3 - 100
    #         valve1_ratio3 = 100
    #         if valve1_ratio1 + d_valve1_ratio1 + surplus > 100:
    #             valve1_ratio1 = 100
    #         else:
    #             valve1_ratio1 += (d_valve1_ratio1 + surplus)
    #     else:
    #         valve1_ratio3 += d_valve1_ratio3

    #     return valve1_ratio1, valve1_ratio3
    


    # def control2(self, demand1: float, demand2: float, thermolyzer_out: float, compressor_out: float, h2_soc1: float, h2_soc2: float) -> dict:
        
    #     # Initilize all valves to zero
    #     v1r1 = 0
    #     v1r2 = 0
    #     v1r3 = 0
    #     v2r1 = 0
    #     v2r2 = 0 
    #     v2r3 = 0

    #     # Initialize the flow to the storages to zero
    #     flow2h2storage1 = 0
    #     flow2h2storage2 = 0
        

    #     tot_demand = demand1 + demand2
    #     available_storage1 = h2_soc1 * self.storage_capacity1
    #     available_storage2 = h2_soc2 * self.storage_capacity2
    #     tot_available_storage = available_storage1 + available_storage2

    #     if demand1 > 0 and demand2 > 0: # if there is demand from both units
    #         v1r1 = 0
    #         v1r2 = demand1 / tot_demand * 100
    #         v1r3 = demand2 / tot_demand * 100
    #         v2r1 = 100
    #         flow2h2storage1 = -(demand1 - v1r2 / 100 * thermolyzer_out)
    #         flow2h2storage2 = -(demand2 - (v1r3 / 100) * (v2r1 / 100) * thermolyzer_out)
    #     elif demand1 > 0 and demand2 <= 0: # if there is demand from unit 1 only
    #         v1r1 = 0
    #         v1r2 = 100
    #         v1r3 = 0
    #         flow2h2storage1 = -(demand1 - v1r2 / 100 * thermolyzer_out)
    #     elif demand2 > 0 and demand1 <= 0: # if there is demand from unit 2 only
    #         v1r1 = 0
    #         v1r2 = 0
    #         v1r2 = 100
    #         flow2h2storage2 = -(demand2 - v1r2 / 100 * thermolyzer_out)
    #     else: # if there is no demand
    #         # prioritize flow to lowest soc
    #         v1r1 = available_storage2 / tot_available_storage * 100
    #         v1r2 = 0
    #         v1r3 = available_storage1 / tot_available_storage * 100

    #     results = {'flow2h2storage1': flow2h2storage1,
    #                 'flow2h2storage2': flow2h2storage2,
    #                 'valve1_ratio1': v1r1,
    #                 'valve1_ratio2': v1r2,
    #                 'valve1_ratio3': v1r3,
    #                 'valve2_ratio1': v2r1,
    #                 'valve2_ratio2': v2r2,
    #                 'valve2_ratio3': v2r3
    #                 }
    #     return results









        # Disregard all below for now   


        # # This is for the upper part of the system (subsystem 1)
        
           
        # if demand1 > 0 or demand2 > 0:  # if there is demand
        #     valve1_ratio1 = 0  # valve ratio to storage1 is set to 0%
        #     valve2_ratio1 = 0  # valve ratio to storage2 is set to 0%
        #     initial_valve1_ratio2 = thermolyzer_out / demand1 * 100
        #     initial_valve1_ratio3 = thermolyzer_out / demand2 * 100
        #     if initial_valve1_ratio2 + initial_valve1_ratio3 > 100:  # if the sum of the valve ratios is greater than 100
        #         valve1_ratio2 = initial_valve1_ratio2 / (initial_valve1_ratio2 + initial_valve1_ratio3) * 100
        #         valve1_ratio3 = 100 - valve1_ratio2
        #     else:
        #         valve1_ratio2 = initial_valve1_ratio2
        #         valve1_ratio3 = initial_valve1_ratio3

        #     for _ in range(100): # max iterations 
        #         storage_list = []
        #         df1 = valve1_ratio2 / 100 * thermolyzer_out   # direct flow to joint1
        #         df2 = valve1_ratio3 / 100 * thermolyzer_out * compressor_eff   # direct flow to joint2
        #         demand1_remaining = demand1 - df1      
        #         demand2_remaining = demand2 - df2   
        #         if (h2_soc1 < h2_soc_min and demand1_remaining > 0) or demand1_remaining > max_output_storage1:
        #             valve1_ratio2 += 1
        #             valve1_ratio3 = 100 - 1
        #         else:
        #             flow2h2storage1 = -demand1_remaining

        #         if (h2_soc2 < h2_soc_min and demand2_remaining > 0) or demand2_remaining > max_output_storage2:
        #             valve1_ratio3 += 1
        #             valve1_ratio2 = 100 - 1
        #         else:
        #             flow2h2storage2 = -demand2_remaining

        #         sorage_list.



        #     while demand1_remaining > 0 or demand2_remaining > 0:  # while there is still demand
        #         if h2_soc1 > self.h2_soc_min and demand1 <= storage_max_out:
        #             flow2h2storage1 = -demand1_remaining
        #             demand1_remaining = 0
        #         else:
        #             flow2h2storage1 = 0     # No h2 possible from storage1
                    
                
                    




        # if demand1_remaining > 0:                    # if direct flow is not enough to meet the demand   
        #     if h2_soc1 > self.h2_soc_min:           
        #         flow2h2storage1 = -demand1_remaining # ask the storage to provide the remaining demand
        #     else:                                   # if the storage is fully discharged
        #         flow2h2storage1 = 0                 # no flow from storage  
        #         valve1_ratio1 = 0                   # the valve to storage1 is set to 0              
        #         valve1_ratio2 = thermolyzer_out / demand1    # valve ratio adapted to facilitate the direct flow

        # # This is for the lower part of the system (subsystem 2)
        # valve2_ratio1 = 100                             # valve ratio to demand2 is set to 100%          
        # df2 = valve2_ratio2 / 100 * compressor_out       # direct flow to joint2
        # demand2_remaining = demand2 - df2               # demand remaing after direct flow to joint2 (prioritising direct flow)
        # if demand2_remaining > 0:                       # if direct flow is not enough to meet the demand
        #     if h2_soc2 > self.h2_soc_min:                # if the storage is not fully discharged
        #         flow2h2storage2 = -demand2_remaining     # ask the storage to provide the remaining demand
        #     else:                                       # if the storage is fully discharged
        #         flow2h2storage2 = 0                      # no flow from storage
        #         valve1_ratio1 = 0                        # the valve to storage1 is set to 0
        #         valve1_ratio3 = thermolyzer_out / demand2 * 100  # valve ratio adapted to facilitate the direct flow
        #         # TODO the above is not accounting for compresor losses
            
                
                


        # # This is in case of 0 demand
        # if demand1_remaining and demand2_remaining <=0:           # if the direct flow is enough to meet the demand
        #     valve1_ratio2 = 0                       # No direct flow to load 1 necessary so =0
        #     if h2_soc2 > h2_soc1:                   # recharge storages based on the lowest soc
        #         valve1_ratio1 = 100                 # valve ratio to storage1 is set to 100%
        #         valve1_ratio3 = 0                   # valve ratio to storage2 is set to 0%   
        #     elif h2_soc1 > h2_soc2:
        #         valve1_ratio3 = 100                 # valve ratio to subsystem 2 is set to 100%
        #         valve2_ratio1 = 0                   # valve ratio to demand2 is set to 0%
        #         valve2_ratio2 = 100                 # valve ratio to storage2 is set to 100%
        #     else:                                   # if both storages have the same soc treat both equal
        #         valve1_ratio1 = 50                  # valve ratio to storage1 is set to 50%
        #         valve1_ratio3 = 50                  # valve ratio to subsystem 2 is set to 50%


        
        # if flow < 0:  # means that the demand is not completely met and we need support from battery and fuel cell
        #     if soc > self.soc_min:  # checking if soc is above minimum. It can be == to soc_max as well.
        #         self.flow_b = flow
        #         self.flow_e = 0
        #         self.h_out = 0

        #     elif soc <= self.soc_min:
        #         self.flow_b = 0
        #         q = 39.4
        #         self.h_out = (flow / q) / self.fc_eff

        #         print('Battery Discharged')


        # elif flow > 0:  # means we have over generation and we want to utilize it for charging battery and storing hydrogen
        #     if soc < self.soc_max:
        #         self.flow_b = flow
        #         self.flow_e = 0
        #         self.h_out = 0
        #     elif soc == self.soc_max:
        #         self.flow_b = 0
        #         if h2_soc < self.h2_soc_max:
        #             self.flow_e = flow
        #             self.dump = 0
        #             self.h_out = 0
        #         elif h2_soc == self.h2_soc_max:
        #             self.flow_e = 0
        #             self.dump = flow
        #             self.h_out = 0

        # re_params = {'flow2b': self.flow_b, 'flow2e': self.flow_e, 'dump': self.dump, 'h2_out':self.h_out}
        # return re_params
