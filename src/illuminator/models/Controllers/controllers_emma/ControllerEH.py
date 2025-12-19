#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# VERSION WITH BATTERY CONTROL IN CONTROLLER

# from illuminator.builder import ModelConstructor
# import numpy as np
# import datetime

# class EMSController(ModelConstructor):
#     parameters = {
#         'soc_min': 20,
#         'soc_max': 80,
#         'h2_soc_min': 0,
#         'h2_soc_max': 100,
#         'fc_eff': 0.99,
#         'el_eff': 0.70,
#         'warmup_fc': 300,
#         'warmup_el': 180,
#         'ramp_rate_fc': 500,
#         'ramp_rate_el': 500,
#         'p_out_fc': 1.83 #kW estimated power output from fuel cell for battery control
#     }
#     inputs = {
#         'pv_signal': 0,
#         'load_signal': 0,
#         'soc': 50,
#         'h2_soc': 50,
#         # 'p_out_fuelcell_controller': 0  # Power output from fuel cell 
#     }
#     outputs = {
#         'charge_battery': 0,  # 1 = charge, -1 = discharge, 0 = idle
#         'run_electrolyser': 0,
#         'run_fuelcell': 0,
#         'compressor_on': 0,
#         'storage_flow': 0     # 1 = store H2, -1 = withdraw H2, 0 = idle
#     }
#     states = {
#         'el_state': 0,  # 0 = off, 1 = on
#         'fc_state': 0, # 0 = off, 1 = on
#         'bat_state': 'off',
#         'el_daily_flag': False,
#         'production_rate': 0  # Production rate of electrolyser
#     }

#     time_step_size = 1  
#     time = None

#     def __init__(self, **kwargs) -> None:
#         super().__init__(**kwargs)
#         self.start_time = self._model.parameters.get('start_time')
#         self.soc_min = self._model.parameters.get('soc_min')
#         self.soc_max = self._model.parameters.get('soc_max')
#         self.h2_soc_min = self._model.parameters.get('h2_soc_min')
#         self.h2_soc_max = self._model.parameters.get('h2_soc_max')
#         self.fc_eff = self._model.parameters.get('fc_eff')
#         self.el_eff = self._model.parameters.get('el_eff')
#         self.warmup_fc = self._model.parameters.get('warmup_fc')
#         self.warmup_el = self._model.parameters.get('warmup_el')
#         self.ramp_rate_fc = self._model.parameters.get('ramp_rate_fc')
#         self.ramp_rate_el = self._model.parameters.get('ramp_rate_el')
#         self.p_out_fc = self._model.parameters.get('p_out_fc')
#         self.el_state = self._model.states.get('el_state')
#         self.fc_state = self._model.states.get('fc_state')
#         self.bat_state = self._model.states.get('bat_state', 'off')
#         self.el_daily_flag = self._model.states.get('el_daily_flag')
#         self.production_rate = self._model.states.get('production_rate')


#     def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> None:
#         input_data = self.unpack_inputs(inputs)
#         pv = input_data['pv_signal']
#         load = input_data['load_signal']
#         soc = input_data['soc']
#         h2_soc = input_data['h2_soc']
#         # fc = input_data['p_out_fuelcell_controller']

#         start_time = datetime.datetime.strptime(inputs.get('start_time', self._model.parameters['start_time']), "%Y-%m-%d %H:%M:%S")
#         now = start_time + datetime.timedelta(seconds=time * self.time_resolution)
#         hour = now.hour
#         today_date = now.date()

#         # Define summer period (16th March to 14th October)
#         is_winter = not (datetime.date(today_date.year, 3, 16) <= today_date <= datetime.date(today_date.year, 10, 14))

#         print(f"[{now}] Winter? {is_winter}, Hour: {hour}, Date: {today_date}")

#         # Reset daily flag on day change
#         today_dayofyear = now.timetuple().tm_yday
#         if not hasattr(self, 'last_day') or self.last_day != today_dayofyear:
#             self.last_day = today_dayofyear
#             self.el_daily_flag = False

