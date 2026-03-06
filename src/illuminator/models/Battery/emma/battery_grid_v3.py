from illuminator.builder import ModelConstructor
import numpy as np
 
 
class BatteryOnly(ModelConstructor):
    """
    Battery model with controller-driven charging and discharging.
    Modes:
    - mode=0 (hold): Do nothing, maintain SOC
    - mode=1 (grid_charge): Charge from grid + any PV surplus
    - mode=2 (discharge): Discharge at requested rate (winter threshold-based)
    - mode=3 (pv_charge): Charge from PV excess only
    - mode=4 (self_consumption): Discharge for self-consumption (summer)
    """
    parameters = {
        'c_rate': 0.33,                # C-rate (power/capacity ratio)
        'charge_efficiency': 97.47,    # Battery charge efficiency (%)
        'charge_inv_efficiency': 93,   # Inverter efficiency during charge (%)
        'discharge_efficiency': 97.47, # Battery discharge efficiency (%)
        'discharge_inv_efficiency': 96,# Inverter efficiency during discharge (%)
        'soc_min': 20.0,               # Minimum SOC (%)
        'soc_max': 90.0,               # Maximum SOC (%)
        'max_energy': 15.36            # Battery capacity (kWh)
    }
 
    inputs = {
        'pv_battery': 0,           # PV generation available to battery (kW)
        'load_battery': 0,         # Load to be served (kW)
        'flow2e': 0,               # Power to electrolyser (kW)
        'eflow2c_batt': 0,         # Power to compressor (kW)
        'p_out_fuelcell': 0,       # Fuel cell output (kW)
        'grid_charge_request': 0,  # Requested grid charging power (kW)
        'discharge_request': 0,    # Requested discharge power (kW)
        'mode': 0,                 # Controller mode
    }
 
    outputs = {
        'flow2b': 0,               # Battery power flow (+ = discharge, - = charge) (kW)
        'grid_charge_actual': 0,   # Actual grid charging power (kW)
    }
 
    states = {
        'soc': 50.0,
        'bat_state': 'off'
    }
 
    time_step_size = 1
    time = None
 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.soc = self._model.states.get('soc')
        self.bat_state = self._model.states.get('bat_state')
 
        self.charge_eff = self._model.parameters.get('charge_efficiency') / 100
        self.charge_inv_eff = self._model.parameters.get('charge_inv_efficiency') / 100
        self.discharge_eff = self._model.parameters.get('discharge_efficiency') / 100
        self.discharge_inv_eff = self._model.parameters.get('discharge_inv_efficiency') / 100
        self.c_rate = self._model.parameters.get('c_rate')
        self.soc_min = self._model.parameters.get('soc_min')
        self.soc_max = self._model.parameters.get('soc_max')
        self.max_energy = self._model.parameters.get('max_energy')
        # Calculate max power from C-rate and capacity
        self.max_p = self.c_rate * self.max_energy   # Max discharge power (kW)
        self.min_p = -self.c_rate * self.max_energy  # Max charge power (kW, negative)
 
    def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> None:
        input_data = self.unpack_inputs(inputs)
        results = self.output_power(
            pv=input_data.get('pv_battery', 0),
            load=input_data.get('load_battery', 0),
            flow2e=input_data.get('flow2e', 0),
            flow2c=input_data.get('eflow2c_batt', 0),
            fc=input_data.get('p_out_fuelcell', 0),
            grid_charge_request=input_data.get('grid_charge_request', 0),
            discharge_request=input_data.get('discharge_request', 0),
            mode=int(input_data.get('mode', 0))
        )
 
        self.soc = results.pop('soc')
        self.bat_state = results.pop('bat_state')
 
        self.set_states({'soc': self.soc, 'bat_state': self.bat_state})
        self.set_outputs(results)
 
        return time + self._model.time_step_size
 
    def output_power(self, pv: float, load: float, flow2e: float,
                     fc: float, flow2c: float, grid_charge_request: float,
                     discharge_request: float, mode: int) -> dict:
        """
        Calculate battery power flow based on controller mode.
        """
        soc = self.soc
        flow2b = 0
        grid_charge_actual = 0
        bat_state = 'hold'
 
        dt_h = self.time_resolution / 3600  # Time step in hours
 
        # Combined efficiencies
        charge_eff_total = self.charge_eff * self.charge_inv_eff
        discharge_eff_total = self.discharge_eff * self.discharge_inv_eff
 
        # Calculate net power balance
        net_generation = pv + fc
        net_consumption = load - flow2e - flow2c
        pv_excess = net_generation - net_consumption  # Positive = excess PV
 
        # ===== MODE 1: Grid charging (+ PV surplus if available) =====
        if mode == 1 and soc < self.soc_max:
            total_charge = 0
            # First: Add PV surplus if available
            pv_charge = 0
            if pv_excess > 0:
                pv_charge = min(pv_excess, -self.min_p)  # Limit by C-rate
            # Second: Add grid charging
            grid_charge = 0
            if grid_charge_request > 0:
                # Remaining C-rate capacity after PV
                remaining_capacity = -self.min_p - pv_charge
                grid_charge = min(grid_charge_request, remaining_capacity)
                grid_charge = max(0, grid_charge)
            # Total charge power
            total_charge = pv_charge + grid_charge
            # Limit by SOC headroom
            max_energy_in = (self.soc_max - soc) * self.max_energy / 100
            max_power_in = max_energy_in / dt_h / charge_eff_total
            total_charge = min(total_charge, max_power_in)
            # Recalculate actual values after SOC limit
            if total_charge > 0:
                # Prioritize PV over grid
                pv_charge_actual = min(pv_charge, total_charge)
                grid_charge_actual = min(grid_charge, total_charge - pv_charge_actual)
                energy_in = total_charge * dt_h * charge_eff_total
                soc_increment = (energy_in / self.max_energy) * 100
                soc = soc + soc_increment
                flow2b = -total_charge  # Negative = charging
                if grid_charge_actual > 0 and pv_charge_actual > 0:
                    bat_state = 'charging (grid+pv)'
                elif grid_charge_actual > 0:
                    bat_state = 'charging (grid)'
                else:
                    bat_state = 'charging (pv)'
 
        # ===== MODE 2: Controlled discharge (winter threshold-based) =====
        elif mode == 2 and discharge_request > 0 and soc > self.soc_min:
            max_energy_out = (soc - self.soc_min) * self.max_energy / 100
            max_power_out = max_energy_out / dt_h * discharge_eff_total
            max_power_out = min(max_power_out, self.max_p)
            # Discharge only the requested amount (excess above threshold)
            flow2b = min(discharge_request, max_power_out)
            flow2b = max(0, flow2b)
            if flow2b > 0:
                energy_out = flow2b * dt_h / discharge_eff_total
                soc_decrement = (energy_out / self.max_energy) * 100
                soc = soc - soc_decrement
                bat_state = 'discharging (threshold)'
 
        # ===== MODE 3: PV charging only =====
        elif mode == 3 and pv_excess > 0 and soc < self.soc_max:
            charge_power = min(pv_excess, -self.min_p)
            max_energy_in = (self.soc_max - soc) * self.max_energy / 100
            max_power_in = max_energy_in / dt_h / charge_eff_total
            charge_power = min(charge_power, max_power_in)
 
            if charge_power > 0:
                energy_in = charge_power * dt_h * charge_eff_total
                soc_increment = (energy_in / self.max_energy) * 100
                soc = soc + soc_increment
                flow2b = -charge_power
                bat_state = 'charging (pv)'
 
        # ===== MODE 4: Self-consumption discharge (summer) =====
        elif mode == 4 and discharge_request > 0 and soc > self.soc_min:
            max_energy_out = (soc - self.soc_min) * self.max_energy / 100
            max_power_out = max_energy_out / dt_h * discharge_eff_total
            max_power_out = min(max_power_out, self.max_p)
            flow2b = min(discharge_request, max_power_out)
            flow2b = max(0, flow2b)
            if flow2b > 0:
                energy_out = flow2b * dt_h / discharge_eff_total
                soc_decrement = (energy_out / self.max_energy) * 100
                soc = soc - soc_decrement
                bat_state = 'discharging (self-consumption)'
 
        # ===== MODE 0: Hold =====
        else:
            flow2b = 0
            bat_state = 'hold'
 
        return {
            'flow2b': round(flow2b, 3),
            'grid_charge_actual': round(grid_charge_actual, 3),
            'soc': round(soc, 3),
            'bat_state': bat_state
        }
