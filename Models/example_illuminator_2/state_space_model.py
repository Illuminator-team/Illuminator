class Model:
    def __init__(self, inputs, outputs, parameters, states, step_size):
        self.inputs = inputs
        self.outputs = outputs
        self.parameters = parameters
        self.states = states
        self.step_size = step_size # Step size in minutes

        self.time = 0

    def step(self):
        # Get current state of charge (soc), capacity, and requested power flow
        soc = self.states['soc'] # SOC is the percentage charge left in the battery
        capacity = self.parameters['capacity'] # Capacity is the total energy capacity of the battery in KWh
        energy_in_battery = soc * capacity # Energy in the battery in KWh
        requested_power_flow = self.inputs['requested_power_flow'] # Requested power flow in KW
        requested_energy_flow = requested_power_flow * self.step_size / 60 # Convert power to energy in KWh

        # Calculate the effective energy flow
        if requested_energy_flow >= 0:
            # Charging the battery
            effective_energy_flow = min(requested_energy_flow, capacity - energy_in_battery)
        else:
            # Discharging the battery
            effective_energy_flow = max(requested_energy_flow, -energy_in_battery)

        # Update the state of charge
        soc += effective_energy_flow / capacity

        effective_power_flow = effective_energy_flow * 60 / self.step_size # Convert energy back to power in KW

        # Update the outputs and state
        self.outputs['effective_power_flow'] = effective_power_flow
        self.states['soc'] = soc