#         run_el = 0
#         run_fc = 0
#         charge_bat = 0
#         storage_flow = 0
#         compressor_on = 0
#         self.production_rate = 0

        
#         if not is_winter:
#             if self.el_state == 0:
#             #     # Try to turn ON the electrolyser
#                 if soc >= 80 and pv > 1 and hour < 12 and not self.el_daily_flag and h2_soc < self.h2_soc_max:
#                     self.el_state = 1
#                     self.el_daily_flag = True
                    

#             elif self.el_state == 1:
#                 if soc < 65 and h2_soc <= self.h2_soc_max and pv<0.5:
#                     self.el_state = 0
#                 else:
#                     self.el_state = 1
        
#             if self.el_state == 1:
#                 run_el = 1
#                 run_fc = 0 
#                 compressor_on = 1
#                 storage_flow = 1
#             elif self.el_state == 0:	
#                 run_el = 0
#                 run_fc = 0
#                 compressor_on = 0

            
#             if soc < 80:
#                 self.production_rate = 0.6
#             elif soc >=80 and soc <= 90:
#                 self.production_rate = 0.6 + (soc - 80)/100 * 4
#             elif soc >= 90:
#                 self.production_rate = 1.0

#         elif soc <= 25:
#             self.fc_state = 1
#             run_fc = 0 
#             storage_flow = -1
#             run_el = 0
#             compressor_on = 0

#         elif is_winter:
#             run_el = 0 
#             # if self.fc_state == 0:
#             if hour < 13 and soc < 40:
#                 self.fc_state = 1
#             elif hour == 13 and soc < 50:
#                 self.fc_state = 1
#             elif hour == 14 and soc < 60:
#                 self.fc_state = 1   
#             elif hour == 15 and soc < 70:
#                 self.fc_state = 1
#             elif hour == 16 and soc < 80:
#                 self.fc_state = 1
#             elif soc > 90:
#                 self.fc_state = 0
#             else:
#                 self.fc_state = 0

#             if self.fc_state == 1 and h2_soc >= self.h2_soc_min and h2_soc <= self.h2_soc_max:
#                 run_el = 0
#                 run_fc = 1
#                 compressor_on = 0
#                 storage_flow = -1
#             elif self.fc_state == 0:
#                 run_fc = 0
        
#         # Battery control
#         # if pv == load or soc >= self.parameters['soc_max']:
#         #     charge_bat = 0  # off
#         #     self.states['bat_state'] = 'off'
#         if pv == load:
#             charge_bat = 0  # off
#             self.states['bat_state'] = 'off'
#         elif pv > load and soc <= self.parameters['soc_max'] and run_el == 0 and run_fc == 0: #run_el ==0 should be removed in real implementation? Solar is not high enough in this code
#             charge_bat = 1  # charging
#             self.states['bat_state'] = 'charging'
#         elif pv + self.p_out_fc > load and soc <= self.parameters['soc_max'] and run_fc == 1:
#             charge_bat = 2  # charging with excess power from fuel cell
#         elif pv < load and soc >= self.parameters['soc_min'] and run_el ==0 and run_fc == 0:
#             charge_bat = -1 #discharging
#             self.states['bat_state'] = 'discharging'
#         elif pv + self.p_out_fc < load and soc >= self.parameters['soc_min'] and run_fc == 1:
#             charge_bat = -3
#             self.states['bat_state'] = 'discharging'
#         elif run_el == 1:
#             charge_bat = -2 
#             self.states['bat_state'] = 'discharging'


#         self.set_outputs({
#             'charge_battery': charge_bat,
#             'run_electrolyser': run_el,
#             'run_fuelcell': run_fc,
#             'compressor_on': compressor_on,
#             'storage_flow': storage_flow
#         })

#         self.set_states({
#             'el_state': self.el_state,
#             'fc_state': self.fc_state,
#             'bat_state': self.states['bat_state'],
#             'el_daily_flag': self.states['el_daily_flag'],
#             'production_rate': self.production_rate
#         })

#         return time + self.time_step_size
    
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# VERSION WITHOUT BATTERY CONTROL IN CONTROLLER

from illuminator.builder import ModelConstructor
import numpy as np
import datetime

