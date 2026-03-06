from illuminator.builder import ModelConstructor
import datetime
 
 
class BatteryController(ModelConstructor):
    """
    Battery controller for congestion mitigation with seasonal strategy.
    WINTER (Nov 1 - Mar 15):
    - Charging: Off-peak grid charging to 75% SOC
    - Discharging: ONLY when grid_flow > threshold (peak shaving)
    SPRING (Mar 16 - May 31):
    - Charging: Light off-peak grid charging to 50% SOC
    - Discharging: Normal self-consumption
    SUMMER (Jun 1 - Aug 31):
    - Charging: Minimal/no grid charging, rely on PV
    - Discharging: Normal self-consumption
    AUTUMN (Sep 1 - Oct 31):
    - Charging: Light off-peak grid charging to 50% SOC
    - Discharging: Normal self-consumption
    """
    parameters = {
        'start_time': '2050-01-01 00:00:00',
        # Winter settings (Nov 1 - Mar 15)
        'soc_target_winter': 75,
        'soc_activate_winter': 40,
        # Spring settings (Mar 16 - May 31)
        'soc_target_spring': 50,
        'soc_activate_spring': 30,
        # Summer settings (Jun 1 - Aug 31)
        'soc_target_summer': 40,
        'soc_activate_summer': 20,
        # Autumn settings (Sep 1 - Oct 31)
        'soc_target_autumn': 50,
        'soc_activate_autumn': 30,
        # Discharge settings (winter only)
        'discharge_threshold': 150,
        'soc_min_discharge': 25,
        'soc_max': 90,
        # System parameters
        'transformer_capacity': 250,
        'off_peak_start': 23,
        'off_peak_end': 6,
        'c_rate': 0.33,
        'max_energy': 15.36,
    }
    inputs = {
        'pv_signal': 0,
        'load_signal': 0,
        'soc': 50,
    }
    outputs = {
        'grid_charge_request': 0,
        'discharge_request': 0,
        'mode': 0,  # 0=hold, 1=grid_charge, 2=discharge, 3=pv_charge, 4=self_consumption
    }
    states = {
        'charging_active': 0,
    }
 
    time_step_size = 1
    time = None
 
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.start_time = self._model.parameters.get('start_time')
        # Winter
        self.soc_target_winter = self._model.parameters.get('soc_target_winter')
        self.soc_activate_winter = self._model.parameters.get('soc_activate_winter')
        # Spring
        self.soc_target_spring = self._model.parameters.get('soc_target_spring')
        self.soc_activate_spring = self._model.parameters.get('soc_activate_spring')
        # Summer
        self.soc_target_summer = self._model.parameters.get('soc_target_summer')
        self.soc_activate_summer = self._model.parameters.get('soc_activate_summer')
        # Autumn
        self.soc_target_autumn = self._model.parameters.get('soc_target_autumn')
        self.soc_activate_autumn = self._model.parameters.get('soc_activate_autumn')
        # Discharge
        self.discharge_threshold = self._model.parameters.get('discharge_threshold')
        self.soc_min_discharge = self._model.parameters.get('soc_min_discharge')
        self.soc_max = self._model.parameters.get('soc_max', 90)
        # System
        self.transformer_capacity = self._model.parameters.get('transformer_capacity')
        self.off_peak_start = self._model.parameters.get('off_peak_start')
        self.off_peak_end = self._model.parameters.get('off_peak_end')
        self.c_rate = self._model.parameters.get('c_rate')
        self.max_energy = self._model.parameters.get('max_energy')
        self.max_p_total = self.c_rate * self.max_energy
        self.charging_active = self._model.states.get('charging_active')
 
    def get_season(self, date):
        """
        Determine season based on date.
        Winter: Nov 1 - Mar 15
        Spring: Mar 16 - May 31
        Summer: Jun 1 - Aug 31
        Autumn: Sep 1 - Oct 31
        """
        month = date.month
        day = date.day
        if month >= 11 or month <= 2 or (month == 3 and day <= 15):
            return 'winter'
        elif (month == 3 and day >= 16) or month == 4 or month == 5:
            return 'spring'
        elif month >= 6 and month <= 8:
            return 'summer'
        else:  # Sep 1 - Oct 31
            return 'autumn'
 
    def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> None:
        input_data = self.unpack_inputs(inputs)
        pv = input_data['pv_signal']
        load = input_data['load_signal']
        soc = input_data['soc']
        # Read state at start of each step
        # self.charging_active = self._model.states.get('charging_active')
 
        # Parse current time
        start_time = datetime.datetime.strptime(
            inputs.get('start_time', self._model.parameters['start_time']),
            "%Y-%m-%d %H:%M:%S"
        )
        now = start_time + datetime.timedelta(seconds=time * self.time_resolution)
        hour = now.hour
        today_date = now.date()
 
        # Determine season
        season = self.get_season(today_date)
 
        # Select seasonal parameters
        if season == 'winter':
            soc_target = self.soc_target_winter
            soc_activate = self.soc_activate_winter
        elif season == 'spring':
            soc_target = self.soc_target_spring
            soc_activate = self.soc_activate_spring
        elif season == 'summer':
            soc_target = self.soc_target_summer
            soc_activate = self.soc_activate_summer
        else:  # autumn
            soc_target = self.soc_target_autumn
            soc_activate = self.soc_activate_autumn
 
        # Time periods
        is_off_peak = (hour >= self.off_peak_start) or (hour < self.off_peak_end)
        # Current grid load (without battery action)
        current_grid_load = load - pv
        # Initialize outputs
        grid_charge_request = 0
        discharge_request = 0
        mode = 0  # hold
 
        # ===== CHARGING LOGIC (off-peak hours) =====
        if is_off_peak:
            # Hysteresis logic:
            # - Start charging when SOC drops below soc_activate
            # - Keep charging until SOC reaches soc_target
            # - Once stopped, don't restart until SOC drops below soc_activate again
            if soc < soc_activate:
                self.charging_active = 1
            elif soc >= soc_target:
                self.charging_active = 0
            # else: keep current state (this is the hysteresis)
            # if self.charging_active == 1 and soc < soc_target:
            #     # Charge at max C-rate, limited by available transformer capacity
            #     desired_charge_rate = self.max_p_total
            #     available_capacity = self.transformer_capacity - max(0, current_grid_load)
            #     grid_charge_request = min(desired_charge_rate, available_capacity)
            #     grid_charge_request = max(0, grid_charge_request)
            #     if grid_charge_request > 0:
            #         mode = 1  # grid_charge
            else:
                self.charging_active = self.charging_active
        else:
            self.charging_active = 0

        if self.charging_active == 1 and soc < soc_target:
                # Charge at max C-rate, limited by available transformer capacity
            desired_charge_rate = self.max_p_total
            available_capacity = self.transformer_capacity - max(0, current_grid_load)
            grid_charge_request = min(desired_charge_rate, available_capacity)
            grid_charge_request = max(0, grid_charge_request)
            if grid_charge_request > 0:
                mode = 1  # grid_charge
 
        # ===== WINTER: Threshold-based discharge only =====
        if season == 'winter' and mode != 1:
            if soc > self.soc_min_discharge and current_grid_load > self.discharge_threshold:
                excess_load = current_grid_load - self.discharge_threshold
                discharge_request = min(excess_load, self.max_p_total)
                discharge_request = max(0, discharge_request)
                if discharge_request > 0:
                    mode = 2  # discharge
            elif current_grid_load < 0 and soc < self.soc_max:
                mode = 3  # pv_charge
            else:
                mode = 0  # hold
 
        # ===== SPRING/SUMMER/AUTUMN: Normal self-consumption =====
        elif season != 'winter' and mode != 1:
            if current_grid_load < 0 and soc < self.soc_max:
                mode = 3  # pv_charge
            elif current_grid_load > 0 and soc > self.soc_min_discharge:
                discharge_request = min(current_grid_load, self.max_p_total)
                mode = 4  # self_consumption
            else:
                mode = 0  # hold
 
        self.set_states({'charging_active': self.charging_active})
        self.set_outputs({
            'grid_charge_request': grid_charge_request,
            'discharge_request': discharge_request,
            'mode': mode
        })
        return time + self.time_step_size
