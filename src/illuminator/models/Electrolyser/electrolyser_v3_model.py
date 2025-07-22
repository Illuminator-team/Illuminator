# from illuminator.builder import IlluminatorModel, ModelConstructor

# class Electrolyzer(ModelConstructor):
    # parameters={
    #         'e_eff' : 70,       # electrolyzer effficiency [%]
    #         'max_p_in' : 10,    # maximum input power [kW]
    #         'max_p_ramp_rate' : 10   # maximum rampup power [kW/s]
    #         }
    # inputs={
    #         'flow2e' : 0        # power flow to the electrolyzer [kW]
    #         }
    # outputs={
    #         'h2_gen' : 0         # hydrogen generation [kg per timestep] 
    #         # 'water_used' : 0    # water required for H2 prodcution [kg/timestep]
    #         }
    # states={},


    # # other attributes
    # time_step_size=1
    # time=None
    # hhv =  286.6                # higher heating value of hydrogen [kJ/mol]
    # mmh2 = 2.02                 # molar mass hydrogen (H2) [gram/mol]
    # p_in_last = 0               # the initial power is initialised to 0 [kW]

    # def __init__(self, **kwargs) -> None:

    #     super().__init__(**kwargs)
    #     self.e_eff = self.parameters['e_eff']
    #     self.max_p_in = self.parameters['max_p_in']
    #     self.max_p_ramp_rate = self.parameters['max_p_ramp_rate']
    #     self.h2_gen = 0

    # def step(self, time: int, inputs: dict=None, max_advance: int=900) -> None:

    #     # print("\nElectrolyzer:")
    #     # print("inputs (passed): ", inputs)
    #     # print("inputs (internal): ", self._model.inputs)
    #     # get input data 
    #     input_data = self.unpack_inputs(inputs)
    #     # print("input data: ", input_data)

    #     self.time = time

    #     current_time = time * self.time_resolution
    #     # print('from electrolyzer %%%%%%%%%%%', current_time)

    #     # calculate generation provided the desired input power [kg/s] 
    #     h_flow = self.generate(
    #         flow2e=input_data['flow2e'],
    #         eff=self.e_eff,
    #         hhv=self.hhv,
    #         mmh2=self.mmh2
    #         ) 
    #     h2_gen = h_flow * self.time_resolution          
    #     # self._model.outputs['h2_gen'] = h2_gen
    #     # print("outputs:", self.outputs)
    #     self.set_outputs({'h2_gen': h2_gen})

    #     return time + self._model.time_step_size

    
    # def ramp_lim(self, flow2e):

    #     """
    #     Limits the input power by the maximimum ramp up limits.

    #     ...

    #     Parameters
    #     ----------
    #     flow2e : float
    #         Input power flow [kW]

    #     Returns
    #     -------
    #     power_in : float
    #         Input power after implemeting ramping limits [kW]
    #     """
    #     # restrict the power input to not increase more than max_p_ramp_rate
    #     # compared to the last timestep
    #     # TODO: check method of using paramters (self. or .get())
    #     p_change = flow2e - self.p_in_last
    #     ramp_limit = self.max_p_ramp_rate * self.time_resolution
    #     if abs(p_change) > ramp_limit:
    #         if p_change > 0:
    #             power_in = self.p_in_last + self.max_p_ramp_rate * self.time_resolution
    #             # power_back = flow2e - power_in 
    #         else:
    #             power_in = self.p_in_last - self.max_p_ramp_rate * self.time_resolution
    #             # power_back = flow2e - power_in
    #     else:
    #         power_in = flow2e
    #     self.p_in_last = power_in
    #     return power_in
        

    # def generate(self, flow2e, eff, hhv, mmh2):
    #     """
    #     Calculates the hydrogen produced per timestep taking the maximum electric power into account.

    #     ...

    #     Parameters
    #     ----------
    #     flow2e : float
    #         Input power flow [kW]
    #     eff : float
    #         Electrolyzer efficiency [%]
    #     hhv : float
    #         Higher heating value of hydrogen [kJ/mol] 
    #     mmh2 : float
    #         Molar mass of hydrogen [g/mol]

    #     Returns
    #     -------
    #     h_out : float
    #         Output flow of hyrdgen [kg/timestep]
    #     """
    #     # restrict the input power to be maximally max_p_in
    #     flow2e = min(flow2e, self.max_p_in) 
    #     power_in = self.ramp_lim(flow2e)
    #     h2_gen = (power_in * eff / 100 * mmh2) / (hhv * 1000)
    #     return h2_gen
