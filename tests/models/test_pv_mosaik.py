import pytest
import numpy as np
import pandas as pd
from illuminator.models.PV.pv_model import PV_py_model
from illuminator.models.PV.pv_mosaik import PvAdapter

class TestPVMosaikMethods():
    """
    Unit tester for the PV mosaik
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
        Tests the constructor happy flow.
        Relatively simple test which only checks if attributes were created
        """
        # Independent variables
        pv = PvAdapter()

        # Expected outcome
        assert type(pv.meta) == dict # Its value is irrelevant
        assert pv.eid_prefix == 'pv_'
        assert pv.entities == pv.mods == pv._cache == {}  # all of these should be an empty dictionary

    def test_init_happy_flow(self):
        """
        The mosaik init override function test.
        Only creates and checks for a few extra attributes.
        """
        # Independent variables
        pv = PvAdapter()
        
        # Expected outcomes
        output = pv.init(sid=None, time_resolution=5)
        assert pv.time_resolution == 5
        assert pv.meta == output
    
    @pytest.mark.skip(reason="[WIP] This test is currently incomplete.")
    def test_create_happy_flow(self, monkeypatch):
        """
        This test is currently being skipped due to its heavy dependency on the mosaik api.
        """
        # Independent variables and mocked methods
        pv = PvAdapter()
        num = 1 
        model = "PVset"
        sim_start = "2012-06-01 00:00:00"
        # {'panel_data': {'Module_area': 1.26, 'NOCT': 44, 'Module_Efficiency': 0.198, 'Irradiance_at_NOCT': 800, 'Power_output_at_STC': 250, 'peak_power': 600}, 'm_tilt': 14, 'm_az': 180, 'cap': 500, 'output_type': 'power'}
        # model_params = {'panel_data': {'Module_area': 1.26, 'NOCT': 44, 'Module_Efficiency': 0.198, 'Irradiance_at_NOCT': 800, 'Power_output_at_STC': 250, 'peak_power': 600}, 'm_tilt': 14, 'm_az': 180, 'cap': 500}
        model_params = {
            "panel_data" : {'Module_area': 1.26, 'NOCT': 44, 'Module_Efficiency': 0.198, 'Irradiance_at_NOCT': 800, 'Power_output_at_STC': 250, 'peak_power': 600},
            "m_tilt" : 14,
            "m_az" : 180,
            "cap" : 500,
            "output_type" : "power",
            "resolution" : 15
        }
        actual_entities = pv.create(num, model, sim_start, model_params)
        expected_entities = [{'eid': 'pv_0', 'type': 'PVset'}]
        
        
        
        assert pv.start == pd.to_datetime(sim_start)
        assert pv.entities['pv_0'] == {}
        assert actual_entities == expected_entities
    
    def test_step_happy_flow(self, monkeypatch):
        """
        An implementation of the step happy flow.
        None is expected as a return value, while the `self._cache` attribute gains a new value.
        """
        # Independent variables
        time = 0
        inputs = {'pv_0': {'G_Gh': {'CSVB-1.Solar_data_0': 0.0}, 'G_Dh': {'CSVB-1.Solar_data_0': 0.0}, 'G_Bn': {'CSVB-1.Solar_data_0': 0.0}, 'Ta': {'CSVB-1.Solar_data_0': 15.4}, 'hs': {'CSVB-1.Solar_data_0': -15.5}, 'FF': {'CSVB-1.Solar_data_0': 5.0}, 'Az': {'CSVB-1.Solar_data_0': -175.14}}}
        max_advance = 899

        # Independent objects and its attributes
        pv = PvAdapter()
        pv.start = pd.to_datetime("2012-06-01 00:00:00")
        pv.time_resolution = 1
        pv_model = self.create_basic_PV_object()
        pv.entities = {'pv_0':pv_model}

        # Mock function to use
        def mock_connect(*args):
            return 0

        monkeypatch.setattr(pv_model, "connect", mock_connect)

        # Expected outcome: No returns, _cache is what we have set it to
        assert pv.step(time, inputs, max_advance) == None
        assert pv._cache['pv_0'] == 0
    
    def test_get_data_happy_flow(self):
        """
        A relatively simple getter test.
        Gets values from `self._cache` attribute
        """
        # Independent variables
        output = {'pv_0': ['pv_gen', 'total_irr']}
        pv = PvAdapter()
        pv._cache = {'pv_0': {'pv_gen': 1.0, 'total_irr': 2.0}}
        expected_dict = {'pv_0': {'pv_gen': 1.0, 'total_irr': 2.0}}

        # Dependent variables and expected output
        output_dict = pv.get_data(output)
        assert output_dict == expected_dict