class EMSController(ModelConstructor):
    parameters = {
        'start_time': '2024-04-01 00:00:00',  # Start time of the simulation
        'soc_min': 20,
        'soc_max': 80,
        'h2_soc_min': 6,
        'h2_soc_max': 100,
        'el_start_soc': 80,     # Battery SOC to start electrolyzer (%)
        'el_start_hour': 12,   # Hour of day to start electrolyzer
        'el_stop_soc': 65,      # Battery SOC to stop electrolyzer (%)
        'fc_emergency_soc': 25, # Battery SOC for emergency fuel cell start (%)
        'fc_stop_soc': 90,      # Battery SOC to stop fuel cell (%)
        'pv_threshold_start': 1.0, # kW - minimum PV to consider starting electrolyzer
        'pv_threshold_stop_fraction': 0.05, # fraction of threshold - PV level to stop electrolyzer
        # 'fc_threshold_start': 60.8, 
        # 'electrolyzer_power': 152,
        # 'fc_power': 100,
        'transformer_capacity': 250  # kW
    }
    inputs = {
        'pv_signal': 0,
        'load_signal': 0,
        'soc': 50,
        'h2_soc': 50,
        'grid_flow': 0,
        'output_power_fc': 0,  # Power output from fuel cell 
        'max_p_in_el': 0
        # 'p_out_fuelcell_controller': 0  # Power output from fuel cell 
    }
    outputs = {
        'run_electrolyser': 0,
        'run_fuelcell': 0,
        'compressor_on': 0,
        'storage_flow': 0     # 1 = store H2, -1 = withdraw H2, 0 = idle
    }
    states = {
        'el_state': 0,  # 0 = off, 1 = on
        'fc_state': 0, # 0 = off, 1 = on
        # 'bat_state': 'off',
        'el_daily_flag': False,
        'production_rate': 0  # Production rate of electrolyser
    }

    time_step_size = 1  
    time = None

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.start_time = self._model.parameters.get('start_time')
        self.soc_min = self._model.parameters.get('soc_min')
        self.soc_max = self._model.parameters.get('soc_max')
        self.h2_soc_min = self._model.parameters.get('h2_soc_min')
        self.h2_soc_max = self._model.parameters.get('h2_soc_max')
        self.el_start_soc = self._model.parameters.get('el_start_soc')
        self.el_start_hour = self._model.parameters.get('el_start_hour')
        self.el_stop_soc = self._model.parameters.get('el_stop_soc')
        self.fc_emergency_soc = self._model.parameters.get('fc_emergency_soc')
        self.fc_stop_soc = self._model.parameters.get('fc_stop_soc')
        self.pv_threshold_start = self._model.parameters.get('pv_threshold_start')
        self.pv_threshold_stop_fraction = self._model.parameters.get('pv_threshold_stop_fraction')
        # self.fc_threshold_start = self._model.parameters.get('fc_threshold_start')
        # self.electrolzer_power = self._model.parameters.get('electrolyzer_power')
        # self.fc_power = self._model.parameters.get('fc_power')
        self.transformer_capacity = self._model.parameters.get('transformer_capacity')

        # self.fc_eff = self._model.parameters.get('fc_eff')
        # self.el_eff = self._model.parameters.get('el_eff')
        # self.warmup_fc = self._model.parameters.get('warmup_fc')
        # self.warmup_el = self._model.parameters.get('warmup_el')
        # self.ramp_rate_fc = self._model.parameters.get('ramp_rate_fc')
        # self.ramp_rate_el = self._model.parameters.get('ramp_rate_el')
        # self.p_out_fc = self._model.parameters.get('p_out_fc')
        self.el_state = self._model.states.get('el_state')
        self.fc_state = self._model.states.get('fc_state')
        self.el_daily_flag = self._model.states.get('el_daily_flag')
        self.production_rate = self._model.states.get('production_rate')


    def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> None:
        input_data = self.unpack_inputs(inputs)
        pv = input_data['pv_signal']
        load = input_data['load_signal']
        soc = input_data['soc']
        h2_soc = input_data['h2_soc']
        grid_flow = input_data['grid_flow']
        output_power_fc = input_data['output_power_fc']
        max_p_in_el = input_data['max_p_in_el']
        # if grid_flow is None:
        #     grid_flow = 0

        start_time = datetime.datetime.strptime(inputs.get('start_time', self._model.parameters['start_time']), "%Y-%m-%d %H:%M:%S")
        now = start_time + datetime.timedelta(seconds=time * self.time_resolution)
        hour = now.hour
        today_date = now.date()

        # Define summer period (16th March to 14th October)
        is_winter = not (datetime.date(today_date.year, 3, 16) <= today_date <= datetime.date(today_date.year, 10, 14))
        # is_winter = datetime.date(today_date.year, 1, 2) <= today_date <= datetime.date(today_date.year, 3, 16) #forvalidationSOC

        print(f"[{now}] Winter? {is_winter}, Hour: {hour}, Date: {today_date}")

        # Reset daily flag on day change
        today_dayofyear = now.timetuple().tm_yday
        if not hasattr(self, 'last_day') or self.last_day != today_dayofyear:
            self.last_day = today_dayofyear
            self.el_daily_flag = False

        run_el = 0
        run_fc = 0
        storage_flow = 0
        compressor_on = 0
        self.production_rate = 0

        
        if not is_winter:
    # Calculate production rate FIRST
            # if soc < 80:
            #     self.production_rate = 0.6
            # elif soc >= 80 and soc <= 90:
            #     self.production_rate = 0.6 + (soc - 80)/100 * 4
            # elif soc >= 90:
            #     self.production_rate = 1.0
            self.production_rate = 1.0
            # Calculate grid utilization
            grid_utilization = grid_flow / self.transformer_capacity
            
            # ====================================================================
            # ELECTROLYZER START
            # ====================================================================
            if self.el_state == 0:
                # if ((soc >= 70 or (grid_flow < 50 and grid_utilization > 0)) and
                #     hour < 13 and
                #     not self.el_daily_flag and
                #     h2_soc < self.h2_soc_max):
                if ((pv - load > 0) and
                    not self.el_daily_flag and
                    h2_soc < self.h2_soc_max):
                    self.el_state = 1
                    self.el_daily_flag = True
                else:
                    self.el_state = 0

            # ====================================================================
            # ELECTROLYZER STOP
            # ====================================================================
            elif self.el_state == 1:
                if (load + max_p_in_el - pv > self.transformer_capacity):
                # if ((load-pv > 0) and load + 200 - pv > self.transformer_capacity and soc<30) or (soc < 85) or (soc >= 85 and (load + 200 - pv > self.transformer_capacity)) or h2_soc >= self.h2_soc_max:
                    self.el_state = 0
                # if grid_flow > 0.8*self.transformer_capacity or h2_soc >= self.h2_soc_max:
                #     self.el_state = 0
                else:
                    self.el_state = 1

            # ====================================================================
            # SET EL OUTPUTS
            # ====================================================================
            if self.el_state == 1:
                run_el = 1
                compressor_on = 1
                storage_flow = 1
            else:
                run_el = 0
                compressor_on = 0
            
            if self.fc_state == 0 and soc <= self.fc_emergency_soc and (load - pv) >= self.transformer_capacity and h2_soc >= self.h2_soc_min:
                self.fc_state = 1
            
            # elif self.fc_state == 1 and ((grid_flow + output_power_fc) < self.transformer_capacity or h2_soc <= self.h2_soc_min):
            #     self.fc_state = 0
            elif self.fc_state == 1 and ((load-pv) < self.transformer_capacity or h2_soc <= self.h2_soc_min):
                self.fc_state = 0

            if self.fc_state == 1 and h2_soc >= self.h2_soc_min and h2_soc <= self.h2_soc_max:
                run_fc = 1
                storage_flow = -1
            else:
                run_fc = 0
            # if soc < 80:
            #     self.production_rate = 0.6
            # elif soc >=80 and soc <= 90:
            #     self.production_rate = 0.6 + (soc - 80)/100 * 4
            # elif soc >= 90:
            #     self.production_rate = 1.0
        
            # if self.el_state == 0:
            # #     # Try to turn ON the electrolyser
            #     if soc >= 80 and pv - load - self.production_rate*self.electrolzer_power> 0 and hour < 13 and not self.el_daily_flag and h2_soc < self.h2_soc_max:
            #         self.el_state = 1
            #         self.el_daily_flag = True
            #     else:
            #         self.el_state = 0

            # elif self.el_state == 1:
            #     # if (soc < 65) or (h2_soc >= self.h2_soc_max) or (pv < self.pv_threshold_stop_fraction * self.pv_threshold_start):
            #     if (soc < 65) or (pv - load - self.production_rate*self.electrolzer_power > self.transformer_capacity) or (h2_soc >= self.h2_soc_max):
            #         self.el_state = 0
            #     else:
            #         self.el_state = 1
            #         self.el_daily_flag = True
        
            # if self.el_state == 1:
            #     run_el = 1
            #     run_fc = 0 
            #     compressor_on = 1
            #     storage_flow = 1
            # elif self.el_state == 0:	
            #     run_el = 0
            #     compressor_on = 0

            # if self.fc_state == 0 and soc <= 25 and (load - pv) >= self.transformer_capacity and h2_soc >= self.h2_soc_min:
            #     self.fc_state = 1
            # # elif self.fc_state == 1 and soc >= 82 or h2_soc <= self.h2_soc_min:
            # elif self.fc_state == 1 and (load - pv) <= self.transformer_capacity or h2_soc <= self.h2_soc_min:
            #     self.fc_state = 0

            # if self.fc_state == 1 and h2_soc >= self.h2_soc_min and h2_soc <= self.h2_soc_max:
            #     run_el = 0
            #     run_fc = 1
            #     compressor_on = 0
            #     storage_flow = -1
            # elif self.fc_state == 0:
            #     run_fc = 0
            # # if soc <= 25 and h2_soc >= self.h2_soc_min and (load - pv) >= self.fc_threshold_start:
            # #     self.fc_state = 1
            # # elif self.fc_state == 1:
            # #     if soc >= 82 and (pv-load+self.fc_threshold_start) >= 0 or h2_soc <= self.h2_soc_min:
            # #         self.fc_state = 0
            # #     else:
            # #         self.fc_state = 1
            # # else:
            # #     self.fc_state = 0

        if is_winter:
            run_el = 0 
            if self.fc_state == 0 and soc <= self.fc_emergency_soc and (load - pv) >= self.transformer_capacity and h2_soc >= self.h2_soc_min:
                self.fc_state = 1
            
            elif self.fc_state == 1 and ((load-pv) < self.transformer_capacity or h2_soc <= self.h2_soc_min):
                self.fc_state = 0

            if self.fc_state == 1 and h2_soc >= self.h2_soc_min and h2_soc <= self.h2_soc_max:
                run_fc = 1
                storage_flow = -1
            else:
                run_fc = 0
            # if self.fc_state == 0 and soc <= 25 and (load - pv) >= self.fc_threshold_start and h2_soc >= self.h2_soc_min:
            #     self.fc_state = 1
            # # elif self.fc_state == 1 and soc >= 82 or h2_soc <= self.h2_soc_min:
            # elif self.fc_state == 1 and (load - pv) <= self.transformer_capacity or h2_soc <= self.h2_soc_min:
            #     self.fc_state = 0
            # # elif self.fc_state == 0 and (load - pv) >= self.fc_threshold_start and h2_soc >= self.h2_soc_min:
            # #     if hour < 13 and soc < 40:
            # #         self.fc_state = 1
            # #     elif hour == 13 and soc < 50:
            # #         self.fc_state = 1
            # #     elif hour == 14 and soc < 60:
            # #         self.fc_state = 1   
            # #     elif hour == 15 and soc < 70:
            # #         self.fc_state = 1
            # #     elif hour == 16 and soc < 80:
            # #         self.fc_state = 1
        

            if self.fc_state == 1 and h2_soc >= self.h2_soc_min and h2_soc <= self.h2_soc_max:
                run_el = 0
                run_fc = 1
                compressor_on = 0
                storage_flow = -1
            elif self.fc_state == 0:
                run_fc = 0

        self.set_outputs({
            'run_electrolyser': run_el,
            'run_fuelcell': run_fc,
            'compressor_on': compressor_on,
            'storage_flow': storage_flow
        })

        self.set_states({
            'el_state': self.el_state,
            'fc_state': self.fc_state,
            'el_daily_flag': self.el_daily_flag,
            'production_rate': self.production_rate
        })

        return time + self.time_step_size