# from illuminator.builder import ModelConstructor
# import numpy as np
 
 
# class BatteryOnly(ModelConstructor):
#     """
#     Battery model with controller-driven charging and discharging.
#     Modes:
#     - mode=0 (hold): Do nothing, maintain SOC
#     - mode=1 (grid_charge): Charge from grid at requested rate
#     - mode=2 (discharge): Discharge at requested rate (winter threshold-based)
#     - mode=3 (pv_charge): Charge from PV excess
#     - mode=4 (self_consumption): Discharge for self-consumption (summer)
#     """
#     parameters = {
#         'c_rate': 0.33,                # C-rate (power/capacity ratio)
#         'charge_efficiency': 97.47,    # Battery charge efficiency (%)
#         'charge_inv_efficiency': 93,   # Inverter efficiency during charge (%)
#         'discharge_efficiency': 97.47, # Battery discharge efficiency (%)
#         'discharge_inv_efficiency': 96,# Inverter efficiency during discharge (%)
#         'soc_min': 20.0,               # Minimum SOC (%)
#         'soc_max': 90.0,               # Maximum SOC (%)
#         'max_energy': 15.36            # Battery capacity (kWh)
#     }
 
#     inputs = {
#         'pv_battery': 0,           # PV generation available to battery (kW)
#         'load_battery': 0,         # Load to be served (kW)
#         'flow2e': 0,               # Power to electrolyser (kW)
#         'eflow2c_batt': 0,         # Power to compressor (kW)
#         'p_out_fuelcell': 0,       # Fuel cell output (kW)
#         'grid_charge_request': 0,  # Requested grid charging power (kW)
#         'discharge_request': 0,    # Requested discharge power (kW)
#         'mode': 0,                 # Controller mode
#     }
 
