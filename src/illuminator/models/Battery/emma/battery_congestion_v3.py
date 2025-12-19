from illuminator.builder import ModelConstructor
import numpy as np
class BatteryCongestion(ModelConstructor):
    parameters = {
        'c_rate': 0.33,              # C-rate
        'charge_efficiency': 97.47,    # %
        'charge_inv_efficiency': 93, # %
        'discharge_efficiency': 97.47, # %
        'discharge_inv_efficiency': 96, # %
        'soc_min': 20.0,            # %
        'soc_max': 90.0,             # %
        'max_energy': 15.36        # kWh
    }

    inputs = {
        'pv_battery': 0,          # kW
        'load_battery': 0,        # kW
        'flow2e': 0,
        'eflow2c_batt' : 0, # kW
        'p_out_fuelcell': 0                      # kW
    }

    outputs = {
        'flow2b': 0           # kW
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
        
        self.max_p = self.c_rate * self.max_energy  # kW
        self.min_p = -self.c_rate * self.max_energy # kW

    def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> None:
        input_data = self.unpack_inputs(inputs)
        results = self.output_power(
            pv=input_data['pv_battery'],
            load=input_data['load_battery'],
            flow2e=input_data['flow2e'],
            flow2c=input_data['eflow2c_batt'],
            fc=input_data['p_out_fuelcell']
        )

        self.soc = results.pop('soc')
        self.bat_state = results.pop('bat_state')

        self.set_states({'soc': self.soc, 'bat_state': self.bat_state})
        self.set_outputs(results)

        return time + self._model.time_step_size

    def output_power(self, pv: float, load: float, flow2e: float, fc: float, flow2c: float) -> dict:
        #Initialize states and output
        soc = self.soc
        flow2b = 0
        bat_state = 'off'


        dt_h= self.time_resolution / 3600

        net_generation = pv + fc  # Total generation
        # net_consumption = load - flow2e - flow2c  # Total consumption (flow2e is negative when consuming) #0.235W voor BoP erbij gezet
        net_consumption = load - flow2c  # Total consumption (flow2e is negative when consuming) #0.235W voor BoP erbij gezet
        battery_power = net_consumption - net_generation  # Positive = discharge, Negative = charge

        if battery_power > 0 and soc >= self.soc_min:
            #Power limit validation
            flow2b = min(battery_power, self.max_p)

            #Calculate maximum allowable discharge to respect SOC_min
            max_energy_out = (soc - self.soc_min) * self.max_energy / 100
            max_power_out = max_energy_out / dt_h * (self.discharge_eff * self.discharge_inv_eff)
            flow2b = min(flow2b, max_power_out)

            #Calculate energy output and SOC decrement
            energy_out = flow2b * dt_h / self.discharge_eff / self.discharge_inv_eff
            soc_decrement = (energy_out / self.max_energy) * 100 
            soc = soc - soc_decrement
            bat_state = 'discharging'

        elif battery_power < 0 and soc <= self.soc_max:
            #Power limit validation
            flow2b = max(battery_power, self.min_p)

            #Calculate maximum allowable Charge to respect SOC_min
            max_energy_in = (self.soc_max - soc) * self.max_energy / 100
            max_power_in = -max_energy_in / dt_h / (self.charge_eff * self.charge_inv_eff)
            flow2b = max(flow2b, max_power_in)

            #Calculate energy input and SOC increment
            energy_in = -1*flow2b * dt_h * self.charge_eff * self.charge_inv_eff
            soc_increment = (energy_in / self.max_energy) * 100
            soc = soc + soc_increment
            bat_state = 'charging'

        else:
            flow2b = 0
            bat_state = 'off'
            soc = soc

        re_params= {
            'flow2b': round(flow2b, 3),
            'soc': round(soc,3), 
            'bat_state': bat_state
        }

        return re_params