# # VERSION WITHOUT BATTERY CONTROL IN CONTROLLER BEFORE DELFTBLUE

# from illuminator.builder import ModelConstructor
# import numpy as np
# import datetime

# class EMSController(ModelConstructor):
#     parameters = {
#         'start_time': '2024-04-01 00:00:00',  # Start time of the simulation
#         'soc_min': 20,
#         'soc_max': 80,
#         'h2_soc_min': 6,
#         'h2_soc_max': 100,
#         'el_start_soc': 80,     # Battery SOC to start electrolyzer (%)
#         'el_stop_soc': 65,      # Battery SOC to stop electrolyzer (%)
#         'fc_emergency_soc': 25, # Battery SOC for emergency fuel cell start (%)
#         'fc_stop_soc': 90      # Battery SOC to stop fuel cell (%)
#         # 'fc_eff': 0.99,
#         # 'el_eff': 0.70,
#         # 'warmup_fc': 300,
#         # 'warmup_el': 180,
#         # 'ramp_rate_fc': 500,
#         # 'ramp_rate_el': 500,
#         # 'p_out_fc': 1.83 #kW estimated power output from fuel cell for battery control
#     }
#     inputs = {
#         'pv_signal': 0,
#         'soc': 50,
#         'h2_soc': 50,
#         # 'p_out_fuelcell_controller': 0  # Power output from fuel cell 
#     }
#     outputs = {
#         'run_electrolyser': 0,
#         'run_fuelcell': 0,
#         'compressor_on': 0,
#         'storage_flow': 0     # 1 = store H2, -1 = withdraw H2, 0 = idle
#     }
#     states = {
#         'el_state': 0,  # 0 = off, 1 = on
#         'fc_state': 0, # 0 = off, 1 = on
#         # 'bat_state': 'off',
#         'el_daily_flag': False,
#         'production_rate': 0  # Production rate of electrolyser
#     }