#     outputs = {
#         'flow2b': 0,               # Battery power flow (+ = discharge, - = charge) (kW)
#         'grid_charge_actual': 0,   # Actual grid charging power (kW)
#     }
 
#     states = {
#         'soc': 50.0,
#         'bat_state': 'off'
#     }
 
#     time_step_size = 1
#     time = None
 
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.soc = self._model.states.get('soc')
#         self.bat_state = self._model.states.get('bat_state')
 
#         self.charge_eff = self._model.parameters.get('charge_efficiency') / 100
#         self.charge_inv_eff = self._model.parameters.get('charge_inv_efficiency') / 100
#         self.discharge_eff = self._model.parameters.get('discharge_efficiency') / 100
#         self.discharge_inv_eff = self._model.parameters.get('discharge_inv_efficiency') / 100
#         self.c_rate = self._model.parameters.get('c_rate')
#         self.soc_min = self._model.parameters.get('soc_min')
#         self.soc_max = self._model.parameters.get('soc_max')
#         self.max_energy = self._model.parameters.get('max_energy')
#         # Calculate max power from C-rate and capacity
#         self.max_p = self.c_rate * self.max_energy   # Max discharge power (kW)
#         self.min_p = -self.c_rate * self.max_energy  # Max charge power (kW, negative)
 
#     def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> None:
#         input_data = self.unpack_inputs(inputs)
#         results = self.output_power(
#             pv=input_data.get('pv_battery', 0),
#             load=input_data.get('load_battery', 0),
#             flow2e=input_data.get('flow2e', 0),
#             flow2c=input_data.get('eflow2c_batt', 0),
#             fc=input_data.get('p_out_fuelcell', 0),
#             grid_charge_request=input_data.get('grid_charge_request', 0),
#             discharge_request=input_data.get('discharge_request', 0),
#             mode=int(input_data.get('mode', 0))
#         )
 
#         self.soc = results.pop('soc')
#         self.bat_state = results.pop('bat_state')
 
#         self.set_states({'soc': self.soc, 'bat_state': self.bat_state})
#         self.set_outputs(results)
 
#         return time + self._model.time_step_size
 
#     def output_power(self, pv: float, load: float, flow2e: float,
#                      fc: float, flow2c: float, grid_charge_request: float,
#                      discharge_request: float, mode: int) -> dict:
#         """
#         Calculate battery power flow based on controller mode.
#         """
#         soc = self.soc
#         flow2b = 0
#         grid_charge_actual = 0
#         bat_state = 'hold'
 
#         dt_h = self.time_resolution / 3600  # Time step in hours
 
#         # Combined efficiencies
#         charge_eff_total = self.charge_eff * self.charge_inv_eff
#         discharge_eff_total = self.discharge_eff * self.discharge_inv_eff
 
#         # Calculate net power balance
#         net_generation = pv + fc
#         net_consumption = load - flow2e - flow2c
#         pv_excess = net_generation - net_consumption  # Positive = excess PV
 
#         # ===== MODE 1: Grid charging =====
#         if mode == 1 and grid_charge_request > 0 and soc < self.soc_max:
#             max_energy_in = (self.soc_max - soc) * self.max_energy / 100
#             max_power_in = max_energy_in / dt_h / charge_eff_total
#             max_power_in = min(max_power_in, -self.min_p)
#             grid_charge_actual = min(grid_charge_request, max_power_in)
#             grid_charge_actual = max(0, grid_charge_actual)
#             if grid_charge_actual > 0:
#                 energy_in = grid_charge_actual * dt_h * charge_eff_total
#                 soc_increment = (energy_in / self.max_energy) * 100
#                 soc = soc + soc_increment
#                 flow2b = -grid_charge_actual
#                 bat_state = 'charging (grid)'
 
#         # ===== MODE 2: Controlled discharge (winter threshold-based) =====
#         elif mode == 2 and discharge_request > 0 and soc > self.soc_min:
#             max_energy_out = (soc - self.soc_min) * self.max_energy / 100
#             max_power_out = max_energy_out / dt_h * discharge_eff_total
#             max_power_out = min(max_power_out, self.max_p)
#             # Discharge only the requested amount (excess above threshold)
#             flow2b = min(discharge_request, max_power_out)
#             flow2b = max(0, flow2b)
#             if flow2b > 0:
#                 energy_out = flow2b * dt_h / discharge_eff_total
#                 soc_decrement = (energy_out / self.max_energy) * 100
#                 soc = soc - soc_decrement
#                 bat_state = 'discharging (threshold)'
 
