import pytest
import numpy as np
from illuminator.models.PV.pv_model import PV_py_model

class TestPVModelMethods():
    """
    Unit tester for the PV model
    """

    def create_basic_PV_object(self):
        """
        Creates the PV object with some pre-set data.
        This method was created to avoid boilerplate code.
        """
        # Independent variables
        panel_data = {'Module_area': 1.26, 'NOCT': 44, 'Module_Efficiency': 0.198, 'Irradiance_at_NOCT': 800, 'Power_output_at_STC': 250, 'peak_power': 600}
        m_tilt = 14
        m_az = 180
        cap = 500
        output_type = "power"
        resolution = 15

        # Dependent variable
        return PV_py_model(panel_data, m_tilt, m_az, cap, output_type, resolution)


    def test_constructor_happy_flow(self):
        """
        The expected __init__ constructor outcome when creating the class object when given all expected values.
        """
        # Independent variables
        panel_data = {'Module_area': 1.26, 'NOCT': 44, 'Module_Efficiency': 0.198, 'Irradiance_at_NOCT': 800, 'Power_output_at_STC': 250, 'peak_power': 600}
        m_tilt = 14
        m_az = 180
        cap = 500
        output_type = "power"
        resolution = 15

        # Expected outcomes
        pv = PV_py_model(panel_data, m_tilt, m_az, cap, output_type, resolution)
        assert pv.m_area == panel_data["Module_area"]
        assert pv.NOCT == panel_data['NOCT']
        assert pv.m_efficiency_stc == panel_data['Module_Efficiency']
        assert pv.G_NOCT == panel_data['Irradiance_at_NOCT']
        assert pv.P_STC == panel_data['Power_output_at_STC']
        assert pv.peak_power == panel_data['peak_power']
        assert pv.m_tilt == m_tilt
        assert pv.m_az == m_az
        assert pv.cap == cap
        assert pv.output_type == output_type
        assert pv.resolution == resolution
        assert pv.time_interval == resolution / 60

    def test_constructor_missing_parameters(self):
        """
        Tests the __init__ constructor when creating the class object when given no expected values.
        """
        with pytest.raises(TypeError):
            pv = PV_py_model()

    def test_sun_azimuth_happy_flow(self):
        """
        Test for getter method of self.sun_az variable
        """
        # Independent variables
        pv = self.create_basic_PV_object()
        pv.sun_az = -175.14

        # Expected results
        assert pv.sun_azimuth() == pv.sun_az

    def test_sun_elevation_happy_flow(self):
        """
        Test for getter method of self.sun_el variable
        """
        # Independent variables
        pv = self.create_basic_PV_object()
        pv.sun_el = -15.5

        # Expected results
        assert pv.sun_elevation() == pv.sun_el

    def test_aoi_happy_flow_positive_aoi(self, monkeypatch):
        """
        aoi method performs small computations.
        Calculated value, with the given parameters, should be 0.03195
        """
        # Independent variables
        pv = self.create_basic_PV_object()
        monkeypatch.setattr(pv, "sun_elevation", lambda: -15.5)
        monkeypatch.setattr(pv, "sun_azimuth", lambda: -175.14)

        # Expected results
        expected_outcome = round(0.03195064, 5)
        actual_outcome = round(float(pv.aoi()), 5)
        assert actual_outcome == expected_outcome


    def test_aoi_happy_flow_negative_aoi(self, monkeypatch):
        """
        aoi method performs small computations.
        Calculated value, with the given parameters, should be 0
        """
        # Independent variables
        pv = self.create_basic_PV_object()
        monkeypatch.setattr(pv, "sun_elevation", lambda: -2)
        monkeypatch.setattr(pv, "sun_azimuth", lambda: -10)
        pv.m_tilt = 1
        pv.m_az = 10

        # Expected results
        expected_outcome = 0
        actual_outcome = pv.aoi()
        assert actual_outcome == expected_outcome

    def test_diffused_irr_happy_flow(self):
        """
        diffused_irr performs some small computations.
        Calculated value, with the given parameters, should be 0.98515
        """
        # Independent variables
        pv = self.create_basic_PV_object()
        pv.dhi = 1

        # Expected outcomes
        expected_value = 0.98515
        assert round(pv.diffused_irr(), 5) == expected_value

    def test_reflected_irr_happy_flow(self):
        """
        reflected_irr performs some small computations.
        Calculated value, with the given parameters, should be -0.60000
        """
        # Independent mocked methods and variables
        pv = self.create_basic_PV_object()
        pv.svf = 4
        pv.ghi = 1

        # Expected outcome
        expected_val = -0.60000
        assert round(pv.reflected_irr(), 5) == expected_val


    def test_direct_irr_happy_flow(self, monkeypatch):
        """
        direct_irr multiplies two values together.
                Calculated value, with the given parameters, should be 10
        """
        # Independent mocked methods and variables
        pv = self.create_basic_PV_object()
        monkeypatch.setattr(pv, "aoi", lambda: 1)
        pv.dni = 10

        # Expected outcome
        expected_dirr = 10
        assert pv.direct_irr() == expected_dirr

    def test_total_irr_happy_flow(self, monkeypatch):
        """
        Total_irr calls three methods and adds their values together.
                Calculated value, with the given parameters, should be 6
        """
        # Independent mocked methods and variables
        pv = self.create_basic_PV_object()
        monkeypatch.setattr(pv, "diffused_irr", lambda: 1)
        monkeypatch.setattr(pv, "reflected_irr", lambda: 2)
        monkeypatch.setattr(pv, "direct_irr", lambda: 3)

        # Expected outcome
        expected_irr = 6
        assert pv.total_irr() == expected_irr

    def test_Temp_effect_happy_flow(self, monkeypatch):
        """
        Test for the temp_effect calculation.
        Calculated value, with the given parameters, should be 0.20465
        """
        # Mocked methods and independent variables
        pv = self.create_basic_PV_object()
        monkeypatch.setattr(pv, "total_irr", lambda: 0.30000)
        pv.temp = 15.4
        pv.ws = 5.0

        # Dependent method and expected outcome
        expected_temp_effect = 0.20465
        assert round(pv.Temp_effect(),5) == expected_temp_effect
    
    @pytest.mark.skip(reason="Numpy divide is used for 0 division, which sets 0 division to -inf.")
    def test_Temp_effect_zero_division_error(self, monkeypatch):
        """
        Test for the temp_effect calculation with `G_NOCT` being set to 0
        """
        # Mocked methods and independent variables
        pv = self.create_basic_PV_object()
        monkeypatch.setattr(pv, "total_irr", lambda: 0.30000)
        pv.temp = 15.4
        pv.ws = 5.0

        # G_NOCT value should never be zero
        pv.G_NOCT = 0
        # Dependent method and expected outcome
        with pytest.raises(ZeroDivisionError):
            test = pv.Temp_effect()
        
    def test_Temp_effect_zero_division_pass(self, monkeypatch):
        """
        Test for the temp_effect calculation with `G_NOCT` being set to 0
        """
        # Mocked methods and independent variables
        pv = self.create_basic_PV_object()
        monkeypatch.setattr(pv, "total_irr", lambda: 0.30000)
        pv.temp = 15.4
        pv.ws = 5.0

        # G_NOCT value should never be zero, however Numpy handles it by setting it to negative infinity
        pv.G_NOCT = 0
        # Dependent method and expected outcome
        assert np.isinf(pv.Temp_effect())


    def test_output_power_happy_flow(self, monkeypatch):
        """
        Output test with the **power** output type.
        This happy flow sets `total_irr` value as 0.3 and `Temp_effect as 0.20465

        Expected power output for these values should be 0.21395
        """
        # Mocked methods and independent variables
        pv = self.create_basic_PV_object()
        monkeypatch.setattr(pv, "total_irr", lambda: 0.30000) # Letting pytest know what to return when `total_irr` is called
        monkeypatch.setattr(pv, "Temp_effect", lambda: 0.20465)
        pv.g_aoi = 0.30000
        
        # Dependend methods
        output = pv.output()
        output['pv_gen'] = round(output['pv_gen'], 5)

        # With the given mocked attributes we expect the following value rounded to 5 decimals
        assert output == {'pv_gen': 0.21395, 'total_irr': pv.g_aoi}
        

    def test_output_energy_happy_flow(self, monkeypatch):
        """
        Output test with the **power** output type.
        This happy flow sets `total_irr` value as 0.3 and `Temp_effect as 0.20465

        Expected power output for these values should be 0.21395
        """
        # Mocked methods and independent variables
        pv = self.create_basic_PV_object()
        monkeypatch.setattr(pv, "total_irr", lambda: 0.30000)
        monkeypatch.setattr(pv, "Temp_effect", lambda: 0.20465)
        pv.g_aoi = 0.30000
        pv.output_type = "energy"
        
        # Dependent methods
        output = pv.output()
        output['pv_gen'] = round(output['pv_gen'], 5)

        # With the given mocked attributes we expect the following value rounded to 5 decimals
        assert output == {'pv_gen': 0.05349, 'total_irr': pv.g_aoi}

    def test_output_invalid_output_type(self, monkeypatch):
        """
        Output test with the **power** output type.
        This happy flow sets `total_irr` value as 0.3 and `Temp_effect as 0.20465

        Expected power output for these values should be 0.21395
        """
        # Mocked methods and independent variables
        pv = self.create_basic_PV_object()
        monkeypatch.setattr(pv, "total_irr", lambda: 0.30000) # Letting pytest know what to return when `total_irr` is called
        monkeypatch.setattr(pv, "Temp_effect", lambda: 0.20465)
        pv.g_aoi = 0.30000
        pv.output_type = "INVALID"

        
        # Dependend methods
        with pytest.raises(NameError):
            output = pv.output()


    def test_connect_happy_flow(self, monkeypatch):
        """
        The connect method with an expected happy flow.
        It is dependent on the `output` method, thus it must be mocked.
        """
        # Mocked methods
        # Output does not influence the connect method, thus it's return value is irrelevant
        pv = self.create_basic_PV_object()
        monkeypatch.setattr(pv, "output", lambda: {})

        # Independent variables
        G_Gh, G_Dh, G_Bn, Ta, hs, FF, Az = 0.0, 0.0, 0.0, 15.4, -15.5, 5.0, -175.14

        # Expected return value
        assert pv.connect(G_Gh, G_Dh, G_Bn, Ta, hs, FF, Az) == {}

        # Exepcted attributes set after pv.connect was called
        assert pv.ghi == G_Gh
        assert pv.dhi == G_Dh
        assert pv.dni == G_Bn
        assert pv.temp == Ta
        assert pv.sun_el == hs
        assert pv.ws == FF
        assert pv.sun_az == Az

    def test_connect_missing_parameters(self):
        """
        The connect method when given no expected values should return a type error
        """
        pv = self.create_basic_PV_object()
        with pytest.raises(TypeError):
            pv.connect()