#     time_step_size = 1  
#     time = None

#     def __init__(self, **kwargs) -> None:
#         super().__init__(**kwargs)
#         self.start_time = self._model.parameters.get('start_time')
#         self.soc_min = self._model.parameters.get('soc_min')
#         self.soc_max = self._model.parameters.get('soc_max')
#         self.h2_soc_min = self._model.parameters.get('h2_soc_min')
#         self.h2_soc_max = self._model.parameters.get('h2_soc_max')
        
#         # self.fc_eff = self._model.parameters.get('fc_eff')
#         # self.el_eff = self._model.parameters.get('el_eff')
#         # self.warmup_fc = self._model.parameters.get('warmup_fc')
#         # self.warmup_el = self._model.parameters.get('warmup_el')
#         # self.ramp_rate_fc = self._model.parameters.get('ramp_rate_fc')
#         # self.ramp_rate_el = self._model.parameters.get('ramp_rate_el')
#         # self.p_out_fc = self._model.parameters.get('p_out_fc')
#         self.el_state = self._model.states.get('el_state')
#         self.fc_state = self._model.states.get('fc_state')
#         self.el_daily_flag = self._model.states.get('el_daily_flag')
#         self.production_rate = self._model.states.get('production_rate')


#     def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> None:
#         input_data = self.unpack_inputs(inputs)
#         pv = input_data['pv_signal']
#         soc = input_data['soc']
#         h2_soc = input_data['h2_soc']
#         # fc = input_data['p_out_fuelcell_controller']