#         # ===== MODE 3: PV charging =====
#         elif mode == 3 and pv_excess > 0 and soc < self.soc_max:
#             charge_power = min(pv_excess, -self.min_p)
#             max_energy_in = (self.soc_max - soc) * self.max_energy / 100
#             max_power_in = max_energy_in / dt_h / charge_eff_total
#             charge_power = min(charge_power, max_power_in)
 
#             if charge_power > 0:
#                 energy_in = charge_power * dt_h * charge_eff_total
#                 soc_increment = (energy_in / self.max_energy) * 100
#                 soc = soc + soc_increment
#                 flow2b = -charge_power
#                 bat_state = 'charging (pv)'
 
#         # ===== MODE 4: Self-consumption discharge (summer) =====
#         elif mode == 4 and discharge_request > 0 and soc > self.soc_min:
#             max_energy_out = (soc - self.soc_min) * self.max_energy / 100
#             max_power_out = max_energy_out / dt_h * discharge_eff_total
#             max_power_out = min(max_power_out, self.max_p)
#             # Discharge to cover load deficit (full self-consumption)
#             flow2b = min(discharge_request, max_power_out)
#             flow2b = max(0, flow2b)
#             if flow2b > 0:
#                 energy_out = flow2b * dt_h / discharge_eff_total
#                 soc_decrement = (energy_out / self.max_energy) * 100
#                 soc = soc - soc_decrement
#                 bat_state = 'discharging (self-consumption)'
 
#         # ===== MODE 0: Hold =====
#         else:
#             flow2b = 0
#             bat_state = 'hold'
 
#         return {
#             'flow2b': round(flow2b, 3),
#             'grid_charge_actual': round(grid_charge_actual, 3),
#             'soc': round(soc, 3),
#             'bat_state': bat_state
#         }
# from illuminator.builder import ModelConstructor
# import numpy as np
 
 
# class BatteryOnly(ModelConstructor):
#     """
#     Battery model with controller-driven charging and discharging.
#     IMPORTANT: This battery ONLY acts when commanded by the controller.
#     - No automatic self-consumption discharge
#     - Must receive mode signal from controller
#     Modes:
#     - mode=0 (hold): Do nothing, maintain SOC
#     - mode=1 (grid_charge): Charge from grid at requested rate
#     - mode=2 (discharge): Discharge at requested rate for peak shaving
#     - mode=3 (pv_charge): Allow PV excess to charge battery
#     """
#     parameters = {
#         'c_rate': 0.33,                # C-rate (power/capacity ratio)
#         'charge_efficiency': 97.47,    # Battery charge efficiency (%)
#         'charge_inv_efficiency': 93,   # Inverter efficiency during charge (%)
#         'discharge_efficiency': 97.47, # Battery discharge efficiency (%)
#         'discharge_inv_efficiency': 96,# Inverter efficiency during discharge (%)
#         'soc_min': 20.0,               # Minimum SOC (%)
#         'soc_max': 90.0,               # Maximum SOC (%)
#         'max_energy': 15.36            # Battery capacity (kWh)
#     }
 
#     inputs = {
#         'pv_battery': 0,           # PV generation available to battery (kW)
#         'load_battery': 0,         # Load to be served (kW)
#         'flow2e': 0,               # Power to electrolyser (kW)
#         'eflow2c_batt': 0,         # Power to compressor (kW)
#         'p_out_fuelcell': 0,       # Fuel cell output (kW)
#         'grid_charge_request': 0,  # Requested grid charging power (kW)
#         'discharge_request': 0,    # Requested discharge power (kW)
#         'mode': 0,                 # Controller mode: 0=hold, 1=charge, 2=discharge, 3=pv_charge
#     }
 
#     outputs = {
#         'flow2b': 0,               # Battery power flow (+ = discharge, - = charge) (kW)
#         'grid_charge_actual': 0,   # Actual grid charging power (kW)
#     }
 
#     states = {
#         'soc': 50.0,
#         'bat_state': 'off'
#     }
 
#     time_step_size = 1
#     time = None
 
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.soc = self._model.states.get('soc')
#         self.bat_state = self._model.states.get('bat_state')
 
#         self.charge_eff = self._model.parameters.get('charge_efficiency') / 100
#         self.charge_inv_eff = self._model.parameters.get('charge_inv_efficiency') / 100
#         self.discharge_eff = self._model.parameters.get('discharge_efficiency') / 100
#         self.discharge_inv_eff = self._model.parameters.get('discharge_inv_efficiency') / 100
#         self.c_rate = self._model.parameters.get('c_rate')
#         self.soc_min = self._model.parameters.get('soc_min')
#         self.soc_max = self._model.parameters.get('soc_max')
#         self.max_energy = self._model.parameters.get('max_energy')
#         # Calculate max power from C-rate and capacity
#         self.max_p = self.c_rate * self.max_energy   # Max discharge power (kW)
#         self.min_p = -self.c_rate * self.max_energy  # Max charge power (kW, negative)
 
