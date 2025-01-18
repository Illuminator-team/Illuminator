import pytest
import numpy as np
from illuminator.models.PV.pv_model_v3 import PV

#                                     PV_V3 TEST
# ============================================================================
#   This file contains unit tests for v3 of the pv model. The tests include:
#       1. Test values for validating model methods and outputs.
#       2. Object initialization with test value parameters.
#       3. Validation of initialization with and without given values.
#       4. Tests for each method of the model.
# ============================================================================

# Define test parameters for reuse
TEST_PARAMS = {
    'm_area': 1.26,
    'NOCT': 44,
    'm_efficiency_stc': 0.198,
    'G_NOCT': 800,
    'P_STC': 250,
    'peak_power': 600,
    'm_tilt': 14,
    'm_az': 180,
    'cap': 500,
    'output_type': "power",
    'sim_start': 0
}

class TestPVModelMethods:
    """
    Unit tester for the PV model
    """
    def test_constructor_missing_parameters(self):
        """
        Tests the parameter default values work properly.
        """
        pv = PV()
        assert pv.m_area == 0
        assert pv.NOCT == 0
        assert pv.m_efficiency_stc == 0
        assert pv.G_NOCT == 0
        assert pv.P_STC == 0
        assert pv.m_tilt == 0
        assert pv.m_az == 0
        assert pv.cap == 0
        assert pv.output_type == "power"

    def create_basic_PV_object(self):
        """
        Creates the PV object with pre-set data.
        This method avoids boilerplate code for creating the PV model object.
        """
        pv = PV()
        pv._model.parameters.update(TEST_PARAMS)
        for key, value in TEST_PARAMS.items():
            setattr(pv, key, value)
        return pv

    def test_constructor_happy_flow(self):
        """
        The expected __init__ constructor outcome when creating the class object with all expected values.
        """
        pv = self.create_basic_PV_object()

        # Test that attributes are correctly initialized
        for key, value in TEST_PARAMS.items():
            assert getattr(pv, key) == value

        # Test internal parameters dictionary
        assert pv._model.parameters == TEST_PARAMS

    # ============== Method Tests ==============

    def test_sun_azimuth_happy_flow(self):
        """
        Test for getter method of self.sun_az variable
        """
        pv = self.create_basic_PV_object()
        pv.sun_az = -175.14
        assert pv.sun_azimuth() == -175.14

    def test_sun_elevation_happy_flow(self):
        """
        Test for getter method of self.hs variable
        """
        pv = self.create_basic_PV_object()
        pv.hs = -15.5
        assert pv.sun_elevation() == -15.5

    def test_aoi_happy_flow_positive(self, monkeypatch):
        """
        Test AOI calculation with positive result.
        """
        pv = self.create_basic_PV_object()
        monkeypatch.setattr(pv, "sun_elevation", lambda: -15.5)
        monkeypatch.setattr(pv, "sun_azimuth", lambda: -175.14)
        expected_outcome = round(0.03195064, 5)
        actual_outcome = round(float(pv.aoi()), 5)
        assert actual_outcome == expected_outcome

    def test_aoi_happy_flow_zero(self, monkeypatch):
        """
        Test AOI calculation with a zero result.
        """
        pv = self.create_basic_PV_object()
        monkeypatch.setattr(pv, "sun_elevation", lambda: -2)
        monkeypatch.setattr(pv, "sun_azimuth", lambda: -10)
        pv.m_tilt = 1
        pv.m_az = 10
        assert pv.aoi() == 0

    def test_diffused_irr_happy_flow(self):
        """
        Test diffuse irradiance calculation.
        """
        pv = self.create_basic_PV_object()
        pv.G_Dh = 1
        pv.m_tilt = 30
        expected_value = round((1 + np.cos(np.radians(30))) / 2 * 1, 5)
        rounded_diffused_irr = round(pv.diffused_irr(), 5)
        assert rounded_diffused_irr == expected_value

    def test_reflected_irr_happy_flow(self):
        """
        Test reflected irradiance calculation.
        """
        pv = self.create_basic_PV_object()
        pv.G_Gh = 1000  # Set the global horizontal irradiance
        pv.m_tilt = 30  # Set the tilt angle
        pv.svf = (1 + np.cos(np.radians(30))) / 2  # Sky view factor based on tilt

        # Method Constants
        albedo = 0.2
        expected_val = round(albedo * (1 - pv.svf) * pv.G_Gh, 5)
        rounded_reflected_irr = round(pv.reflected_irr(), 5)
        
        assert rounded_reflected_irr == expected_val

    def test_direct_irr_happy_flow(self, monkeypatch):
        """
        Test direct irradiance calculation.
        """
        pv = self.create_basic_PV_object()
        monkeypatch.setattr(pv, "aoi", lambda: 1)
        pv.G_Bn = 10
        assert pv.direct_irr() == 10

    def test_total_irr_happy_flow(self, monkeypatch):
        """
        Test total irradiance calculation.
        """
        pv = self.create_basic_PV_object()
        monkeypatch.setattr(pv, "diffused_irr", lambda: 1)
        monkeypatch.setattr(pv, "reflected_irr", lambda: 2)
        monkeypatch.setattr(pv, "direct_irr", lambda: 3)
        assert pv.total_irr() == 6

    def test_Temp_effect_happy_flow(self, monkeypatch):
        """
        Test temperature effect on module efficiency.
        """
        pv = self.create_basic_PV_object()
        monkeypatch.setattr(pv, "total_irr", lambda: 300)  # Mock total irradiance
        pv.Ta = 25  # Ambient temperature
        pv.FF = 5  # Wind speed factor

        # Method Constants
        m_temp = 25 + (300 / TEST_PARAMS['G_NOCT']) * (TEST_PARAMS['NOCT'] - 20) * (9.5 / (5.7 + 3.8 * 5)) * (1 - (TEST_PARAMS['m_efficiency_stc'] / 0.90))
        expected_efficiency = round(TEST_PARAMS['m_efficiency_stc'] * (1 + (-0.0035 * (m_temp - 25))), 5)

        rounded_efficiency = round(pv.Temp_effect(), 5)

        assert rounded_efficiency == expected_efficiency

    def test_output_power_happy_flow(self, monkeypatch):
        """
        Test output method with power output type.
        """
        pv = self.create_basic_PV_object()

        monkeypatch.setattr(pv, "total_irr", lambda: 300)  # Mock total irradiance (W/m^2)
        monkeypatch.setattr(pv, "Temp_effect", lambda: 0.20465)  # Mock temperature effect efficiency

        # Method Constants
        inv_eff = 0.96  # Inverter efficiency
        mppt_eff = 0.99  # MPPT efficiency
        losses = 0.97  # System losses
        sf = 1.1  # Safety factor

        num_of_modules = np.ceil(TEST_PARAMS['cap'] * sf / TEST_PARAMS['P_STC'])
        total_m_area = num_of_modules * TEST_PARAMS['m_area']
        expected_output = round((total_m_area * 300 * 0.20465 * inv_eff * mppt_eff * losses) / 1000, 5)  # Power (kW)

        rounded_output = round(pv.output()['pv_gen'], 5)

        assert rounded_output == expected_output

    def test_connect_happy_flow(self):
        """
        Test input unpacker by "forcing" connections.
        """
        pv = self.create_basic_PV_object()
        inputs = {  # This a working input dictionary format for connections
            'G_Gh': {'G_Gh': {'source': {'value': 600, 'message_origin': 'output'}}},
            'G_Dh': {'G_Dh': {'source': {'value': 200, 'message_origin': 'output'}}},
            'G_Bn': {'G_Bn': {'source': {'value': 300, 'message_origin': 'output'}}},
            'Ta': {'Ta': {'source': {'value': 25, 'message_origin': 'output'}}},
            'hs': {'hs': {'source': {'value': 45, 'message_origin': 'output'}}},
            'FF': {'FF': {'source': {'value': 2, 'message_origin': 'output'}}},
            'Az': {'Az': {'source': {'value': 180, 'message_origin': 'output'}}}
        }
        pv.step(0, inputs)
        assert pv.G_Gh == 600
        assert pv.G_Dh == 200
        assert pv.G_Bn == 300
        assert pv.Ta == 25
        assert pv.hs == 45
        assert pv.FF == 2
        assert pv.Az == 180