#         start_time = datetime.datetime.strptime(inputs.get('start_time', self._model.parameters['start_time']), "%Y-%m-%d %H:%M:%S")
#         now = start_time + datetime.timedelta(seconds=time * self.time_resolution)
#         hour = now.hour
#         today_date = now.date()

#         # Define summer period (16th March to 14th October)
#         # is_winter = not (datetime.date(today_date.year, 3, 16) <= today_date <= datetime.date(today_date.year, 10, 14))
#         is_winter = datetime.date(today_date.year, 1, 2) <= today_date <= datetime.date(today_date.year, 3, 16) #forvalidationSOC

#         print(f"[{now}] Winter? {is_winter}, Hour: {hour}, Date: {today_date}")

#         # Reset daily flag on day change
#         today_dayofyear = now.timetuple().tm_yday
#         if not hasattr(self, 'last_day') or self.last_day != today_dayofyear:
#             self.last_day = today_dayofyear
#             self.el_daily_flag = False

#         run_el = 0
#         run_fc = 0
#         storage_flow = 0
#         compressor_on = 0
#         self.production_rate = 0

        
#         if not is_winter:
#             if self.el_state == 0:
#             #     # Try to turn ON the electrolyser
#                 if soc >= 80 and pv > 1 and hour < 12 and not self.el_daily_flag and h2_soc < self.h2_soc_max:
#                     self.el_state = 1
#                     self.el_daily_flag = True
                    