#     def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> None:
#         input_data = self.unpack_inputs(inputs)
#         results = self.output_power(
#             pv=input_data.get('pv_battery', 0),
#             load=input_data.get('load_battery', 0),
#             flow2e=input_data.get('flow2e', 0),
#             flow2c=input_data.get('eflow2c_batt', 0),
#             fc=input_data.get('p_out_fuelcell', 0),
#             grid_charge_request=input_data.get('grid_charge_request', 0),
#             discharge_request=input_data.get('discharge_request', 0),
#             mode=int(input_data.get('mode', 0))  # Default to hold (0)
#         )
 
#         self.soc = results.pop('soc')
#         self.bat_state = results.pop('bat_state')
 
#         self.set_states({'soc': self.soc, 'bat_state': self.bat_state})
#         self.set_outputs(results)
 
#         return time + self._model.time_step_size
 
#     def output_power(self, pv: float, load: float, flow2e: float,
#                      fc: float, flow2c: float, grid_charge_request: float,
#                      discharge_request: float, mode: int) -> dict:
#         """
#         Calculate battery power flow based on controller mode.
#         Modes:
#         - 0 (hold): No action
#         - 1 (grid_charge): Charge from grid
#         - 2 (discharge): Discharge for peak shaving
#         - 3 (pv_charge): Charge from PV excess
#         """
#         soc = self.soc
#         flow2b = 0
#         grid_charge_actual = 0
#         bat_state = 'hold'
 
#         dt_h = self.time_resolution / 3600  # Time step in hours
 
#         # Combined efficiencies
#         charge_eff_total = self.charge_eff * self.charge_inv_eff
#         discharge_eff_total = self.discharge_eff * self.discharge_inv_eff
 
#         # Calculate net power balance (for PV charging mode)
#         net_generation = pv + fc
#         net_consumption = load - flow2e - flow2c
#         pv_excess = net_generation - net_consumption  # Positive = excess PV
 
#         # ===== MODE 1: Grid charging =====
#         if mode == 1 and grid_charge_request > 0 and soc < self.soc_max:
#             # Calculate how much the battery can accept
#             max_energy_in = (self.soc_max - soc) * self.max_energy / 100
#             max_power_in = max_energy_in / dt_h / charge_eff_total
#             max_power_in = min(max_power_in, -self.min_p)  # Limit by C-rate
#             # Actual grid charging
#             grid_charge_actual = min(grid_charge_request, max_power_in)
#             grid_charge_actual = max(0, grid_charge_actual)
#             if grid_charge_actual > 0:
#                 energy_in = grid_charge_actual * dt_h * charge_eff_total
#                 soc_increment = (energy_in / self.max_energy) * 100
#                 soc = soc + soc_increment
#                 flow2b = -grid_charge_actual  # Negative = charging
#                 bat_state = 'charging (grid)'
 
#         # ===== MODE 2: Controlled discharge (peak shaving) =====
#         elif mode == 2 and discharge_request > 0 and soc > self.soc_min:
#             # Calculate how much can be discharged
#             max_energy_out = (soc - self.soc_min) * self.max_energy / 100
#             max_power_out = max_energy_out / dt_h * discharge_eff_total
#             max_power_out = min(max_power_out, self.max_p)  # Limit by C-rate
#             # Actual discharge - only what's requested!
#             flow2b = min(discharge_request, max_power_out)
#             flow2b = max(0, flow2b)
#             if flow2b > 0:
#                 energy_out = flow2b * dt_h / discharge_eff_total
#                 soc_decrement = (energy_out / self.max_energy) * 100
#                 soc = soc - soc_decrement
#                 bat_state = 'discharging'
 
#         # ===== MODE 3: PV charging (when PV excess exists) =====
#         elif mode == 3 and pv_excess > 0 and soc < self.soc_max:
#             # Charge from PV excess
#             charge_power = min(pv_excess, -self.min_p)  # Limit to max charge rate
 
#             # Limit by SOC headroom
#             max_energy_in = (self.soc_max - soc) * self.max_energy / 100
#             max_power_in = max_energy_in / dt_h / charge_eff_total
#             charge_power = min(charge_power, max_power_in)
 
#             if charge_power > 0:
#                 # Calculate SOC increment
#                 energy_in = charge_power * dt_h * charge_eff_total
#                 soc_increment = (energy_in / self.max_energy) * 100
#                 soc = soc + soc_increment
#                 flow2b = -charge_power  # Negative = charging
#                 bat_state = 'charging (pv)'
 
#         # ===== MODE 0: Hold (default - do nothing) =====
#         else:
#             flow2b = 0
#             bat_state = 'hold'
 
#         return {
#             'flow2b': round(flow2b, 3),
#             'grid_charge_actual': round(grid_charge_actual, 3),
#             'soc': round(soc, 3),
#             'bat_state': bat_state
#         }