# from illuminator.builder import ModelConstructor
# import datetime
 
 
# class BatteryController(ModelConstructor):
#     """
#     Battery controller for congestion mitigation with seasonal strategy.
#     WINTER (Nov 1 - Mar 15):
#     - Charging: Off-peak grid charging to 75% SOC
#     - Discharging: ONLY when grid_flow > threshold (peak shaving)
#     SPRING (Mar 16 - May 31):
#     - Charging: Light off-peak grid charging to 50% SOC
#     - Discharging: Normal self-consumption
#     SUMMER (Jun 1 - Aug 31):
#     - Charging: Minimal/no grid charging, rely on PV
#     - Discharging: Normal self-consumption
#     AUTUMN (Sep 1 - Oct 31):
#     - Charging: Light off-peak grid charging to 50% SOC
#     - Discharging: Normal self-consumption
#     """
#     parameters = {
#         'start_time': '2050-01-01 00:00:00',
#         # Winter settings (Nov 1 - Mar 15)
#         'soc_target_winter': 75,
#         'soc_activate_winter': 40,
#         # Spring settings (Mar 16 - May 31)
#         'soc_target_spring': 50,
#         'soc_activate_spring': 30,
#         # Summer settings (Jun 1 - Aug 31)
#         'soc_target_summer': 40,
#         'soc_activate_summer': 20,
#         # Autumn settings (Sep 1 - Oct 31)
#         'soc_target_autumn': 50,
#         'soc_activate_autumn': 30,
#         # Discharge settings (winter only)
#         'discharge_threshold': 150,
#         'soc_min_discharge': 25,
#         'soc_max': 90,
#         # System parameters
#         'transformer_capacity': 250,
#         'off_peak_start': 23,
#         'off_peak_end': 6,
#         'c_rate': 0.33,
#         'max_energy': 15.36,
#     }
#     inputs = {
#         'pv_signal': 0,
#         'load_signal': 0,
#         'soc': 50,
#     }
#     outputs = {
#         'grid_charge_request': 0,
#         'discharge_request': 0,
#         'mode': 0,  # 0=hold, 1=grid_charge, 2=discharge, 3=pv_charge, 4=self_consumption
#     }
#     states = {
#         'charging_active': False,
#     }
 
#     time_step_size = 1
 
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.start_time = self._model.parameters.get('start_time')
#         # Winter
#         self.soc_target_winter = self._model.parameters.get('soc_target_winter')
#         self.soc_activate_winter = self._model.parameters.get('soc_activate_winter')
#         # Spring
#         self.soc_target_spring = self._model.parameters.get('soc_target_spring')
#         self.soc_activate_spring = self._model.parameters.get('soc_activate_spring')
#         # Summer
#         self.soc_target_summer = self._model.parameters.get('soc_target_summer')
#         self.soc_activate_summer = self._model.parameters.get('soc_activate_summer')
#         # Autumn
#         self.soc_target_autumn = self._model.parameters.get('soc_target_autumn')
#         self.soc_activate_autumn = self._model.parameters.get('soc_activate_autumn')
#         # Discharge
#         self.discharge_threshold = self._model.parameters.get('discharge_threshold', 150)
#         self.soc_min_discharge = self._model.parameters.get('soc_min_discharge', 25)
#         self.soc_max = self._model.parameters.get('soc_max', 90)
#         # System
#         self.transformer_capacity = self._model.parameters.get('transformer_capacity')
#         self.off_peak_start = self._model.parameters.get('off_peak_start')
#         self.off_peak_end = self._model.parameters.get('off_peak_end')
#         self.c_rate = self._model.parameters.get('c_rate')
#         self.max_energy = self._model.parameters.get('max_energy')
#         self.max_p_total = self.c_rate * self.max_energy
#         self.charging_active = self._model.states.get('charging_active', False)
 
