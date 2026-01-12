
from illuminator.builder import IlluminatorModel, ModelConstructor

class Electrolyzer(ModelConstructor):
    
    parameters = {
        'e_eff': 63.59,  # % this is including the BoP losses and conversion losses
        'max_p_in': 2.45,  # kW this is total power
        'warm_up_time': 900,  # seconds (15 minutes) - CHANGED FROM 720
        # 'warm_up_power': 0.260,  # kW (power during warm-up phase)
        'ramp_up_time': 900,  # seconds (15 minutes) - CHANGED FROM 600
        'ramp_down_time': 900,  # seconds (15 minutes) - CHANGED FROM 1800
        'hold_time': 1800,  # seconds (30 minutes) - CHANGED FROM 1500
        # 'hydrogen_production_rate': 0.04494  # kg/h or 500 NL/h
    }
    inputs = {
        'run_electrolyser': 0,  # signal: 0 or 1
        'production_rate': 0  # rate that electrolyzer is working
    }
    outputs = {
        'flow2e': 0,  # kW (power consumption)
        'flow2e_grid': 0,  # kW (power consumption from grid)
        'flow2c': 0  # kg/timestep (for compressor input)
    }
    states = {
        'el_status': 0,  # one of: 'off', 'warm_up', 'ramp_up', 'on', 'ramp_down', 'hold'
        'phase_step': 0,  # 0=off/warmup, 1=ramp_up, 2=on, 3=ramp_down, 4=hold
        'max_p_in_el': 0 #defined it as a state in order to use it as input for controller, easy use for DelftBlue
    }

    time_step_size = 1  
    time = None
    mmh2 = 2.016  # g/mol

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.e_eff = self._model.parameters.get('e_eff')
        self.max_p_in = self._model.parameters.get('max_p_in')
        self.warm_up_time = self._model.parameters.get('warm_up_time')
        # self.warm_up_power = self._model.parameters.get('warm_up_power')
        self.ramp_up_time = self._model.parameters.get('ramp_up_time')
        self.ramp_down_time = self._model.parameters.get('ramp_down_time')
        self.hold_time = self._model.parameters.get('hold_time')
        # self.h2_rate_hr = self._model.parameters.get('hydrogen_production_rate')  # kg/h
        self.el_status = self._model.states.get('el_status')
        self.phase_step = self._model.states.get('phase_step')
        self.max_p_in_el = self._model.states.get('max_p_in_el')

        self.phase_start_time = None
        self.prev_flow2e = 0  # Initialize
        self.prev_flow2c = 0  # Initialize

        self.warm_up_power = 0.260/2.45 * self.max_p_in

    def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> None:
        if inputs is None:
            raise ValueError("Inputs cannot be None. Please provide valid input data.")
        
        input_data = self.unpack_inputs(inputs)
        signal = input_data['run_electrolyser']
        production_rate = input_data['production_rate']
        dt_h = self.time_resolution / 3600  # convert resolution to hours
        lhv = 33.33  # kWh/kg (lower heating value of hydrogen)
        self.time = time
        self.max_p_in_el = self.max_p_in
        
        # === Phase Logic ===
        
        # Check if the signal to run the electrolyzer is active
        if signal == 1:
            # Warm-up phase: 15 minutes at 0.260 kW
            if self.phase_step == 0:
                if self.phase_start_time is None:
                    self.phase_start_time = time
                    self.el_status = 'warm_up'
                
                flow2e = -self.warm_up_power
                flow2c = 0
                
                elapsed = (time - self.phase_start_time) * self.time_resolution
                if elapsed >= self.warm_up_time:
                    self.phase_step = 1  # start ramp up
                    self.phase_start_time = time  # reset for ramp up phase
            
            # Ramp-up phase: 15 minutes linear ramp from 0.260 kW to 0.6 * max_p_in
            elif self.phase_step == 1:
                elapsed = (time - self.phase_start_time) * self.time_resolution
                ramp_fraction = min(elapsed / self.ramp_up_time, 1.0)
                self.el_status = 'ramp_up'
                
                # Linear interpolation from warm_up_power to 0.6 * max_p_in
                start_power = self.warm_up_power
                end_power = 0.6 * self.max_p_in
                flow2e = -(start_power + (end_power - start_power) * ramp_fraction)
                flow2c = -flow2e / lhv * self.e_eff/100 * dt_h
                
                if ramp_fraction >= 1.0:
                    self.phase_step = 2  # on
                    self.el_status = 'on'
            
            # On phase: Production rate controlled, from 0.6 to 1.0 of max_p_in
            elif self.phase_step == 2:
                self.el_status = 'on'
                # Production rate should be between 0.6 and 1.0
                actual_rate = max(0.6, min(production_rate, 1.0))
                flow2e = -actual_rate * self.max_p_in
                flow2c = -flow2e / lhv * self.e_eff/100 * dt_h
                self.prev_flow2e = flow2e  # Store for ramp-down
                self.prev_flow2c = flow2c
        
        # Check if the signal to stop the electrolyzer is active
        elif signal == 0:
            # Start ramp-down from ON phase
            if self.phase_step == 2:
                self.phase_step = 3
                self.phase_start_time = time
                self.el_status = 'ramp_down'
            
            # Ramp-down phase: Linear ramp from current power to 0.6 * max_p_in over 15 minutes
            if self.phase_step == 3:
                elapsed = (time - self.phase_start_time) * self.time_resolution
                
                if elapsed < self.ramp_down_time:
                    # Linear ramp from previous power to 0.6 * max_p_in
                    ramp_fraction = elapsed / self.ramp_down_time
                    start_power = -self.prev_flow2e  # Make positive for calculation
                    end_power = 0.6 * self.max_p_in
                    
                    # Linear interpolation
                    current_power = start_power + (end_power - start_power) * ramp_fraction
                    flow2e = -current_power
                    flow2c = -flow2e / lhv * self.e_eff/100 * dt_h
                else:
                    # Reached 0.6 * max_p_in, move to hold phase
                    self.phase_step = 4
                    self.phase_start_time = time
                    self.el_status = 'hold'
                    flow2e = -0.6 * self.max_p_in
                    flow2c = -flow2e / lhv * self.e_eff/100 * dt_h
            
            # Hold phase: Stay at 0.6 * max_p_in for 30 minutes
            elif self.phase_step == 4:
                elapsed = (time - self.phase_start_time) * self.time_resolution
                
                if elapsed < self.hold_time:
                    flow2e = -0.6 * self.max_p_in
                    flow2c = -flow2e / lhv * self.e_eff/100 * dt_h
                else:
                    # Fully shut down after hold time
                    self.phase_step = 0
                    self.phase_start_time = None
                    self.el_status = 'off'
                    flow2e = 0
                    flow2c = 0
            
            # Fully off
            elif self.phase_step == 0:
                flow2e = 0
                flow2c = 0
                self.el_status = 'off'

            elif self.phase_step ==1:
                flow2e = 0
                flow2c = 0
                self.el_status = 'off'
                self.phase_step = 0

        self.set_outputs({
            'flow2e': round(flow2e, 4),
            'flow2e_grid': round(flow2e, 4),
            'flow2c': round(flow2c, 6)
        })

        self.set_states({
            'el_status': self.el_status,
            'phase_step': self.phase_step,
            'max_p_in_el': self.max_p_in_el
        })

        return time + self._model.time_step_size