# from illuminator.builder import ModelConstructor
# import numpy as np
 
 
# class BatteryOnly(ModelConstructor):
#     """
#     Battery model with grid charging capability.
#     Handles:
#     - Self-consumption (PV excess charging, load deficit discharging)
#     - Grid charging during off-peak hours (via grid_charge_request input)
#     - SOC limits and efficiency losses
#     Priority:
#     1. If grid_charge_request > 0: charge from grid (skip self-consumption discharge)
#     2. Else: normal self-consumption (PV excess → battery, battery → load deficit)
#     """
#     parameters = {
#         'c_rate': 0.33,                # C-rate (power/capacity ratio)
#         'charge_efficiency': 97.47,    # Battery charge efficiency (%)
#         'charge_inv_efficiency': 93,   # Inverter efficiency during charge (%)
#         'discharge_efficiency': 97.47, # Battery discharge efficiency (%)
#         'discharge_inv_efficiency': 96,# Inverter efficiency during discharge (%)
#         'soc_min': 20.0,               # Minimum SOC (%)
#         'soc_max': 90.0,               # Maximum SOC (%)
#         'max_energy': 15.36            # Battery capacity (kWh)
#     }
 
#     inputs = {
#         'pv_battery': 0,           # PV generation available to battery (kW)
#         'load_battery': 0,         # Load to be served (kW)
#         'flow2e': 0,               # Power to electrolyser (kW)
#         'eflow2c_batt': 0,         # Power to compressor (kW)
#         'p_out_fuelcell': 0,       # Fuel cell output (kW)
#         'grid_charge_request': 0,  # Requested grid charging power (kW)
#     }
 
#     outputs = {
#         'flow2b': 0,               # Battery power flow (+ = discharge, - = charge) (kW)
#         'grid_charge_actual': 0,   # Actual grid charging power (kW)
#     }
 
#     states = {
#         'soc': 50.0,
#         'bat_state': 'off'
#     }
 
#     time_step_size = 1
#     time = None
 
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.soc = self._model.states.get('soc')
#         self.bat_state = self._model.states.get('bat_state')
 
#         self.charge_eff = self._model.parameters.get('charge_efficiency') / 100
#         self.charge_inv_eff = self._model.parameters.get('charge_inv_efficiency') / 100
#         self.discharge_eff = self._model.parameters.get('discharge_efficiency') / 100
#         self.discharge_inv_eff = self._model.parameters.get('discharge_inv_efficiency') / 100
#         self.c_rate = self._model.parameters.get('c_rate')
#         self.soc_min = self._model.parameters.get('soc_min')
#         self.soc_max = self._model.parameters.get('soc_max')
#         self.max_energy = self._model.parameters.get('max_energy')
#         # Calculate max power from C-rate and capacity
#         self.max_p = self.c_rate * self.max_energy   # Max discharge power (kW)
#         self.min_p = -self.c_rate * self.max_energy  # Max charge power (kW, negative)
 
#     def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> None:
#         input_data = self.unpack_inputs(inputs)
#         results = self.output_power(
#             pv=input_data.get('pv_battery', 0),
#             load=input_data.get('load_battery', 0),
#             flow2e=input_data.get('flow2e', 0),
#             flow2c=input_data.get('eflow2c_batt', 0),
#             fc=input_data.get('p_out_fuelcell', 0),
#             grid_charge_request=input_data.get('grid_charge_request', 0)
#         )
 
#         self.soc = results.pop('soc')
#         self.bat_state = results.pop('bat_state')
 
#         self.set_states({'soc': self.soc, 'bat_state': self.bat_state})
#         self.set_outputs(results)
 
#         return time + self._model.time_step_size
 
#     def output_power(self, pv: float, load: float, flow2e: float,
#                      fc: float, flow2c: float, grid_charge_request: float) -> dict:
#         """
#         Calculate battery power flow and SOC update.
#         Priority:
#         1. If grid_charge_request > 0 and SOC < max: charge from grid
#         2. Else if PV excess: charge from PV
#         3. Else if load deficit: discharge to load
#         """
#         soc = self.soc
#         flow2b = 0
#         grid_charge_actual = 0
#         bat_state = 'off'
 
#         dt_h = self.time_resolution / 3600  # Time step in hours
 
#         # Combined efficiencies
#         charge_eff_total = self.charge_eff * self.charge_inv_eff
#         discharge_eff_total = self.discharge_eff * self.discharge_inv_eff
 
#         # Calculate net power balance
#         net_generation = pv + fc  # Total generation
#         net_consumption = load - flow2e - flow2c  # Total consumption
#         battery_power = net_consumption - net_generation  # + = needs discharge, - = can charge
 