#     def get_season(self, date):
#         """
#         Determine season based on date.
#         Winter: Nov 1 - Mar 15
#         Spring: Mar 16 - May 31
#         Summer: Jun 1 - Aug 31
#         Autumn: Sep 1 - Oct 31
#         """
#         month = date.month
#         day = date.day
#         if month >= 11 or month <= 2 or (month == 3 and day <= 15):
#             return 'winter'
#         elif (month == 3 and day >= 16) or month == 4 or month == 5:
#             return 'spring'
#         elif month >= 6 and month <= 8:
#             return 'summer'
#         else:  # Sep 1 - Oct 31
#             return 'autumn'
 
#     def step(self, time: int, inputs: dict = None, max_advance: int = 900):
#         input_data = self.unpack_inputs(inputs)
#         pv = input_data['pv_signal']
#         load = input_data['load_signal']
#         soc = input_data['soc']
 
#         # Parse current time
#         start_time = datetime.datetime.strptime(
#             inputs.get('start_time', self._model.parameters['start_time']),
#             "%Y-%m-%d %H:%M:%S"
#         )
#         now = start_time + datetime.timedelta(seconds=time * self.time_resolution)
#         hour = now.hour
#         today_date = now.date()
 
#         # Determine season
#         season = self.get_season(today_date)
 
#         # Select seasonal parameters
#         if season == 'winter':
#             soc_target = self.soc_target_winter
#             soc_activate = self.soc_activate_winter
#         elif season == 'spring':
#             soc_target = self.soc_target_spring
#             soc_activate = self.soc_activate_spring
#         elif season == 'summer':
#             soc_target = self.soc_target_summer
#             soc_activate = self.soc_activate_summer
#         else:  # autumn
#             soc_target = self.soc_target_autumn
#             soc_activate = self.soc_activate_autumn
 
#         # Time periods
#         is_off_peak = (hour >= self.off_peak_start) or (hour < self.off_peak_end)
#         # Current grid load (without battery action)
#         current_grid_load = load - pv
#         # Initialize outputs
#         grid_charge_request = 0
#         discharge_request = 0
#         mode = 0  # hold
 
#         # ===== CHARGING LOGIC (off-peak hours) =====
#         if is_off_peak:
#             if soc < soc_activate:
#                 self.charging_active = True
#             elif soc >= soc_target:
#                 self.charging_active = False
#             if self.charging_active and soc < soc_target:
#                 soc_deficit = soc_target - soc
#                 energy_needed = (soc_deficit / 100) * self.max_energy
#                 if hour >= self.off_peak_start:
#                     hours_remaining = (24 - hour) + self.off_peak_end
#                 else:
#                     hours_remaining = self.off_peak_end - hour
#                 hours_remaining = max(hours_remaining, 0.25)
#                 desired_charge_rate = energy_needed / hours_remaining
#                 desired_charge_rate = min(desired_charge_rate, self.max_p_total)
#                 available_capacity = self.transformer_capacity - max(0, current_grid_load)
#                 grid_charge_request = min(desired_charge_rate, available_capacity)
#                 grid_charge_request = max(0, grid_charge_request)
#                 if grid_charge_request > 0:
#                     mode = 1  # grid_charge
#         else:
#             self.charging_active = False
 
#         # ===== WINTER: Threshold-based discharge only =====
#         if season == 'winter' and mode != 1:
#             if soc > self.soc_min_discharge and current_grid_load > self.discharge_threshold:
#                 excess_load = current_grid_load - self.discharge_threshold
#                 discharge_request = min(excess_load, self.max_p_total)
#                 discharge_request = max(0, discharge_request)
#                 if discharge_request > 0:
#                     mode = 2  # discharge
#             elif current_grid_load < 0 and soc < self.soc_max:
#                 mode = 3  # pv_charge
#             else:
#                 mode = 0  # hold
 
#         # ===== SPRING/SUMMER/AUTUMN: Normal self-consumption =====
#         elif season != 'winter' and mode != 1:
#             if current_grid_load < 0 and soc < self.soc_max:
#                 mode = 3  # pv_charge
#             elif current_grid_load > 0 and soc > self.soc_min_discharge:
#                 discharge_request = min(current_grid_load, self.max_p_total)
#                 mode = 4  # self_consumption
#             else:
#                 mode = 0  # hold
 
#         self.set_states({'charging_active': self.charging_active})
#         self.set_outputs({
#             'grid_charge_request': grid_charge_request,
#             'discharge_request': discharge_request,
#             'mode': mode
#         })
#         return time + self.time_step_size
    
# from illuminator.builder import ModelConstructor
# import datetime
 
 
# class BatteryController(ModelConstructor):
#     """
#     Battery controller for congestion mitigation with seasonal strategy.
#     WINTER (Oct 15 - Mar 15):
#     - Charging: Off-peak grid charging to 75% SOC
#     - Discharging: ONLY when grid_flow > threshold (e.g., 150 kW)
#     - Otherwise: Hold (save energy for peak moments)
#     SUMMER (Mar 16 - Oct 14):
#     - Charging: PV self-consumption + light off-peak if SOC very low
#     - Discharging: Normal self-consumption (when load > pv)
#     - No threshold logic - let battery work naturally
#     """
#     parameters = {
#         'start_time': '2050-01-01 00:00:00',
#         # Winter settings
#         'soc_target_winter': 75,       # Target SOC in winter (%)
#         'soc_activate_winter': 40,     # Start grid charging if SOC below this (%)
#         # Summer settings  
#         'soc_target_summer': 50,       # Target SOC in summer (%)
#         'soc_activate_summer': 30,     # Start grid charging if SOC below this (%)
#         'soc_max': 90,               # Max SOC (%)
#         # Discharge settings (winter only)
#         'discharge_threshold': 150,    # Winter: discharge when grid_flow > this (kW)
#         'soc_min_discharge': 25,       # Don't discharge below this SOC (%)
#         # System parameters
#         'transformer_capacity': 250,   # kW - transformer limit
#         'off_peak_start': 23,          # Off-peak starts at 23:00
#         'off_peak_end': 6,             # Off-peak ends at 06:00
#         'c_rate': 0.33,                # Battery C-rate
#         'max_energy': 15.36,           # Battery capacity per household (kWh)
#     }
#     inputs = {
#         'pv_signal': 0,      # Total PV generation (kW)
#         'load_signal': 0,    # Total load (kW)
#         'soc': 50,           # Battery SOC (%)
#     }
#     outputs = {
#         'grid_charge_request': 0,   # Power to charge from grid (kW)
#         'discharge_request': 0,     # Power to discharge (kW)
#         'mode': 0,                  # 0=hold, 1=grid_charge, 2=discharge, 3=pv_charge, 4=self_consumption
#     }
#     states = {
#         'charging_active': False,  # Hysteresis flag for grid charging
#     }
 
