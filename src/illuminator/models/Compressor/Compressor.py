from illuminator.builder import ModelConstructor

class Compressor(ModelConstructor):
    parameters = {
        'p_in': 30,  # bar
        'p_out': 500,  # bar
        'T_amb': 293.15,  # K
        'compressor_eff': 62.22,  # %
        'nom_compression_energy': 8.5, # kWh/kg
        'max_hydrogen_flow': 0.3, #kg/h
    }
    inputs = {
        'compressor_on': 0,
        'flow2c': 0,  # hydrogen flow to the compressor [kg/timestep]
        'phase_step': 0 # phase step of electrolyser
    }
    outputs = {
        'eflow2c': 0,  # energy flow to the compressor [kW]
        'flow_from_c': 0  # hydrogen flow from compressor [kg/timestep]
    }
    states = {
        'volume_flow_out': 0,  # m3/hours
        'new_density_p': 0  # new density of hydrogen at p_out and T_amb
    }

    time_step_size = 1  
    time = None

    def __init__(self, **kwargs) -> None:

        super().__init__(**kwargs)
        self.volume_flow_out = self._model.states.get('volume_flow_out')
        self.new_density_p = self._model.states.get('new_density_p')
        self.p_in = self._model.parameters.get('p_in')  # bar
        self.p_out = self._model.parameters.get('p_out')  # bar 
        self.T_amb = self._model.parameters.get('T_amb')  # K
        self.compressor_eff = self._model.parameters.get('compressor_eff')  # %
        self.nom_compression_energy = self._model.parameters.get('nom_compression_energy')  # kWh/kg
        self.max_hydrogen_flow = self._model.parameters.get('max_hydrogen_flow')  # kg/h
        self.installed_power = self._model.parameters.get('installed_power')  # kW


    # hhv = 286.6  # Higher heating value of hydrogen (kJ/mol)
    mmh2 = 2.016  # g/mol
    R = 8.314  # J/mol*K
    # gamma = 1.41 #cp/cv constant pressure / constant volume for hydrogen
    # e_grav_h2 = 120e6  # J/kg

    def step(self, time: int, inputs: dict = None, max_advance: int=900) -> None:
        input_data = self.unpack_inputs(inputs)
        flow = input_data['flow2c']
        compressor_on = input_data['compressor_on']
        phase_step = input_data['phase_step']

        power_data = self.power_req(
            compressor_on=compressor_on,
            flow=flow,
            phase_step =phase_step,
            p_in=self.p_in,
            p_out=self.p_out,
            T_amb=self.T_amb
        )

        self.update_outputs_and_states(flow, power_data)
        return time + self.time_step_size

    def update_outputs_and_states(self, flow: float, power_data: dict) -> None:
        dt_h = self.time_resolution / 3600
        density = self.new_density(self.p_out, self.T_amb)
        volume_flow_out = (flow / density) / dt_h

        self.set_outputs({
            'flow_from_c': power_data['output_flow'],
            'eflow2c': round(power_data['power_req'], 3)
        })

        self.set_states({
            'new_density_p': round(density, 3),
            'volume_flow_out': round(volume_flow_out, 3)
        })

    def power_req(self, compressor_on: int, phase_step: int, flow: float, p_in: float, p_out: float, T_amb: float) -> dict:
        if compressor_on == 1 or phase_step == 2 or phase_step == 3 or phase_step == 4:  
            # pr = p_out / p_in
            # exponent = (self.gamma - 1) / self.gamma
            # w_isentropic = (self.gamma / (self.gamma - 1)) * self.R * T_amb * (pr ** exponent - 1)
            # P_isothermal = flow/self.time_resolution*1000/self.mmh2*self.R * T_amb * (p_out / p_in)  # J/mol
            power_in_kw = flow*(3600/self.time_resolution)*self.nom_compression_energy/(self.compressor_eff / 100)  # kW
            # w_real = w_isentropic / (self.compressor_eff / 100)
            # P_real = P_isothermal / (self.compressor_eff / 100)  
            # flow_mol_s = (flow * 1000 / self.mmh2) / self.time_resolution
            # power_in_kw = w_real * flow_mol_s/1000

            return {'power_req': power_in_kw, 'output_flow': flow}
        else:
            return {'power_req': 0, 'output_flow': 0}

    def new_density(self, p: float, T: float) -> float:
        z_val = self.find_z_val(p, T)
        return ((p * 1e5) * (self.mmh2 / 1e3)) / (z_val * self.R * T)

    def find_z_val(self, press: float, temp: float) -> float:
        z_values = [
            [1.00070, 1.00004, 1.0006, 1.00055, 1.00047, 1.00041, 1.00041],
            [1.00337, 1.00319, 1.00304, 1.00270, 1.00241, 1.00219, 1.00196],
            [1.00672, 1.00643, 1.00605, 1.00540, 1.00484, 1.00435, 1.00395],
            [1.03387, 1.03235, 1.03037, 1.02701, 1.02411, 1.02159, 1.01957],
            [1.06879, 1.06520, 1.06127, 1.05369, 1.04807, 1.04314, 1.03921],
            [1.10404, 1.09795, 1.09189, 1.08070, 1.07200, 1.06523, 1.05936],
            [1.14056, 1.13177, 1.12320, 1.10814, 1.09631, 1.08625, 1.07849],
            [1.17789, 1.16617, 1.15499, 1.13543, 1.12034, 1.10793, 1.08764],
            [1.21592, 1.20101, 1.18716, 1.16300, 1.14456, 1.12957, 1.11699],
            [1.25461, 1.23652, 1.21936, 1.19051, 1.16877, 1.15112, 1.13648],
            [1.29379, 1.27220, 1.25205, 1.21842, 1.19317, 1.17267, 1.15588],
            [1.33332, 1.30820, 1.28487, 1.24634, 1.19439, 1.17533, 1.21739],
            [137284, 1.34392, 1.31784, 1.27398, 1.24173, 1.21583, 1.19463],
            [1.45188, 1.41618, 1.38797, 1.33010, 1.29040, 1.2592, 1.23373],
            [1.33161, 1.48880, 1.44991, 1.38593, 1.33914, 1.30236, 1.27226]
        ]
        temps = [250, 273.15, 298.15, 350, 400, 450, 500]
        pressures = [1, 5, 10, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 600, 700]

        closest_temp = min(temps, key=lambda t: abs(t - temp))
        closest_pressure = min(pressures, key=lambda p: abs(p - press))
        return z_values[pressures.index(closest_pressure)][temps.index(closest_temp)]