#         # ===== PRIORITY 1: Grid charging (if requested) =====
#         if grid_charge_request > 0 and soc < self.soc_max:
#             # Calculate how much the battery can accept
#             max_energy_in = (self.soc_max - soc) * self.max_energy / 100
#             max_power_in = max_energy_in / dt_h / charge_eff_total
#             # Limit by C-rate
#             max_power_in = min(max_power_in, -self.min_p)
#             # Actual grid charging
#             grid_charge_actual = min(grid_charge_request, max_power_in)
#             grid_charge_actual = max(0, grid_charge_actual)
#             if grid_charge_actual > 0:
#                 # Update SOC
#                 energy_in = grid_charge_actual * dt_h * charge_eff_total
#                 soc_increment = (energy_in / self.max_energy) * 100
#                 soc = soc + soc_increment
#                 # flow2b is negative for charging
#                 flow2b = -grid_charge_actual
#                 bat_state = 'charging (grid)'
 
#         # ===== PRIORITY 2: Self-consumption - PV excess charging =====
#         elif battery_power < 0 and soc < self.soc_max:
#             # PV excess available, charge battery
#             flow2b = max(battery_power, self.min_p)  # Limit to max charge rate
 
#             # Calculate maximum allowable charge to respect SOC_max
#             max_energy_in = (self.soc_max - soc) * self.max_energy / 100
#             max_power_in = -max_energy_in / dt_h / charge_eff_total
#             flow2b = max(flow2b, max_power_in)
 
#             # Calculate SOC increment
#             energy_in = -flow2b * dt_h * charge_eff_total
#             soc_increment = (energy_in / self.max_energy) * 100
#             soc = soc + soc_increment
#             bat_state = 'charging (pv)'
 
#         # ===== PRIORITY 3: Self-consumption - Discharge to load =====
#         elif battery_power > 0 and soc > self.soc_min:
#             # Load deficit, discharge battery
#             flow2b = min(battery_power, self.max_p)  # Limit to max discharge rate
 
#             # Calculate maximum allowable discharge to respect SOC_min
#             max_energy_out = (soc - self.soc_min) * self.max_energy / 100
#             max_power_out = max_energy_out / dt_h * discharge_eff_total
#             flow2b = min(flow2b, max_power_out)
 
#             # Calculate SOC decrement
#             energy_out = flow2b * dt_h / discharge_eff_total
#             soc_decrement = (energy_out / self.max_energy) * 100
#             soc = soc - soc_decrement
#             bat_state = 'discharging'
 
#         # ===== PRIORITY 4: No action =====
#         else:
#             flow2b = 0
#             bat_state = 'off'
 
#         return {
#             'flow2b': round(flow2b, 3),
#             'grid_charge_actual': round(grid_charge_actual, 3),
#             'soc': round(soc, 3),
#             'bat_state': bat_state
#         }

# from illuminator.builder import ModelConstructor
# import numpy as np
 
 
# class BatteryOnly(ModelConstructor):
#     """
#     Battery model with grid charging capability.
#     Handles:
#     - Self-consumption (PV excess charging, load deficit discharging)
#     - Grid charging during off-peak hours (via grid_charge_request input)
#     - SOC limits and efficiency losses
#     """
#     parameters = {
#         'c_rate': 0.33,                # C-rate (power/capacity ratio)
#         'charge_efficiency': 97.47,    # Battery charge efficiency (%)
#         'charge_inv_efficiency': 93,   # Inverter efficiency during charge (%)
#         'discharge_efficiency': 97.47, # Battery discharge efficiency (%)
#         'discharge_inv_efficiency': 96,# Inverter efficiency during discharge (%)
#         'soc_min': 20.0,               # Minimum SOC (%)
#         'soc_max': 90.0,               # Maximum SOC (%)
#         'max_energy': 15.36            # Battery capacity (kWh)
#     }
 
#     inputs = {
#         'pv_battery': 0,           # PV generation available to battery (kW)
#         'load_battery': 0,         # Load to be served (kW)
#         'flow2e': 0,               # Power to electrolyser (kW)
#         'eflow2c_batt': 0,         # Power to compressor (kW)
#         'p_out_fuelcell': 0,       # Fuel cell output (kW)
#         'grid_charge_request': 0,  # Requested grid charging power (kW)
#     }
 
#     outputs = {
#         'flow2b': 0,               # Battery power flow (+ = discharge, - = charge) (kW)
#         'grid_charge_actual': 0,   # Actual grid charging power (kW)
#     }
 
#     states = {
#         'soc': 50.0,
#         'bat_state': 'off'
#     }
 
#     time_step_size = 1
#     time = None
 
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.soc = self._model.states.get('soc')
#         self.bat_state = self._model.states.get('bat_state')
 
#         self.charge_eff = self._model.parameters.get('charge_efficiency') / 100
#         self.charge_inv_eff = self._model.parameters.get('charge_inv_efficiency') / 100
#         self.discharge_eff = self._model.parameters.get('discharge_efficiency') / 100
#         self.discharge_inv_eff = self._model.parameters.get('discharge_inv_efficiency') / 100
#         self.c_rate = self._model.parameters.get('c_rate')
#         self.soc_min = self._model.parameters.get('soc_min')
#         self.soc_max = self._model.parameters.get('soc_max')
#         self.max_energy = self._model.parameters.get('max_energy')
#         # Calculate max power from C-rate and capacity
#         self.max_p = self.c_rate * self.max_energy   # Max discharge power (kW)
#         self.min_p = -self.c_rate * self.max_energy  # Max charge power (kW, negative)
 