#     time_step_size = 1
 
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.start_time = self._model.parameters.get('start_time')
#         # Winter
#         self.soc_target_winter = self._model.parameters.get('soc_target_winter')
#         self.soc_activate_winter = self._model.parameters.get('soc_activate_winter')
#         # Summer
#         self.soc_target_summer = self._model.parameters.get('soc_target_summer')
#         self.soc_activate_summer = self._model.parameters.get('soc_activate_summer')
#         self.soc_max = self._model.parameters.get('soc_max')
#         # Discharge
#         self.discharge_threshold = self._model.parameters.get('discharge_threshold', 150)
#         self.soc_min_discharge = self._model.parameters.get('soc_min_discharge', 25)
#         # System
#         self.transformer_capacity = self._model.parameters.get('transformer_capacity')
#         self.off_peak_start = self._model.parameters.get('off_peak_start')
#         self.off_peak_end = self._model.parameters.get('off_peak_end')
#         self.c_rate = self._model.parameters.get('c_rate')
#         self.max_energy = self._model.parameters.get('max_energy')
#         # Calculate max power from C-rate
#         self.max_p_total = self.c_rate * self.max_energy
#         # Hysteresis state
#         self.charging_active = self._model.states.get('charging_active', False)
 
#     def step(self, time: int, inputs: dict = None, max_advance: int = 900):
#         input_data = self.unpack_inputs(inputs)
#         pv = input_data['pv_signal']
#         load = input_data['load_signal']
#         soc = input_data['soc']
 
#         # Parse current time
#         start_time = datetime.datetime.strptime(
#             inputs.get('start_time', self._model.parameters['start_time']),
#             "%Y-%m-%d %H:%M:%S"
#         )
#         now = start_time + datetime.timedelta(seconds=time * self.time_resolution)
#         hour = now.hour
#         today_date = now.date()
 
#         # Determine season (winter: Oct 15 - Mar 15)
#         # is_winter = not (datetime.date(today_date.year, 4, 16) <= today_date <= datetime.date(today_date.year, 10, 14))
#         is_winter = not (datetime.date(today_date.year, 4, 1) <= today_date <= datetime.date(today_date.year, 10, 14))
 
#         # Select seasonal parameters
#         if is_winter:
#             soc_target = self.soc_target_winter
#             soc_activate = self.soc_activate_winter
#         else:
#             soc_target = self.soc_target_summer
#             soc_activate = self.soc_activate_summer
 
#         # Time periods
#         is_off_peak = (hour >= self.off_peak_start) or (hour < self.off_peak_end)
#         # Current grid load (without battery action)
#         current_grid_load = load - pv  # Positive = import, negative = export
#         # Initialize outputs
#         grid_charge_request = 0
#         discharge_request = 0
#         mode = 0  # 0 = hold
 
#         # ===== CHARGING LOGIC (off-peak hours) =====
#         if is_off_peak:
#             # Hysteresis for grid charging
#             if soc < soc_activate:
#                 self.charging_active = True
#             elif soc >= soc_target:
#                 self.charging_active = False
#             if self.charging_active and soc < soc_target:
#                 # Calculate energy needed
#                 soc_deficit = soc_target - soc
#                 energy_needed = (soc_deficit / 100) * self.max_energy
#                 # Hours remaining in off-peak
#                 if hour >= self.off_peak_start:
#                     hours_remaining = (24 - hour) + self.off_peak_end
#                 else:
#                     hours_remaining = self.off_peak_end - hour
#                 hours_remaining = max(hours_remaining, 0.25)
#                 # Desired rate (spread over remaining hours)
#                 desired_charge_rate = energy_needed / hours_remaining
#                 desired_charge_rate = min(desired_charge_rate, self.max_p_total)
#                 # Available transformer capacity
#                 available_capacity = self.transformer_capacity - max(0, current_grid_load)
#                 # Final request
#                 grid_charge_request = min(desired_charge_rate, available_capacity)
#                 grid_charge_request = max(0, grid_charge_request)
#                 if grid_charge_request > 0:
#                     mode = 1  # grid_charge
#         else:
#             # Outside off-peak: reset charging flag
#             self.charging_active = False
 
#         # ===== WINTER: Threshold-based discharge =====
#         if is_winter and mode != 1:
#             if soc > self.soc_min_discharge and current_grid_load > self.discharge_threshold:
#                 # Discharge only the excess above threshold
#                 excess_load = current_grid_load - self.discharge_threshold
#                 discharge_request = min(excess_load, self.max_p_total)
#                 discharge_request = max(0, discharge_request)
#                 if discharge_request > 0:
#                     mode = 2  # discharge
#             elif current_grid_load < 0 and soc < self.soc_max:
#                 # PV excess in winter - still allow charging
#                 mode = 3  # pv_charge
#             else:
#                 # Hold - don't discharge, wait for high grid load
#                 mode = 0  # hold
 
#         # ===== SUMMER: Normal self-consumption =====
#         elif not is_winter and mode != 1:
#             if current_grid_load < 0 and soc < self.soc_max:
#                 # PV excess - charge battery
#                 mode = 3  # pv_charge
#             elif current_grid_load > 0 and soc > self.soc_min_discharge:
#                 # Load > PV - discharge for self-consumption
#                 discharge_request = min(current_grid_load, self.max_p_total)
#                 mode = 4  # self_consumption
#             else:
#                 mode = 0  # hold
 
