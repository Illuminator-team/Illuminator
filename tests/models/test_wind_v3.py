import pytest
import numpy as np
from illuminator.models.Wind.wind_v3 import Wind

#                                     Wind_V3 TEST
# ============================================================================
#   This file contains unit tests for v3 of the pv model. The tests include:
#       1. Test values for validating model methods and outputs.
#       2. Object initialization with test value parameters.
#       3. Validation of initialization with and without given values.
#       4. Tests for each method of the model.
# ============================================================================

# Define test parameters for reuse
TEST_PARAMS = {
    'p_rated': 500,
    'u_rated': 100,
    'u_cutin': 1,
    'u_cutout': 1000,
    'cp': 0.40,
    'diameter': 30,
    'output_type': 'power'
}

class TestWindModelMethods:
    """
    Unit tester for the Wind model
    """
    def test_constructor_missing_parameters(self):
        """
        Tests the parameter default values work properly.
        """
        wind = Wind()
        assert wind.p_rated == 500
        assert wind.u_rated == 100
        assert wind.u_cutin == 1
        assert wind.u_cutout == 1000
        assert wind.cp == 0.40
        assert wind.diameter == 30
        assert wind.output_type == 'power'

    def create_basic_Wind_object(self):
        """
        Creates the Wind object with pre-set data.
        This method avoids boilerplate code for creating the Wind model object.
        """
        wind = Wind()
        wind._model.parameters.update(TEST_PARAMS)
        for key, value in TEST_PARAMS.items():
            setattr(wind, key, value)
        return wind

    def test_constructor_happy_flow(self):
        """
        The expected __init__ constructor outcome when creating the class object with all expected values.
        """
        wind = self.create_basic_Wind_object()

        # Test that attributes are correctly initialized
        for key, value in TEST_PARAMS.items():
            assert getattr(wind, key) == value

        # Test internal parameters dictionary
        assert wind._model.parameters == TEST_PARAMS

    # ============== Method Tests ==============

    def test_production(self):
        """
        Test wind power production calculation.
        """
        wind = self.create_basic_Wind_object()
        wind_speed = 10 

        # Method constants
        radius = wind.diameter / 2
        air_density = 1.225

        # Adjust wind speeds for height
        wind.u60 = wind_speed * ((60 / 100) ** 0.14)
        wind.u25 = wind.u60 * (np.log(20 / 0.2) / np.log(60 / 0.2))

        # Calculate expected power based on output type
        if wind.output_type == 'energy':
            wind.resolution_h = 1  # Mock resolution
            expected_power = ((0.5 * (wind.u25 ** 3) * (np.pi * (radius ** 2)) * air_density * wind.cp) / 1000) * wind.resolution_h
        elif wind.output_type == 'power':
            expected_power = ((0.5 * (wind.u25 ** 3) * (np.pi * (radius ** 2)) * air_density * wind.cp) / 1000)
        else:
            raise ValueError(f"Invalid output_type: {wind.output_type}")

        expected_power = round(expected_power, 5)
        actual_output = round(wind.production(wind_speed)['wind_gen'], 5)
        assert actual_output == expected_power

    def test_generation(self):
        """
        Test wind power generation calculation, covering all cases and subcases in the exact order of the model method.
        """
        wind = self.create_basic_Wind_object()

        # Case 1: `self.u25 >= self.u_rated`
        # Subcase 1a: `self.u25 == self.u_rated`
        wind_speed_at_rated = wind.u_rated
        wind.u60 = wind_speed_at_rated * ((60 / 100) ** 0.14)
        wind.u25 = wind.u60 * (np.log(20 / 0.2) / np.log(60 / 0.2))

        if wind.u25 == wind.u_rated:
            if wind.output_type == 'power':
                expected_output = wind.p_rated
            elif wind.output_type == 'energy':
                wind.resolution_h = 1  # Mock time resolution
                expected_output = wind.p_rated * wind.resolution_h
            actual_output = wind.generation(wind_speed_at_rated)['wind_gen']
            assert actual_output == expected_output, (
                f"Subcase 1a failed: Expected {expected_output}, got {actual_output} for u25 == u_rated"
            )

        # Subcase 1b: `self.u25 > self.u_rated and self.u25 <= self.u_cutout`
        wind_speed_between_rated_and_cutout = (wind.u_rated + wind.u_cutout) / 2
        wind.u60 = wind_speed_between_rated_and_cutout * ((60 / 100) ** 0.14)
        wind.u25 = wind.u60 * (np.log(20 / 0.2) / np.log(60 / 0.2))

        if wind.u25 > wind.u_rated and wind.u25 <= wind.u_cutout:
            if wind.output_type == 'power':
                expected_output = wind.p_rated
            elif wind.output_type == 'energy':
                wind.resolution_h = 1
                expected_output = wind.p_rated * wind.resolution_h
            actual_output = wind.generation(wind_speed_between_rated_and_cutout)['wind_gen']
            assert actual_output == expected_output, (
                f"Subcase 1b failed: Expected {expected_output}, got {actual_output} for u25 > u_rated and u25 <= u_cutout"
            )

        # Subcase 1c: `self.u25 > self.u_cutout`
        wind_speed_above_cutout = wind.u_cutout + 1
        wind.u60 = wind_speed_above_cutout * ((60 / 100) ** 0.14)
        wind.u25 = wind.u60 * (np.log(20 / 0.2) / np.log(60 / 0.2))

        if wind.u25 > wind.u_cutout:
            expected_output = 0
            actual_output = wind.generation(wind_speed_above_cutout)['wind_gen']
            assert actual_output == expected_output, (
                f"Subcase 1c failed: Expected {expected_output}, got {actual_output} for u25 > u_cutout"
            )

        # Case 2: `self.u25 < self.u_cutin`
        wind_speed_below_cutin = wind.u_cutin - 0.1
        wind.u60 = wind_speed_below_cutin * ((60 / 100) ** 0.14)
        wind.u25 = wind.u60 * (np.log(20 / 0.2) / np.log(60 / 0.2))

        if wind.u25 < wind.u_cutin:
            expected_output = 0
            actual_output = wind.generation(wind_speed_below_cutin)['wind_gen']
            assert actual_output == expected_output, (
                f"Case 2 failed: Expected {expected_output}, got {actual_output} for u25 < u_cutin"
            )

        # Case 3: `self.u25 >= self.u_cutin and self.u25 < self.u_rated`
        wind_speed_intermediate = (wind.u_cutin + wind.u_rated) / 2
        wind.u60 = wind_speed_intermediate * ((60 / 100) ** 0.14)
        wind.u25 = wind.u60 * (np.log(20 / 0.2) / np.log(60 / 0.2))

        if wind.u25 >= wind.u_cutin and wind.u25 < wind.u_rated:
            expected_output = wind.production(wind_speed_intermediate)['wind_gen']
            actual_output = wind.generation(wind_speed_intermediate)['wind_gen']
            assert actual_output == expected_output, (
                f"Case 3 failed: Expected {expected_output}, got {actual_output} for u25 >= u_cutin and u25 < u_rated"
            )

    def test_connect_happy_flow(self):
        """
        Test connect method for setting inputs.
        """
        wind = self.create_basic_Wind_object()
        wind.time_resolution = 3600  # Mock 1-hour resolution

        inputs = {
            'u': {'u': {'source': {'value': 20, 'message_origin': 'output'}}}  # Wind speed at hub height (100m)
        }
        wind.step(0, inputs)        
        assert wind.u == 20
        
    def test_step_happy_flow(self):
        """
        Test the step function for correct state and output updates.
        """
        wind = self.create_basic_Wind_object()
        wind.time_resolution = 3600  # Mock 1-hour resolution

        # Define inputs
        inputs = {
            'u': {'u': {'source': {'value': 15, 'message_origin': 'output'}}}  # Wind speed at hub height (100m)
        }

        # So far like the test_connect_happy_flow method to make connection

        next_time = wind.step(0, inputs)

        expected_generation = wind.generation(15)  # Call generation method
        expected_wind_gen = expected_generation['wind_gen']  # Extract the wind_gen value
        expected_u = expected_generation['u']  # Extract the adjusted u value

        # Check updated outputs
        assert wind.outputs['wind_gen']['value'] == expected_wind_gen
        assert wind.outputs['u']['value'] == expected_u

        # Check updated states
        assert wind.states['u60']['value'] == pytest.approx(15 * ((60 / 100) ** 0.14))
        assert wind.states['u25']['value'] == pytest.approx(wind.states['u60']['value'] * (np.log(20 / 0.2) / np.log(60 / 0.2)))

        # Check returned time
        assert next_time == 1, f"Expected next time: 1, got {next_time}"