#             elif self.el_state == 1:
#                 if (soc < 65) or (h2_soc >= self.h2_soc_max) or (pv < 0.05):
#                     self.el_state = 0
#                 else:
#                     self.el_state = 1
        
#             if self.el_state == 1:
#                 run_el = 1
#                 run_fc = 0 
#                 compressor_on = 1
#                 storage_flow = 1
#             elif self.el_state == 0:	
#                 run_el = 0
#                 run_fc = 0
#                 compressor_on = 0

#             if soc < 80:
#                 self.production_rate = 0.6
#             elif soc >=80 and soc <= 90:
#                 self.production_rate = 0.6 + (soc - 80)/100 * 4
#             elif soc >= 90:
#                 self.production_rate = 1.0

#         if soc <= 25:
#             self.fc_state = 1
#         elif soc >= 90:
#             self.fc_state = 0

#         if is_winter:
#             run_el = 0 
            
#             if self.fc_state == 0 and soc <= 25 and h2_soc >= self.h2_soc_min:
#                 self.fc_state = 1
#             elif self.fc_state == 1 and soc > 90 and h2_soc >= self.h2_soc_max:
#                 self.fc_state = 0
#             elif self.fc_state == 0 and h2_soc >= self.h2_soc_min:
#                 if hour < 13 and soc < 40:
#                     self.fc_state = 1
#                 elif hour == 13 and soc < 50:
#                     self.fc_state = 1
#                 elif hour == 14 and soc < 60:
#                     self.fc_state = 1   
#                 elif hour == 15 and soc < 70:
#                     self.fc_state = 1
#                 elif hour == 16 and soc < 80:
#                     self.fc_state = 1
        
#         # elif is_winter:
#         #     run_el = 0 
#         #     # if self.fc_state == 0:
#         #     if hour < 13 and soc < 40:
#         #         self.fc_state = 1
#         #     elif hour < 14 and soc < 50:
#         #         self.fc_state = 1
#         #     elif hour < 15 and soc < 60:
#         #         self.fc_state = 1   
#         #     elif hour < 16 and soc < 70:
#         #         self.fc_state = 1
#         #     elif hour < 17 and soc < 80:
#         #         self.fc_state = 1
#         #     elif soc > 90:
#         #         self.fc_state = 0
#         #     else:
#         #         self.fc_state = 0

#             if self.fc_state == 1 and h2_soc >= self.h2_soc_min and h2_soc <= self.h2_soc_max:
#                 run_el = 0
#                 run_fc = 1
#                 compressor_on = 0
#                 storage_flow = -1
#             elif self.fc_state == 0:
#                 run_fc = 0

#         self.set_outputs({
#             'run_electrolyser': run_el,
#             'run_fuelcell': run_fc,
#             'compressor_on': compressor_on,
#             'storage_flow': storage_flow
#         })

#         self.set_states({
#             'el_state': self.el_state,
#             'fc_state': self.fc_state,
#             # 'el_daily_flag': self.states['el_daily_flag'], #voor DelftBlue
#             'el_daily_flag': self.el_daily_flag,
#             'production_rate': self.production_rate
#         })

#         return time + self.time_step_size