#         self.set_states({'charging_active': self.charging_active})
#         self.set_outputs({
#             'grid_charge_request': grid_charge_request,
#             'discharge_request': discharge_request,
#             'mode': mode
#         })
#         return time + self.time_step_size

# from illuminator.builder import ModelConstructor
# import datetime
 
 
# class BatteryController(ModelConstructor):
#     """
#     Battery controller for congestion mitigation.
#     Charging (off-peak 23:00-06:00):
#     - Winter: Charge to 75% SOC if below 40%
#     - Summer: Charge to 50% SOC if below 30%
#     Discharging (any time):
#     - When grid_flow > threshold: discharge only the excess above threshold
#     - Example: threshold=150kW, grid_flow=200kW → discharge 50kW
#     """
#     parameters = {
#         'start_time': '2050-01-01 00:00:00',
#         # Winter settings
#         'soc_target_winter': 75,       # Target SOC in winter (%)
#         'soc_activate_winter': 40,     # Start grid charging if SOC below this (%)
#         # Summer settings  
#         'soc_target_summer': 50,       # Target SOC in summer (%)
#         'soc_activate_summer': 30,     # Start grid charging if SOC below this (%)
#         # Discharge settings
#         'discharge_threshold': 150,    # Discharge when grid_flow > this (kW)
#         'soc_min_discharge': 25,       # Don't discharge below this SOC (%)
#         # System parameters
#         'transformer_capacity': 250,   # kW - transformer limit
#         'off_peak_start': 23,          # Off-peak starts at 23:00
#         'off_peak_end': 6,             # Off-peak ends at 06:00
#         'c_rate': 0.33,                # Battery C-rate
#         'max_energy': 15.36,           # Battery capacity per household (kWh)
#     }
#     inputs = {
#         'pv_signal': 0,      # Total PV generation (kW)
#         'load_signal': 0,    # Total load (kW)
#         'soc': 50,           # Battery SOC (%)
#     }
#     outputs = {
#         'grid_charge_request': 0,   # Power to charge from grid (kW)
#         'discharge_request': 0,     # Power to discharge (kW)
#         'mode': 0,                  # 0=hold, 1=charge, 2=discharge, 3=pv_charge
#     }
#     states = {
#         'charging_active': False,  # Hysteresis flag for grid charging
#     }
 
#     time_step_size = 1
 
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.start_time = self._model.parameters.get('start_time')
#         # Winter
#         self.soc_target_winter = self._model.parameters.get('soc_target_winter')
#         self.soc_activate_winter = self._model.parameters.get('soc_activate_winter')
#         # Summer
#         self.soc_target_summer = self._model.parameters.get('soc_target_summer')
#         self.soc_activate_summer = self._model.parameters.get('soc_activate_summer')
#         # Discharge
#         self.discharge_threshold = self._model.parameters.get('discharge_threshold')
#         self.soc_min_discharge = self._model.parameters.get('soc_min_discharge')
#         # System
#         self.transformer_capacity = self._model.parameters.get('transformer_capacity')
#         self.off_peak_start = self._model.parameters.get('off_peak_start')
#         self.off_peak_end = self._model.parameters.get('off_peak_end')
#         self.c_rate = self._model.parameters.get('c_rate')
#         self.max_energy = self._model.parameters.get('max_energy')
#         # Calculate max power from C-rate
#         self.max_p_total = self.c_rate * self.max_energy
#         # Hysteresis state
#         self.charging_active = self._model.states.get('charging_active', False)
 
#     def step(self, time: int, inputs: dict = None, max_advance: int = 900):
#         input_data = self.unpack_inputs(inputs)
#         pv = input_data['pv_signal']
#         load = input_data['load_signal']
#         soc = input_data['soc']
 
#         # Parse current time
#         start_time = datetime.datetime.strptime(
#             inputs.get('start_time', self._model.parameters['start_time']),
#             "%Y-%m-%d %H:%M:%S"
#         )
#         now = start_time + datetime.timedelta(seconds=time * self.time_resolution)
#         hour = now.hour
#         today_date = now.date()
 
#         # Determine season (winter: Oct 15 - Mar 15)
#         is_winter = not (datetime.date(today_date.year, 3, 16) <= today_date <= datetime.date(today_date.year, 10, 14))
 
#         # Select seasonal parameters
#         if is_winter:
#             soc_target = self.soc_target_winter
#             soc_activate = self.soc_activate_winter
#         else:
#             soc_target = self.soc_target_summer
#             soc_activate = self.soc_activate_summer
 
#         # Time periods
#         is_off_peak = (hour >= self.off_peak_start) or (hour < self.off_peak_end)
#         # Current grid load (without battery action)
#         current_grid_load = load - pv  # Positive = import, negative = export
#         # Initialize outputs
#         grid_charge_request = 0
#         discharge_request = 0
#         mode = 0  # 0 = hold
 
#         # ===== CHARGING LOGIC (off-peak hours) =====
#         if is_off_peak:
#             # Hysteresis for grid charging
#             if soc < soc_activate:
#                 self.charging_active = True
#             elif soc >= soc_target:
#                 self.charging_active = False
#             if self.charging_active and soc < soc_target:
#                 # Calculate energy needed
#                 soc_deficit = soc_target - soc
#                 energy_needed = (soc_deficit / 100) * self.max_energy
#                 # Hours remaining in off-peak
#                 if hour >= self.off_peak_start:
#                     hours_remaining = (24 - hour) + self.off_peak_end
#                 else:
#                     hours_remaining = self.off_peak_end - hour
#                 hours_remaining = max(hours_remaining, 0.25)
#                 # Desired rate (spread over remaining hours)
#                 desired_charge_rate = energy_needed / hours_remaining
#                 desired_charge_rate = min(desired_charge_rate, self.max_p_total)
#                 # Available transformer capacity
#                 available_capacity = self.transformer_capacity - max(0, current_grid_load)
#                 # Final request
#                 grid_charge_request = min(desired_charge_rate, available_capacity)
#                 grid_charge_request = max(0, grid_charge_request)
#                 if grid_charge_request > 0:
#                     mode = 1  # charge
#         else:
#             # Outside off-peak: reset charging flag
#             self.charging_active = False
 
