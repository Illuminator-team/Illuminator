import pytest
from illuminator.models.Load.load_v3 import Load

#                                     Load_V3 TEST
# ============================================================================
#   This file contains unit tests for v3 of the load model. The tests include:
#       1. Test values for validating model methods and outputs.
#       2. Object initialization with test value parameters.
#       3. Validation of initialization with and without given values.
#       4. Tests for each method of the model.
# ============================================================================

# Define test parameters for reuse
TEST_PARAMS = {
    'houses': 5,
    'output_type': 'power'
}

class TestLoadModelMethods:
    """
    Unit tester for the Load model
    """
    def test_constructor_missing_parameters(self):
        """
        Tests the parameter default values work properly.
        """
        load_model = Load()
        assert load_model._model.parameters['houses'] == 1
        assert load_model._model.parameters['output_type'] == 'power'

    def create_basic_Load_object(self):
        """
        Creates the Load object with pre-set data.
        This method avoids boilerplate code for creating the Load model object.
        """
        load_model = Load()
        load_model._model.parameters.update(TEST_PARAMS)
        return load_model

    def test_constructor_happy_flow(self):
        """
        The expected __init__ constructor outcome when creating the class object with all expected values.
        """
        load_model = self.create_basic_Load_object()

        # Test that attributes are correctly initialized
        assert load_model._model.parameters['houses'] == TEST_PARAMS['houses']
        assert load_model._model.parameters['output_type'] == TEST_PARAMS['output_type']

    # ============== Method Tests ==============

    def test_demand_energy(self):
        """
        Test demand calculation for 'energy' output type.
        """
        load_model = self.create_basic_Load_object()
        load_model.time_resolution = 3600
        load_model.time_step_size = 1

        input_load = 2 
        expected_demand = TEST_PARAMS['houses'] * input_load

        actual_demand = load_model.demand(input_load)['load_dem']
        assert actual_demand == expected_demand, (
            f"Expected demand: {expected_demand}, got: {actual_demand}"
        )

    def test_demand_power(self):
        """
        Test demand calculation for 'power' output type.
        """
        load_model = self.create_basic_Load_object()
        load_model._model.parameters['output_type'] = 'power'
        load_model.time_resolution = 3600  # 1-hour resolution
        load_model.time_step_size = 1

        input_load = 2 
        deltaTime = load_model.time_resolution * load_model.time_step_size / 60 / 60
        expected_demand = TEST_PARAMS['houses'] * input_load * deltaTime

        actual_demand = load_model.demand(input_load)['load_dem']
        assert actual_demand == expected_demand, (
            f"Expected demand: {expected_demand}, got: {actual_demand}"
        )

    def test_connect_happy_flow(self):
        """
        Test the connect method for setting inputs.
        """
        load_model = self.create_basic_Load_object()
        load_model.time_resolution = 3600  # 1-hour resolution
        
        inputs = {
            'load': {'load': {'source': {'value': 3, 'message_origin': 'output'}}}
        }
        load_model.step(0, inputs)

        expected_demand = TEST_PARAMS['houses'] * 3 * (3600 / 60 / 60)
        assert load_model.outputs['load_dem']['value'] == expected_demand

    def test_step_function(self):
        """
        Test the step function for correct state and output updates.
        """
        load_model = self.create_basic_Load_object()
        load_model.time_resolution = 3600  # 1-hour resolution

        inputs = {
            'load': {'load': {'source': {'value': 3, 'message_origin': 'output'}}}  # Load value in kW
        }
        current_time = 0

        next_time = load_model.step(current_time, inputs)

        # Check updated outputs
        expected_demand = TEST_PARAMS['houses'] * 3 * (3600 / 60 / 60)
        assert load_model.outputs['load_dem']['value'] == expected_demand, (
            f"Expected load_dem: {expected_demand}, got: {load_model.outputs['load_dem']['value']}"
        )

        # Check returned time
        assert next_time == 1, "Expected time advancement by one step."
