import unittest
# from state_space_model import Model  # Assuming the state_space_model.py is in the same directory
try:
    from Models.example_illuminator_2.state_space_simulator import StateSpaceSimulator 
except ModuleNotFoundError:
    from state_space_simulator import StateSpaceSimulator  # Assuming the state_space_simulator.py is in the same directory

class TestStateSpaceSimulator(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment. Initialize the simulator and create model instances.
        """
        # Initialize the simulator with metadata
        self.simulator = StateSpaceSimulator()
        self.simulator.init('sim1', step_size=15)  # Step size is 15 minutes

        # Define the inputs, outputs, parameters, and states for the model instance
        self.inputs = {'requested_power_flow': 0.0}
        self.outputs = {'effective_power_flow': 0.0}
        self.parameters = {'capacity': 1000}  # Battery capacity is 1000 kWh
        self.states = {'soc': 0.5}  # Initial state of charge is 50%

        # Create a model instance using the simulator's `create` method
        self.simulator.create(num=1, inputs=self.inputs, outputs=self.outputs,
                              parameters=self.parameters, states=self.states)

    def test_initial_state(self):
        """
        Test the initial state of the model after creation.
        """
        # Access the model instance
        model_instance = list(self.simulator.entities.values())[0]

        # Check initial state of charge (soc)
        self.assertAlmostEqual(model_instance.states['soc'], 0.5)
        # Check initial capacity
        self.assertEqual(model_instance.parameters['capacity'], 1000)
        # Check initial requested power flow input
        self.assertEqual(model_instance.inputs['requested_power_flow'], 0.0)

    def test_step_charging(self):
        """
        Test the charging behavior of the model.
        """
        # Set the input to charge the battery
        self.simulator.entities['SSM_Battery_1'].inputs['requested_power_flow'] = 500  # 500 kW charging power

        # Perform a simulation step
        self.simulator.step(0, {'SSM_Battery_1': {'requested_power_flow': {0: 500}}})

        # Access the model instance
        model_instance = list(self.simulator.entities.values())[0]

        # Calculate the expected state of charge after the step
        # Charging 500 kW for 15 mins -> 125 kWh added (500 kW * 0.25 hour)
        expected_soc = 0.5 + 125 / 1000  # 1000 kWh capacity
        expected_effective_power_flow = 500

        # Check that the state of charge (soc) and effective power flow have been updated correctly
        self.assertAlmostEqual(model_instance.states['soc'], expected_soc)
        self.assertAlmostEqual(model_instance.outputs['effective_power_flow'], expected_effective_power_flow)

    def test_step_discharging(self):
        """
        Test the discharging behavior of the model.
        """
        # Set the input to discharge the battery
        self.simulator.entities['SSM_Battery_1'].inputs['requested_power_flow'] = -300  # 300 kW discharging power

        # Perform a simulation step
        self.simulator.step(0, {'SSM_Battery_1': {'requested_power_flow': {0: -300}}})

        # Access the model instance
        model_instance = list(self.simulator.entities.values())[0]

        # Calculate the expected state of charge after the step
        # Discharging 300 kW for 15 mins -> 75 kWh removed (300 kW * 0.25 hour)
        expected_soc = 0.5 - 75 / 1000  # 1000 kWh capacity
        expected_effective_power_flow = -300

        # Check that the state of charge (soc) and effective power flow have been updated correctly
        self.assertAlmostEqual(model_instance.states['soc'], expected_soc)
        self.assertAlmostEqual(model_instance.outputs['effective_power_flow'], expected_effective_power_flow)

    def test_overcharge_protection(self):
        """
        Test that the model does not overcharge beyond its capacity.
        """
        # Set the input to charge the battery beyond its capacity
        self.simulator.entities['SSM_Battery_1'].inputs['requested_power_flow'] = 5000  # 5000 kW charging power

        # Perform a simulation step
        self.simulator.step(0, {'SSM_Battery_1': {'requested_power_flow': {0: 5000}}})

        # Access the model instance
        model_instance = list(self.simulator.entities.values())[0]

        # The state of charge should not exceed 1.0 (100%)
        expected_soc = 1.0  # Maximum SOC is 100%
        expected_effective_power_flow = (1.0 - 0.5) * 1000 / 0.25  # Capacity left for charging in 15 minutes

        # Check that the state of charge (soc) and effective power flow have been updated correctly
        self.assertAlmostEqual(model_instance.states['soc'], expected_soc)
        self.assertAlmostEqual(model_instance.outputs['effective_power_flow'], expected_effective_power_flow)

    def test_overdischarge_protection(self):
        """
        Test that the model does not discharge below 0% state of charge.
        """
        # Set the input to discharge the battery beyond its available energy
        self.simulator.entities['SSM_Battery_1'].inputs['requested_power_flow'] = -7000  # 7000 kW discharging power

        # Perform a simulation step
        self.simulator.step(0, {'SSM_Battery_1': {'requested_power_flow': {0: -7000}}})

        # Access the model instance
        model_instance = list(self.simulator.entities.values())[0]

        # The state of charge should not go below 0
        expected_soc = 0.0  # Minimum SOC is 0%
        expected_effective_power_flow = -(1.0 - 0.5) * 1000 / 0.25  # Maximum possible discharge for 15 minutes

        # Check that the state of charge (soc) and effective power flow have been updated correctly
        self.assertAlmostEqual(model_instance.states['soc'], expected_soc)
        self.assertAlmostEqual(model_instance.outputs['effective_power_flow'], expected_effective_power_flow)

if __name__ == '__main__':
    unittest.main()