#         # ===== DISCHARGE LOGIC (threshold-based) =====
#         # Only discharge if:
#         # - Not currently charging from grid
#         # - SOC is above minimum
#         # - Grid flow exceeds threshold
#         if mode != 1 and soc > self.soc_min_discharge and current_grid_load > self.discharge_threshold:
#             # Discharge only the excess above threshold
#             excess_load = current_grid_load - self.discharge_threshold
#             # Limit to C-rate
#             discharge_request = min(excess_load, self.max_p_total)
#             discharge_request = max(0, discharge_request)
#             if discharge_request > 0:
#                 mode = 2  # discharge
 
#         # ===== PV CHARGING (when PV excess) =====
#         if mode == 0 and current_grid_load < 0 and soc < 90:
#             mode = 3  # pv_charge
 
#         # Debug output
#         season_str = "Winter" if is_winter else "Summer"
#         mode_str = {0: 'hold', 1: 'grid_charge', 2: 'discharge', 3: 'pv_charge'}
#         if grid_charge_request > 0 or discharge_request > 0:
#             print(f"[{now}] {season_str} | Mode: {mode_str[mode]} | "
#                   f"SOC={soc:.1f}% | Grid={current_grid_load:.1f}kW | "
#                   f"Charge={grid_charge_request:.1f}kW | Discharge={discharge_request:.1f}kW")
 
#         self.set_states({'charging_active': self.charging_active})
#         self.set_outputs({
#             'grid_charge_request': grid_charge_request,
#             'discharge_request': discharge_request,
#             'mode': mode
#         })
#         return time + self.time_step_size
# from illuminator.builder import ModelConstructor
# import datetime
 
 
# class BatteryController(ModelConstructor):
#     """
#     Battery controller for off-peak grid charging with seasonal strategy.
#     Winter (Oct 15 - Mar 15): Charge to higher SOC for evening peak support
#     Summer (Mar 16 - Oct 14): Light charging to buffer morning peak, leave room for PV
#     Charges during off-peak hours (23:00 - 06:00) while respecting transformer limits.
#     Logic:
#     - Activate charging when SOC drops below soc_activate
#     - Keep charging until SOC reaches soc_target
#     - This prevents oscillation between charging/discharging
#     """
#     parameters = {
#         'start_time': '2050-01-01 00:00:00',
#         # Winter settings
#         'soc_target_winter': 75,       # Target SOC in winter (%)
#         'soc_activate_winter': 40,     # Start charging if SOC below this in winter (%)
#         # Summer settings  
#         'soc_target_summer': 50,       # Target SOC in summer (%)
#         'soc_activate_summer': 30,     # Start charging if SOC below this in summer (%)
#         # System parameters
#         'transformer_capacity': 250,   # kW - transformer limit
#         'off_peak_start': 23,          # Off-peak starts at 23:00
#         'off_peak_end': 6,             # Off-peak ends at 06:00
#         'c_rate': 0.33,                # Battery C-rate
#         'max_energy': 15.36,           # Battery capacity per household (kWh)
#     }
#     inputs = {
#         'pv_signal': 0,      # Total PV generation (kW)
#         'load_signal': 0,    # Total load (kW)
#         'soc': 50,           # Battery SOC (%)
#     }
#     outputs = {
#         'grid_charge_request': 0,  # Power to charge from grid (kW)
#     }
#     states = {
#         'charging_active': False,  # Hysteresis flag to prevent oscillation
#     }
 
#     time_step_size = 1
 
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.start_time = self._model.parameters.get('start_time')
#         # Winter
#         self.soc_target_winter = self._model.parameters.get('soc_target_winter')
#         self.soc_activate_winter = self._model.parameters.get('soc_activate_winter')
#         # Summer
#         self.soc_target_summer = self._model.parameters.get('soc_target_summer')
#         self.soc_activate_summer = self._model.parameters.get('soc_activate_summer')
#         # System
#         self.transformer_capacity = self._model.parameters.get('transformer_capacity')
#         self.off_peak_start = self._model.parameters.get('off_peak_start')
#         self.off_peak_end = self._model.parameters.get('off_peak_end')
#         self.c_rate = self._model.parameters.get('c_rate')
#         self.max_energy = self._model.parameters.get('max_energy')
#         # Calculate max power from C-rate (for limiting)
#         self.max_p_total = self.c_rate * self.max_energy
#         # Hysteresis state
#         self.charging_active = self._model.states.get('charging_active', False)
 
#     def step(self, time: int, inputs: dict = None, max_advance: int = 900):
#         input_data = self.unpack_inputs(inputs)
#         pv = input_data['pv_signal']
#         load = input_data['load_signal']
#         soc = input_data['soc']
 
#         # Parse current time
#         start_time = datetime.datetime.strptime(
#             inputs.get('start_time', self._model.parameters['start_time']),
#             "%Y-%m-%d %H:%M:%S"
#         )
#         now = start_time + datetime.timedelta(seconds=time * self.time_resolution)
#         hour = now.hour
#         today_date = now.date()
 
#         # Determine season (winter: Oct 15 - Mar 15)
#         is_winter = not (datetime.date(today_date.year, 3, 16) <= today_date <= datetime.date(today_date.year, 10, 14))
 
#         # Select seasonal parameters
#         if is_winter:
#             soc_target = self.soc_target_winter
#             soc_activate = self.soc_activate_winter
#         else:
#             soc_target = self.soc_target_summer
#             soc_activate = self.soc_activate_summer
 
#         # Check if we're in off-peak hours (23:00 - 06:00)
#         is_off_peak = (hour >= self.off_peak_start) or (hour < self.off_peak_end)
 
#         grid_charge_request = 0
 