#Before DelftBlue
# from illuminator.builder import IlluminatorModel, ModelConstructor

# class Electrolyzer(ModelConstructor):
    
#     parameters = {
#         'e_eff': 63.59,  # % this is including the BoP losses and conversion losses
#         'max_p_in': 2.45,  # kW this is total power
#         'warm_up_time': 900,  # seconds (15 minutes) - CHANGED FROM 720
#         'warm_up_power': 0.260,  # kW (power during warm-up phase)
#         'ramp_up_time': 900,  # seconds (15 minutes) - CHANGED FROM 600
#         'ramp_down_time': 900,  # seconds (15 minutes) - CHANGED FROM 1800
#         'hold_time': 1800,  # seconds (30 minutes) - CHANGED FROM 1500
#         'hydrogen_production_rate': 0.04494  # kg/h or 500 NL/h
#     }
#     inputs = {
#         'run_electrolyser': 0,  # signal: 0 or 1
#         'production_rate': 0  # rate that electrolyzer is working
#     }
#     outputs = {
#         'flow2e': 0,  # kW (power consumption)
#         'flow2e_grid': 0,  # kW (power consumption from grid)
#         'flow2c': 0  # kg/timestep (for compressor input)
#     }
#     states = {
#         'el_status': 0,  # one of: 'off', 'warm_up', 'ramp_up', 'on', 'ramp_down', 'hold'
#         'phase_step': 0  # 0=off/warmup, 1=ramp_up, 2=on, 3=ramp_down, 4=hold
#     }

#     time_step_size = 1  
#     time = None
#     mmh2 = 2.016  # g/mol

#     def __init__(self, **kwargs) -> None:
#         super().__init__(**kwargs)
#         self.e_eff = self._model.parameters.get('e_eff')
#         self.max_p_in = self._model.parameters.get('max_p_in')
#         self.warm_up_time = self._model.parameters.get('warm_up_time')
#         self.warm_up_power = self._model.parameters.get('warm_up_power')
#         self.ramp_up_time = self._model.parameters.get('ramp_up_time')
#         self.ramp_down_time = self._model.parameters.get('ramp_down_time')
#         self.hold_time = self._model.parameters.get('hold_time')
#         self.h2_rate_hr = self._model.parameters.get('hydrogen_production_rate')  # kg/h
#         self.el_status = self._model.states.get('el_status')
#         self.phase_step = self._model.states.get('phase_step')
#         self.phase_start_time = None
#         self.prev_flow2e = 0  # Initialize
#         self.prev_flow2c = 0  # Initialize

