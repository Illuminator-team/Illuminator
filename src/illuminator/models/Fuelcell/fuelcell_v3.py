
from illuminator.builder import ModelConstructor

class Fuelcell(ModelConstructor):

    parameters = {
        'h2_to_DC_eff': 58.0,  # %
        'h2_to_AC_eff': 68.6,  # % also with AC BoP Losses (PLC, cooling pump, H2 pump) 
        'p_out_stack': 2.37,      # kW
        'specific_h2_consumption': 11.35 #NL/min per kW
    }
    inputs = {
        'run_fuelcell': 0,   # signal
    }
    outputs = {
        'p_out_fuelcell': 0,
        'p_out_fuelcell_grid': 0 # kW, power output to the grid
    }
    states = {
        'h2_flow': 0, #kg/h
        'fc_status': 'off',  # 'off', 'ramp_up1', 'ramp_up2', 'on', 'ramp_down
        'output_power_fc': 0  # kW
    }

    time_step_size = 1  
    time = None

    hydrogen_energy_content = 33.33 # kWh/kg at 1 atm
    hydrogen_density = 0.08988/1000 # kg/L at 1 atm

    def __init__(self, **kwargs) -> None:

        super().__init__(**kwargs)
        self.h2_to_DC_eff = self._model.parameters.get('h2_to_DC_eff')  
        self.h2_to_AC_eff = self._model.parameters.get('h2_to_AC_eff')
        self.p_out_stack = self._model.parameters.get('p_out_stack')
        self.specific_h2_consumption = self._model.parameters.get('specific_h2_consumption')

        self.h2_flow = self._model.states.get('h2_flow')
        self.fc_status = self._model.states.get('fc_status')
        self.output_power_fc = self._model.states.get('output_power_fc')

        self.phase_start_time = None


    def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> None:
        input_data = self.unpack_inputs(inputs)
        run_fc = input_data['run_fuelcell']
        self.time = time
        h2_in_rating = self.p_out_stack*self.specific_h2_consumption 
        self.output_power_fc = h2_in_rating*60*self.hydrogen_density *self.hydrogen_energy_content*(self.h2_to_DC_eff/100)*(self.h2_to_AC_eff/100)
        p_out = 0
        if run_fc ==1:
            h2_in = self.p_out_stack*self.specific_h2_consumption # NL/min
            p_out = h2_in*60*self.hydrogen_density *self.hydrogen_energy_content*(self.h2_to_DC_eff/100)*(self.h2_to_AC_eff/100) #kW
            self.h2_flow = h2_in * 60* self.hydrogen_density  # kg/h
            self.fc_status = 'on'
      

        elif run_fc ==0:
            p_out = 0
            self.h2_flow = 0 
            self.fc_status = 'off'


        self.set_outputs({
            'p_out_fuelcell': round(p_out, 3),
            'p_out_fuelcell_grid': round(p_out, 3)  # Assuming all power goes to the grid
        })

    
        self.set_states({
            'h2_flow': self.h2_flow,
            'fc_status': self.fc_status,
            'output_power_fc': self.output_power_fc
        })

        return time + self._model.time_step_size
    
#Before DelftBlue

# from illuminator.builder import ModelConstructor

# class Fuelcell(ModelConstructor):

#     parameters = {
#         'fuelcell_eff': 39.78,  # %
#         # 'ramp_up_time1': 40, # s from 0 W to 500 W
#         # 'ramp_up_power1': 0.5, # kW at the end of ramp_up_time1
#         # 'ramp_up_time2': 60, # s from 500 W to 1000 W
#         # 'ramp_down_time': 60, # s from 1.623 kW to 0 W
#         'max_p_out': 1.83,      # kW
#         'h2_in': 0.002040276 #kg/min and 22.7 NL/min at standard conditions
#     }
#     inputs = {
#         'run_fuelcell': 0,   # signal
#         # 'h2_flow2f': 0       # kg/timestep
#     }
#     outputs = {
#         'p_out_fuelcell': 0,
#         # 'p_out_fuelcell_controller': 0,  # kW
#         'p_out_fuelcell_grid': 0 # kW, power output to the grid
#     }
#     states = {
#         'h2_flow': 0, #kg/h
#         'fc_status': 'off',  # 'off', 'ramp_up1', 'ramp_up2', 'on', 'ramp_down
#         # 'timer': 0  # Timer for fuelcell warmup
#         'phase_step': 0  # 0: off, 1: ramp_up1, 2: ramp_up2, 3: on, 4: ramp_down
#     }

#     time_step_size = 1  
#     time = None

#     hydrogen_energy_content = 33.33 # kWh/kg at 1 atm
#     hhv = 141.9  # kJ/mol
#     mmh2 = 2.016  # g/mol

#     def __init__(self, **kwargs) -> None:

#         super().__init__(**kwargs)
#         self.fuelcell_eff = self._model.parameters.get('fuelcell_eff')  
#         self.ramp_up_time1 = self._model.parameters.get('ramp_up_time1')
#         self.ramp_up_power1 = self._model.parameters.get('ramp_up_power1')
#         self.ramp_up_time2 = self._model.parameters.get('ramp_up_time2')
#         self.ramp_down_time = self._model.parameters.get('ramp_down_time')
#         self.max_p_out = self._model.parameters.get('max_p_out')
#         self.h2_in = self._model.parameters.get('h2_in')
#         self.h2_flow = self._model.states.get('h2_flow')
#         # self.fc_status = self._model.states.get('fc_status')
#         # self.timer = self._model.states.get('timer')
#         self.phase_step = self._model.states.get('phase_step')

#         self.phase_start_time = None