#         # Hysteresis logic to prevent oscillation:
#         # - Turn ON charging when SOC drops below soc_activate
#         # - Keep charging ON until SOC reaches soc_target
#         # - Turn OFF when outside off-peak hours
#         if not is_off_peak:
#             # Outside off-peak: always off
#             self.charging_active = False
#         elif soc < soc_activate:
#             # SOC dropped below activation threshold: turn on
#             self.charging_active = True
#         elif soc >= soc_target:
#             # SOC reached target: turn off
#             self.charging_active = False
#         # else: keep current state (hysteresis)
 
#         if is_off_peak and self.charging_active:
#             # Calculate energy needed to reach target
#             soc_deficit = soc_target - soc  # %
#             if soc_deficit > 0:
#                 energy_needed = (soc_deficit / 100) * self.max_energy  # kWh
#                 # Calculate remaining off-peak hours
#                 if hour >= self.off_peak_start:
#                     hours_remaining = (24 - hour) + self.off_peak_end
#                 else:
#                     hours_remaining = self.off_peak_end - hour
#                 hours_remaining = max(hours_remaining, 0.25)  # Avoid division by zero
#                 # Desired charging rate (spread evenly)
#                 desired_charge_rate = energy_needed / hours_remaining  # kW
#                 # Limit to C-rate maximum
#                 desired_charge_rate = min(desired_charge_rate, self.max_p_total)
#                 # Calculate current grid load from load and pv
#                 current_grid_load = max(0, load - pv)  # Net import only
#                 available_capacity = self.transformer_capacity - current_grid_load
#                 # Final charge request
#                 grid_charge_request = min(desired_charge_rate, available_capacity)
#                 grid_charge_request = max(0, grid_charge_request)
#                 season_str = "Winter" if is_winter else "Summer"
#                 print(f"[{now}] {season_str} off-peak: SOC={soc:.1f}%, "
#                       f"Target={soc_target}%, "
#                       f"Hours left={hours_remaining:.1f}h, "
#                       f"Grid load={current_grid_load:.1f}kW, "
#                       f"Available={available_capacity:.1f}kW, "
#                       f"Charge request={grid_charge_request:.1f}kW")
 
#         self.set_states({'charging_active': self.charging_active})
#         self.set_outputs({'grid_charge_request': grid_charge_request})
#         return time + self.time_step_size
# from illuminator.builder import ModelConstructor
# import datetime
 
 
# class BatteryController(ModelConstructor):
#     """
#     Battery controller for off-peak grid charging with seasonal strategy.
#     Winter (Oct 15 - Mar 15): Charge to higher SOC for evening peak support
#     Summer (Mar 16 - Oct 14): Light charging to buffer morning peak, leave room for PV
#     Charges during off-peak hours (23:00 - 06:00) while respecting transformer limits.
#     """
#     parameters = {
#         'start_time': '2050-01-01 00:00:00',
#         # Winter settings
#         'soc_target_winter': 75,       # Target SOC in winter (%)
#         'soc_activate_winter': 40,     # Only charge if SOC below this in winter (%)
#         # Summer settings  
#         'soc_target_summer': 50,       # Target SOC in summer (%)
#         'soc_activate_summer': 30,     # Only charge if SOC below this in summer (%)
#         # System parameters
#         'transformer_capacity': 250,   # kW - transformer limit
#         'off_peak_start': 23,          # Off-peak starts at 23:00
#         'off_peak_end': 6,             # Off-peak ends at 06:00
#         'c_rate': 0.33,                # Battery C-rate
#         'max_energy': 15.36,           # Battery capacity per household (kWh)
#         # 'n_households': 155,           # Number of households with batteries
#     }
#     inputs = {
#         'pv_signal': 0,      # Total PV generation (kW)
#         'load_signal': 0,    # Total load (kW)
#         'soc': 50,           # Battery SOC (%)
#     }
#     outputs = {
#         'grid_charge_request': 0,  # Power to charge from grid (kW)
#     }
 
#     time_step_size = 1
 
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.start_time = self._model.parameters.get('start_time')
#         # Winter
#         self.soc_target_winter = self._model.parameters.get('soc_target_winter')
#         self.soc_activate_winter = self._model.parameters.get('soc_activate_winter')
#         # Summer
#         self.soc_target_summer = self._model.parameters.get('soc_target_summer')
#         self.soc_activate_summer = self._model.parameters.get('soc_activate_summer')
#         # System
#         self.transformer_capacity = self._model.parameters.get('transformer_capacity')
#         self.off_peak_start = self._model.parameters.get('off_peak_start')
#         self.off_peak_end = self._model.parameters.get('off_peak_end')
#         self.c_rate = self._model.parameters.get('c_rate')
#         self.max_energy = self._model.parameters.get('max_energy')
#         # self.n_households = self._model.parameters.get('n_households')
#         # Calculate max power from C-rate (for limiting)
#         self.max_p_total = self.c_rate * self.max_energy
#         # self.max_p_per_hh = self.c_rate * self.max_energy
#         # self.max_p_total = self.max_p_per_hh * self.n_households
 
#     def step(self, time: int, inputs: dict = None, max_advance: int = 900):
#         input_data = self.unpack_inputs(inputs)
#         pv = input_data['pv_signal']
#         load = input_data['load_signal']
#         soc = input_data['soc']
 
#         # Parse current time
#         start_time = datetime.datetime.strptime(
#             inputs.get('start_time', self._model.parameters['start_time']), 
#             "%Y-%m-%d %H:%M:%S"
#         )
#         now = start_time + datetime.timedelta(seconds=time * self.time_resolution)
#         hour = now.hour
#         today_date = now.date()
 
#         # Determine season (winter: Oct 15 - Mar 15)
#         is_winter = not (datetime.date(today_date.year, 3, 16) <= today_date <= datetime.date(today_date.year, 10, 14))
 
#         # Select seasonal parameters
#         if is_winter:
#             soc_target = self.soc_target_winter
#             soc_activate = self.soc_activate_winter
#         else:
#             soc_target = self.soc_target_summer
#             soc_activate = self.soc_activate_summer
 
