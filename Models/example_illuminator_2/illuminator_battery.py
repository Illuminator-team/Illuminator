""" In the YAML file:
- name: ExampleSim
  program: python # program that will start the simulator
  path: 'Models/example_illuminator_2/example_battery_illuminator_adapter.py' # path to the simulator's code
  models: 
  - name: ExampleModel
    public: true
    Inputs: [demand_power_flow=0] # Positive values are charging, negative values are discharging
    Outputs: [effective_power_flow=0, soc=None]
    Parameters: [charge_power_max=100, discharge_power_max=200, soc_min=0.1, soc_max=0.9, capacity=1000]
    States: [initial_soc=0.5]
    trigger: [delta]
"""

""" What we need as a result:
inputs = {"requested_power_flow": 0}
outputs = {"effective_power_flow": 0, "soc": None}
parameters = {"charge_power_max": 100, "discharge_power_max": 200, "soc_min": 0.1, "soc_max": 0.9, "capacity": 1000}
states = {"initial_soc": 0.5}
"""


class IlluminatorBattery:
    def __init__(self, inputs, outputs, parameters, states):
        self.inputs = inputs
        self.outputs = outputs
        self.parameters = parameters
        self.states = states
        # Initialize the state of charge (SoC) based on initial state
        self.soc = states["initial_soc"] * parameters["capacity"]

    def step(self):
        # Get the requested power flow
        requested_power_flow = self.inputs["requested_power_flow"]

        # Determine maximum allowed charge and discharge power
        charge_power_max = self.parameters["charge_power_max"]
        discharge_power_max = self.parameters["discharge_power_max"]

        # Determine current SoC as a fraction of capacity
        current_soc_fraction = self.soc / self.parameters["capacity"]

        # Check if the requested power flow is for charging or discharging
        if requested_power_flow > 0:  # Charging
            # Limit power flow to maximum charge power and SOC max
            actual_power_flow = min(requested_power_flow, charge_power_max)
            if current_soc_fraction + (actual_power_flow / self.parameters["capacity"]) > self.parameters["soc_max"]:
                actual_power_flow = (self.parameters["soc_max"] - current_soc_fraction) * self.parameters["capacity"]
            self.soc += actual_power_flow  # Update SoC

        elif requested_power_flow < 0:  # Discharging
            # Limit power flow to maximum discharge power and SOC min
            actual_power_flow = max(requested_power_flow, -discharge_power_max)
            if current_soc_fraction + (actual_power_flow / self.parameters["capacity"]) < self.parameters["soc_min"]:
                actual_power_flow = (self.parameters["soc_min"] - current_soc_fraction) * self.parameters["capacity"]
            self.soc += actual_power_flow  # Update SoC

        else:  # No power flow
            actual_power_flow = 0

        # Update outputs
        self.outputs["effective_power_flow"] = actual_power_flow
        self.outputs["soc"] = self.soc / self.parameters["capacity"]
  
