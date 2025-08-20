import pytest
from unittest.mock import patch
import unittest
from illuminator.models.Wind.wind_v3 import Wind

class TestWindModelMethods(unittest.TestCase):
    """
    Unit tester for the Wind (v3) model.
    """

    def create_basic_load_object(self):
        """
        Creates the Load object with some pre-set data.
        This method was created to avoid boilerplate code.
        """
    
        self.parameters={'p_rated': 501,  # Rated power output (kW) of the wind turbine at the rated wind speed and above.
                        'u_rated': 101,  # Rated wind speed (m/s) where the wind turbine reaches its maximum power output.
                        'u_cutin': 2,  # Cut-in wind speed (m/s) below which the wind turbine does not generate power.
                        'u_cutout': 1001,  # Cut-out wind speed (m/s) above which the wind turbine stops generating power to prevent damage.
                        'cp': 0.41,  # Coefficient of performance of the wind turbine, typically around 0.40 and never more than 0.59.
                        'diameter': 31,  # Diameter of the wind turbine rotor (m), used in calculating the swept area for wind power production.
                        'output_type': 'energy'  # Output type of the wind generation, either 'power' (kW) or 'energy' (kWh).
                        }
        self.inputs={'u': 1,  # Wind speed (m/s) at a specific height used to calculate the wind power generation.
                }
        self.outputs={'wind_gen': 1,  # Generated wind power output (kW) or energy (kWh) based on the chosen output type (power or energy).
                    'u': 1  # Adjusted wind speed (m/s) at 25m height after converting from the original height (e.g., 100m or 60m).
                    }
        self.states={'u60': 11,  # Wind speeds adjusted for 60m height using logarithmic wind profile equations.
                    'u25': 1  # Wind speeds adjusted for 25m height using logarithmic wind profile equations.
                }
        return Wind(parameters=self.parameters, inputs=self.inputs, outputs=self.outputs, states=self.states)


    def test_wind_init(self):
    # Create an instance of the Wind model
        wind_model = self.create_basic_load_object()

        assert wind_model.inputs == self.inputs
        assert wind_model.outputs == self.outputs
        assert wind_model.states == self.states
        assert wind_model.parameters == self.parameters
        assert wind_model.p_rated == 501
        assert wind_model.u_rated == 101
        assert wind_model.u_cutin == 2
        assert wind_model.u_cutout == 1001
        assert wind_model.cp == 0.41
        assert wind_model.diameter == 31
        assert wind_model.output_type == 'energy'


    @patch.object(Wind, "unpack_inputs", new=lambda self, inputs: {"u": 9.67})
    @patch.object(Wind, "generation", new=lambda self, u: {"wind_gen": 20, "u": 4.8})
    @patch.object(Wind, "set_outputs", new=lambda self, outputs: None)
    @patch.object(Wind, "set_states", new=lambda self, states: None)
    def test_load_step(self):
        """
        Test the step method of the Wind model.
        """
        wind_model = self.create_basic_load_object()
        wind_model.time_resolution = 900
        in_dict = {'time-based_0': {'u': {'CSV_wind-0.time-based_0': {'message_origin': 'state', 'value': 9.67}}}}
        assert wind_model.step(time=3, inputs=in_dict, max_advance=1) == 4


    @patch.object(Wind, 'production', new=lambda self, u: {'wind_gen': 66.50, 'u': 7.27})
    def test_wind_generation(self):
        """
        Test the wind generation calculation.
        """
        wind_model = self.create_basic_load_object()
        result =  wind_model.generation(9.67)
        self.assertAlmostEqual(result['wind_gen'], 66.50, places=2)
        self.assertAlmostEqual(result['u'], 7.27, places=2)
    

    def test_wind_production(self):
        """
        Test the wind production calculation.
        """
        wind_model = self.create_basic_load_object()
        result = wind_model.production(9.67)
        self.assertAlmostEqual(result['wind_gen'], 66.50, places=2)
        self.assertAlmostEqual(result['u'], 7.27, places=2)


if __name__ == "__main__":
    tester = TestWindModelMethods()
    tester.test_wind_init()
    tester.test_load_step()
    tester.test_wind_generation()
    tester.test_wind_production()