#         # Check if we're in off-peak hours (23:00 - 06:00)
#         is_off_peak = (hour >= self.off_peak_start) or (hour < self.off_peak_end)
 
#         grid_charge_request = 0
 
#         # Grid charge during off-peak when SOC is below activation threshold
#         if is_off_peak and soc < soc_activate:
#             # Calculate energy needed to reach target
#             soc_deficit = soc_target - soc  # %
#             if soc_deficit > 0:
#                 # energy_needed = (soc_deficit / 100) * self.max_energy * self.n_households  # kWh
#                 energy_needed = (soc_deficit / 100) * self.max_energy  # kWh
#                 # Calculate remaining off-peak hours
#                 if hour >= self.off_peak_start:
#                     hours_remaining = (24 - hour) + self.off_peak_end
#                 else:
#                     hours_remaining = self.off_peak_end - hour
#                 hours_remaining = max(hours_remaining, 0.25)  # Avoid division by zero
#                 # Desired charging rate (spread evenly)
#                 desired_charge_rate = energy_needed / hours_remaining  # kW
#                 # Limit to C-rate maximum
#                 desired_charge_rate = min(desired_charge_rate, self.max_p_total)
#                 # Calculate current grid load from load and pv
#                 current_grid_load = max(0, load - pv)  # Net import only
#                 available_capacity = self.transformer_capacity - current_grid_load
#                 # Final charge request
#                 grid_charge_request = min(desired_charge_rate, available_capacity)
#                 grid_charge_request = max(0, grid_charge_request)
#                 season_str = "Winter" if is_winter else "Summer"
#                 print(f"[{now}] {season_str} off-peak: SOC={soc:.1f}%, "
#                       f"Target={soc_target}%, "
#                       f"Hours left={hours_remaining:.1f}h, "
#                       f"Grid load={current_grid_load:.1f}kW, "
#                       f"Charge request={grid_charge_request:.1f}kW")
 
#         self.set_outputs({'grid_charge_request': grid_charge_request})
#         return time + self.time_step_size

# from illuminator.builder import ModelConstructor
# import numpy as np
# import datetime

# class BatteryController(ModelConstructor):
#     parameters = {
#         'start_time': '2024-04-01 00:00:00',  # Start time of the simulation
#         'soc_start': 20,
#         'soc_stop': 80,
#         'transformer_capacity': 250  # kW
#     }
#     inputs = {
#         'pv_signal': 0,
#         'load_signal': 0,
#         'soc': 50,
#     }
#     outputs = {
#         'run_battery': 0,
#     }
#     # states = {
#     #     # 'bat_state': 'off',
#     #     'el_daily_flag': False,
#     #     'production_rate': 0  # Production rate of electrolyser
#     # }

#     time_step_size = 1  
#     time = None

#     def __init__(self, **kwargs) -> None:
#         super().__init__(**kwargs)
#         self.start_time = self._model.parameters.get('start_time')
#         self.soc_start = self._model.parameters.get('soc_start')
#         self.soc_stop = self._model.parameters.get('soc_stop')
#         self.transformer_capacity = self._model.parameters.get('transformer_capacity')


#     def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> None:
#         input_data = self.unpack_inputs(inputs)
#         pv = input_data['pv_signal']
#         load = input_data['load_signal']
#         soc = input_data['soc']

#         start_time = datetime.datetime.strptime(inputs.get('start_time', self._model.parameters['start_time']), "%Y-%m-%d %H:%M:%S")
#         now = start_time + datetime.timedelta(seconds=time * self.time_resolution)
#         hour = now.hour
#         today_date = now.date()

#         # Define summer period (16th March to 14th October)
#         is_winter = not (datetime.date(today_date.year, 3, 16) <= today_date <= datetime.date(today_date.year, 10, 14))
#         # is_winter = datetime.date(today_date.year, 1, 2) <= today_date <= datetime.date(today_date.year, 3, 16) #forvalidationSOC

#         print(f"[{now}] Winter? {is_winter}, Hour: {hour}, Date: {today_date}")

#         # Reset daily flag on day change
#         today_dayofyear = now.timetuple().tm_yday
#         if not hasattr(self, 'last_day') or self.last_day != today_dayofyear:
#             self.last_day = today_dayofyear
#             self.el_daily_flag = False

#         if hour > 23 and hour < 6 and soc <= self.soc_start:
#             run_battery = 1
#             if soc >= self.soc_stop:
#                 run_battery = 0 
#             else:
#                 run_battery = 1

#         else:
#             run_battery = 0

        
#         # if not is_winter:
#         #     if ((pv - load > 0) an


#         # if is_winter:
#         #     run_el = 0 
#         #     if self.fc_state == 0 and soc <= self.fc_emergency_soc and (load - pv) >= self.transformer_capacity and h2_soc >= self.h2_soc_min:
#         #         self.fc_state = 1
            
#         #     elif self.fc_state == 1 and ((load-pv) < self.transformer_capacity or h2_soc <= self.h2_soc_min):
#         #         self.fc_state = 0

#         #     if self.fc_state == 1 and h2_soc >= self.h2_soc_min and h2_soc <= self.h2_soc_max:
#         #         run_fc = 1
#         #         storage_flow = -1
#         #     else:
#         #         run_fc = 0
   

#         #     if self.fc_state == 1 and h2_soc >= self.h2_soc_min and h2_soc <= self.h2_soc_max:
#         #         run_el = 0
#         #         run_fc = 1
#         #         compressor_on = 0
#         #         storage_flow = -1
#         #     elif self.fc_state == 0:
#         #         run_fc = 0

#         self.set_outputs({
#             'run_battery': run_battery
#             # 'run_electrolyser': run_el,
#             # 'run_fuelcell': run_fc,
#             # 'compressor_on': compressor_on,
#             # 'storage_flow': storage_flow
#         })

#         self.set_states({
#             'el_state': self.el_state,
#             'fc_state': self.fc_state,
#             'el_daily_flag': self.el_daily_flag,
#             'production_rate': self.production_rate
#         })

#         return time + self.time_step_size