#     def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> None:
#         if inputs is None:
#             raise ValueError("Inputs cannot be None. Please provide valid input data.")
        
#         input_data = self.unpack_inputs(inputs)
#         signal = input_data['run_electrolyser']
#         production_rate = input_data['production_rate']
#         dt_h = self.time_resolution / 3600  # convert resolution to hours
#         lhv = 33.33  # kWh/kg (lower heating value of hydrogen)
#         self.time = time
        
#         # === Phase Logic ===
        
#         # Check if the signal to run the electrolyzer is active
#         if signal == 1:
#             # Warm-up phase: 15 minutes at 0.260 kW
#             if self.phase_step == 0:
#                 if self.phase_start_time is None:
#                     self.phase_start_time = time
#                     self.el_status = 'warm_up'
                
#                 flow2e = -self.warm_up_power
#                 flow2c = 0
                
#                 elapsed = (time - self.phase_start_time) * self.time_resolution
#                 if elapsed >= self.warm_up_time:
#                     self.phase_step = 1  # start ramp up
#                     self.phase_start_time = time  # reset for ramp up phase
            
#             # Ramp-up phase: 15 minutes linear ramp from 0.260 kW to 0.6 * max_p_in
#             elif self.phase_step == 1:
#                 elapsed = (time - self.phase_start_time) * self.time_resolution
#                 ramp_fraction = min(elapsed / self.ramp_up_time, 1.0)
#                 self.el_status = 'ramp_up'
                
#                 # Linear interpolation from warm_up_power to 0.6 * max_p_in
#                 start_power = self.warm_up_power
#                 end_power = 0.6 * self.max_p_in
#                 flow2e = -(start_power + (end_power - start_power) * ramp_fraction)
#                 flow2c = -flow2e / lhv * self.e_eff/100 * dt_h
                
#                 if ramp_fraction >= 1.0:
#                     self.phase_step = 2  # on
#                     self.el_status = 'on'
            
#             # On phase: Production rate controlled, from 0.6 to 1.0 of max_p_in
#             elif self.phase_step == 2:
#                 self.el_status = 'on'
#                 # Production rate should be between 0.6 and 1.0
#                 actual_rate = max(0.6, min(production_rate, 1.0))
#                 flow2e = -actual_rate * self.max_p_in
#                 flow2c = -flow2e / lhv * self.e_eff/100 * dt_h
#                 self.prev_flow2e = flow2e  # Store for ramp-down
#                 self.prev_flow2c = flow2c
        
#         # Check if the signal to stop the electrolyzer is active
#         elif signal == 0:
#             # Start ramp-down from ON phase
#             if self.phase_step == 2:
#                 self.phase_step = 3
#                 self.phase_start_time = time
#                 self.el_status = 'ramp_down'
            
#             # Ramp-down phase: Linear ramp from current power to 0.6 * max_p_in over 15 minutes
#             if self.phase_step == 3:
#                 elapsed = (time - self.phase_start_time) * self.time_resolution
                
#                 if elapsed < self.ramp_down_time:
#                     # Linear ramp from previous power to 0.6 * max_p_in
#                     ramp_fraction = elapsed / self.ramp_down_time
#                     start_power = -self.prev_flow2e  # Make positive for calculation
#                     end_power = 0.6 * self.max_p_in
                    
#                     # Linear interpolation
#                     current_power = start_power + (end_power - start_power) * ramp_fraction
#                     flow2e = -current_power
#                     flow2c = -flow2e / lhv * self.e_eff/100 * dt_h
#                 else:
#                     # Reached 0.6 * max_p_in, move to hold phase
#                     self.phase_step = 4
#                     self.phase_start_time = time
#                     self.el_status = 'hold'
#                     flow2e = -0.6 * self.max_p_in
#                     flow2c = -flow2e / lhv * self.e_eff/100 * dt_h
            
#             # Hold phase: Stay at 0.6 * max_p_in for 30 minutes
#             elif self.phase_step == 4:
#                 elapsed = (time - self.phase_start_time) * self.time_resolution
                
#                 if elapsed < self.hold_time:
#                     flow2e = -0.6 * self.max_p_in
#                     flow2c = -flow2e / lhv * self.e_eff/100 * dt_h
#                 else:
#                     # Fully shut down after hold time
#                     self.phase_step = 0
#                     self.phase_start_time = None
#                     self.el_status = 'off'
#                     flow2e = 0
#                     flow2c = 0
            
#             # Fully off
#             elif self.phase_step == 0:
#                 flow2e = 0
#                 flow2c = 0
#                 self.el_status = 'off'

#         self.set_outputs({
#             'flow2e': round(flow2e, 4),
#             'flow2e_grid': round(flow2e, 4),
#             'flow2c': round(flow2c, 6)
#         })

#         self.set_states({
#             'el_status': self.el_status,
#             'phase_step': self.phase_step
#         })

#         return time + self._model.time_step_size