from illuminator.builder import IlluminatorModel, ModelConstructor

class Electrolyzer(ModelConstructor):
    
    parameters = {
        'e_eff': 63.59,  # % this is including the BoP losses and conversion losses (AC flow goes intro eletrolyser, converters are inside)
        'max_p_in': 2.45,  # kW this is total power, stack power is 2178.4 W (so for electrochemical process)
        'warm_up_time': 720,  # seconds (12 minutes)
        'warm_up_power': 0.260,  # kW (power during warm-up phase)
        'ramp_up_time': 600,  # seconds (10 minutes)
        'ramp_down_time': 1800,  # seconds (30 minutes)
        'hold_time': 1500,  # seconds (25 minutes)
        'hydrogen_production_rate': 0.04494  # kg/h or 500 NL/h
    }
    inputs = {
        'run_electrolyser': 0,  # signal: 0 or 1
        'production_rate': 0  #rate that electrolyzer is working
    }
    outputs = {
        'flow2e': 0,  # kW (power consumption)
        'flow2e_grid': 0,  # kW (power consumption from grid)
        'flow2c': 0  # kg/timestep (for compressor input)
    }
    states = {
        'el_status': 0,  # one of: 'off', 'warm_up', 'ramp_up', 'on', 'ramp_down'
        'phase_step': 0      # how many timesteps we've been in the current state
    }

    time_step_size = 1  
    time = None

    
    mmh2 = 2.016  # g/mol

    def __init__(self, **kwargs) -> None:

        super().__init__(**kwargs)
        self.e_eff = self._model.parameters.get('e_eff')
        self.max_p_in = self._model.parameters.get('max_p_in')
        self.warm_up_time = self._model.parameters.get('warm_up_time')
        self.warm_up_power = self._model.parameters.get('warm_up_power')
        self.ramp_up_time = self._model.parameters.get('ramp_up_time')
        self.ramp_down_time = self._model.parameters.get('ramp_down_time')
        self.hold_time = self._model.parameters.get('hold_time')
        self.h2_rate_hr = self._model.parameters.get('hydrogen_production_rate')  # kg/h
        self.el_status = self._model.states.get('el_status')
        self.phase_step = self._model.states.get('phase_step')

        self.phase_start_time = None
   
        # self.warm_up_steps = self._model.parameters['warm_up_time'] / self.time_resolution
        # self.ramp_up_steps = self._model.parameters['ramp_up_time'] / self.time_resolution
        # self.ramp_down_steps = self._model.parameters['ramp_down_time'] / self.time_resolution

    def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> None:
        if inputs is None:
            raise ValueError("Inputs cannot be None. Please provide valid input data.")
        input_data = self.unpack_inputs(inputs)
        signal = input_data['run_electrolyser']
        production_rate = input_data['production_rate']
        dt_h = self.time_resolution / 3600  # convert resolution to hours
        lhv = 33.33 # kWh/kg (lower heating value of hydrogen)
        self.time = time
        # flow2e = 0.0
        # flow2c = 0.0
        # === Phase Logic ===
       
        # Check if the signal to run the electrolyzer is active
        if signal == 1:
                # Warm-up phase: Initialize and maintain warm-up power until the warm-up time is reached
                if self.phase_step == 0:  # warm up
                    if self.phase_start_time is None:
                        self.phase_start_time = time
                    flow2e = -self.warm_up_power
                    flow2c = 0
                    if (self.time_resolution >= self.warm_up_time) or (
                        (time - self.phase_start_time) * self.time_resolution >= self.warm_up_time
                    ):
                        self.phase_step = 1  # start ramp up
                        self.phase_start_time = time  # reset for ramp up phase
                
                # Ramp-up phase: Gradually increase power and hydrogen production until maximum is reached
                elif self.phase_step == 1:  # ramp up
                    elapsed = (time - self.phase_start_time) * self.time_resolution  # convert time to seconds
                    ramp_fraction = min(elapsed / self.ramp_up_time, 1.0)
                    self.el_status = 'ramp_up'
                    flow2e = -ramp_fraction * self.max_p_in
                    flow2c = -flow2e / lhv * self.e_eff/100 * dt_h  
                    if ramp_fraction >= 1.0 and elapsed >= self.ramp_up_time:
                        self.phase_step = 2  # on
                
                # On phase: Maintain maximum power and hydrogen production
                elif self.phase_step == 2:  # on
                    if self.el_status != 'on':
                        self.el_status = 'on'
                    flow2e = -production_rate*self.max_p_in
                    flow2c = -flow2e / lhv * self.e_eff/100 * dt_h 
                    self.prev_flow2e = -production_rate * self.max_p_in
                    self.prev_flow2c = -self.prev_flow2e / lhv * self.e_eff/100 * dt_h 
        
        # Check if the signal to stop the electrolyzer is active
        elif signal == 0:
                # Ramp-down phase: Gradually decrease power and hydrogen production until fully off
                if self.phase_step == 2:
                    self.phase_step = 3
                    self.phase_start_time = time

                if self.phase_step == 3:  # ramp down
                    elapsed = (time - self.phase_start_time) * self.time_resolution
                    ramp_fraction = max(1 - (elapsed / self.ramp_down_time), 0)
                    flow2e = -((-1*self.prev_flow2e - 0.6 * self.max_p_in) * ramp_fraction + 0.6 * self.max_p_in)
                    # flow2c = ((self.prev_flow2c - 0.6 * self.h2_rate_hr * dt_h) * ramp_fraction + 0.6 * self.h2_rate_hr * dt_h)
                    flow2c = -flow2e / lhv * self.e_eff/100 * dt_h 

                    if elapsed >= self.ramp_down_time:
                        self.phase_step = 4
                        self.phase_start_time = time

                elif self.phase_step == 4:  # fully off
                    elapsed = (time - self.phase_start_time) * self.time_resolution
                    # flow2e = -0.6 * self.max_p_in
                    # flow2c = 0.6 * self.h2_rate_hr * dt_h
                    if elapsed >= self.hold_time:  # 25 minutes in seconds
                        self.phase_step = 0
                        self.phase_start_time = None
                        flow2e = 0
                        flow2c = 0
                    else:
                        flow2e = -0.6 * self.max_p_in
                        # flow2c = 0.6 * self.h2_rate_hr * dt_h
                        flow2c = -flow2e / lhv * self.e_eff/100 * dt_h 

                elif self.phase_step == 0:  # Turn off completely
                    flow2e = 0
                    flow2c = 0
                    self.phase_step = 0
                    self.phase_start_time = None
                #     if ramp_fraction <= 0 and elapsed >= self.ramp_down_time:
                #         self.phase_step = 0  # fully off
                #         self.phase_start_time = None
                #         flow2e = 0
                #         flow2c = 0
                # elif self.phase_step == 0:
                #     # If not in ramp down, ensure no power is consumed
                #     flow2e = 0
                #     flow2c = 0

        self.set_outputs({
            'flow2e': round(flow2e, 4),
            'flow2e_grid': round(flow2e, 4),  # assuming flow2e_grid is same as flow2e
            'flow2c': round(flow2c, 6)
        })

        self.set_states({
            'el_status': self.el_status,
            'phase_step': self.phase_step
        })

        return time + self._model.time_step_size