#     def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> None:
#         input_data = self.unpack_inputs(inputs)
#         run_fc = input_data['run_fuelcell']
#         dt_h = self.time_resolution / 3600
#         self.time = time
#         # flow2f = 0
#         p_out = 0
#         # self.h2_flow = 0
#         # hourflow2f = 0

#         if run_fc ==1:
#             p_out = self.h2_in*60 * self.hydrogen_energy_content * (self.fuelcell_eff/100) #kW
#             self.h2_flow = self.h2_in * 60

#         if run_fc ==0:
#             p_out = 0
#             self.h2_flow = 0 


#         # if run_fc == 1:
#         #     if self.phase_step == 3:
#         #         self.phase_step = 0 #als in de ramping down fase de fuel cell weer word aangezet is de phase_step nog 3 en blijft p_out op 0
#         #     if self.phase_step == 0: #start ramping up
#         #         if self.phase_start_time is None:
#         #             self.phase_start_time = time  # Set once
#         #         elapsed = (time - self.phase_start_time) * self.time_resolution
#         #         ramp_fraction = min(elapsed / self.ramp_up_time1, 1.0)
#         #         p_out = ramp_fraction * self.ramp_up_power1
#         #         self.h2_flow = p_out * self.h2_flow_max / self.max_p_out
#         #         if elapsed >= self.ramp_up_time1:
#         #             self.phase_step = 1
#         #             self.phase_start_time = time  # Reset for next ramp phase

#         #     elif self.phase_step == 1:
#         #         elapsed = (time - self.phase_start_time) * self.time_resolution
#         #         ramp_fraction = min(elapsed / self.ramp_up_time2, 1.0)
#         #         p_out = self.ramp_up_power1 + ramp_fraction * (self.max_p_out - self.ramp_up_power1)
#         #         self.h2_flow = p_out * self.h2_flow_max / self.max_p_out

#         #         if elapsed >= self.ramp_up_time2:
#         #             self.phase_step = 2
#         #             self.phase_start_time = time

#         #     elif self.phase_step == 2:
#         #         p_out = self.max_p_out
#         #         self.h2_flow = self.h2_flow_max

#         # elif run_fc == 0:
#         #     if self.phase_step == 2:
#         #         self.phase_step = 3
#         #         self.phase_start_time = time

#         #     if self.phase_step == 3:
#         #         elapsed = (time - self.phase_start_time) * self.time_resolution
#         #         ramp_fraction = max(1 - (elapsed / self.ramp_down_time), 0)
#         #         p_out = ramp_fraction * self.max_p_out
#         #         self.h2_flow = p_out * self.h2_flow_max / self.max_p_out

#         #         if elapsed >= self.ramp_down_time:
#         #             self.phase_step = 0
#         #             self.phase_start_time = None
#         #             # p_out = 0
#         #             # self.h2_flow = 0

#             # elif self.phase_step == 0:
#             #     p_out = 0
#             #     self.h2_flow = 0

#         self.set_outputs({
#             'p_out_fuelcell': round(p_out, 3),
#             # 'p_out_fuelcell_controller': round(p_out, 3),  # Assuming controller output is same as fuelcell output
#             'p_out_fuelcell_grid': round(p_out, 3)  # Assuming all power goes to the grid
#         })

    
#         self.set_states({
#             'h2_flow': self.h2_flow,
#             # 'fc_status': self.fc_status,
#             'phase_step': self.phase_step
#             # 'timer': self.timer
#         })

#         return time + self._model.time_step_size
    
     
#         # # === Phase Logic ===
#         # if self.fc_status == 'off':
#         #     if run_fc == 1:
#         #         self.fc_status = 'ramp_up1'
#         #         self.timer = time

#         # elif self.fc_status == 'ramp_up1':
#         #     elapsed = time - self.timer
#         #     ramp_fraction = min(elapsed / self.ramp_up_time1, 1.0)
#         #     p_out = ramp_fraction * self.ramp_up_power1
#         #     hourflow2f = ramp_fraction * self.h2_flow_max * (self.ramp_up_power1 / self.max_p_out)
#         #     # flow2f = h2_flow2f

#         #     if elapsed >= self.ramp_up_time1:
#         #         self.fc_status = 'ramp_up2'
#         #         self.timer = time

#         # elif self.fc_status == 'ramp_up2':
#         #     elapsed = time - self.timer
#         #     ramp_fraction = min(elapsed / self.ramp_up_time2, 1.0)
#         #     p_out = self.ramp_up_power1 + ramp_fraction * (self.max_p_out - self.ramp_up_power1 )
#         #     hourflow2f = (self.ramp_up_power1 + ramp_fraction * (self.max_p_out - self.ramp_up_power1 )) * self.h2_flow_max / self.max_p_out
#         #     # flow2f = h2_flow2f
#         #     if elapsed >= self.ramp_up_time2:
#         #         self.fc_status = 'on'
#         #         self.timer = time

#         # elif self.fc_status == 'on':
#         #     p_out = self.max_p_out
#         #     hourflow2f = self.h2_flow_max
#         #     # flow2f = h2_flow2f
#         #     if run_fc == 0:
#         #         self.fc_status = 'ramp_down'
#         #         self.timer = time

#         # elif self.fc_status == 'ramp_down':
#         #     elapsed = time - self.timer
#         #     ramp_fraction = max(1 - (elapsed / self.ramp_down_time), 0)
#         #     p_out = ramp_fraction * self.max_p_out
#         #     hourflow2f = ramp_fraction * self.h2_flow_max
#         #     # flow2f = h2_flow2f * ramp_fraction
#         #     if elapsed >= self.ramp_down_time:
#         #         self.fc_status = 'off'
#         #         self.timer = time