#     def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> None:
#         input_data = self.unpack_inputs(inputs)
#         results = self.output_power(
#             pv=input_data['pv_battery'],
#             load=input_data['load_battery'],
#             flow2e=input_data.get('flow2e', 0),
#             flow2c=input_data.get('eflow2c_batt', 0),
#             fc=input_data.get('p_out_fuelcell', 0),
#             grid_charge_request=input_data['grid_charge_request']
#         )
 
#         self.soc = results.pop('soc')
#         self.bat_state = results.pop('bat_state')
 
#         self.set_states({'soc': self.soc, 'bat_state': self.bat_state})
#         self.set_outputs(results)
 
#         return time + self._model.time_step_size
 
#     def output_power(self, pv: float, load: float, flow2e: float, 
#                      fc: float, flow2c: float, grid_charge_request: float) -> dict:
#         """
#         Calculate battery power flow and SOC update.
#         Priority:
#         1. Self-consumption (PV excess → battery, battery → load deficit)
#         2. Grid charging (if requested and battery can accept)
#         """
#         soc = self.soc
#         flow2b = 0
#         grid_charge_actual = 0
#         bat_state = 'off'
 
#         dt_h = self.time_resolution / 3600  # Time step in hours
 
#         # Calculate net power balance (without grid charging)
#         net_generation = pv + fc  # Total generation
#         net_consumption = load - flow2e - flow2c  # Total consumption
#         battery_power = net_consumption - net_generation  # + = discharge, - = charge
 
#         # Combined charging efficiency
#         charge_eff_total = self.charge_eff * self.charge_inv_eff
#         discharge_eff_total = self.discharge_eff * self.discharge_inv_eff
 
#         # ===== CASE 1: Self-consumption requires discharge =====
#         if battery_power > 0 and soc > self.soc_min:
#             # Limit to max discharge power
#             flow2b = min(battery_power, self.max_p)
 
#             # Calculate maximum allowable discharge to respect SOC_min
#             max_energy_out = (soc - self.soc_min) * self.max_energy / 100
#             max_power_out = max_energy_out / dt_h * discharge_eff_total
#             flow2b = min(flow2b, max_power_out)
 
#             # Calculate SOC decrement
#             energy_out = flow2b * dt_h / discharge_eff_total
#             soc_decrement = (energy_out / self.max_energy) * 100
#             soc = soc - soc_decrement
#             bat_state = 'discharging'
 
#         # ===== CASE 2: Self-consumption can charge (PV excess) =====
#         elif battery_power < 0 and soc < self.soc_max:
#             # Limit to max charge power (min_p is negative)
#             flow2b = max(battery_power, self.min_p)
 
#             # Calculate maximum allowable charge to respect SOC_max
#             max_energy_in = (self.soc_max - soc) * self.max_energy / 100
#             max_power_in = -max_energy_in / dt_h / charge_eff_total
#             flow2b = max(flow2b, max_power_in)
 
#             # Calculate SOC increment
#             energy_in = -flow2b * dt_h * charge_eff_total
#             soc_increment = (energy_in / self.max_energy) * 100
#             soc = soc + soc_increment
#             bat_state = 'charging'
 
#         # ===== CASE 3: No self-consumption need, check grid charging =====
#         else:
#             flow2b = 0
 
#         # ===== Grid charging (additional to self-consumption charging) =====
#         if grid_charge_request > 0 and soc < self.soc_max:
#             # Calculate remaining charging capacity
#             remaining_charge_capacity = -self.min_p - abs(min(flow2b, 0))
#             if remaining_charge_capacity > 0:
#                 # Calculate how much energy the battery can still accept
#                 max_energy_in = (self.soc_max - soc) * self.max_energy / 100
#                 max_power_in = max_energy_in / dt_h / charge_eff_total
#                 # Actual grid charging (limited by request, capacity, and SOC headroom)
#                 grid_charge_actual = min(grid_charge_request, remaining_charge_capacity, max_power_in)
#                 grid_charge_actual = max(0, grid_charge_actual)
#                 if grid_charge_actual > 0:
#                     # Update SOC for grid charging
#                     energy_in = grid_charge_actual * dt_h * charge_eff_total
#                     soc_increment = (energy_in / self.max_energy) * 100
#                     soc = soc + soc_increment
#                     # Add grid charging to flow2b (negative = charging)
#                     flow2b = flow2b - grid_charge_actual
#                     bat_state = 'charging (grid)'
 
#         return {
#             'flow2b': round(flow2b, 3),
#             'grid_charge_actual': round(grid_charge_actual, 3),
#             'soc': round(soc, 3),
#             'bat_state': bat_state
#         }