import unittest
from illuminator.models.PV.pv_model_v3 import PV
from unittest.mock import patch
import math


class TestPVModel(unittest.TestCase):
    # NO MOCKING
    # def setUp(self):
    #     self.pv = PV()
    
    # Mocking
    @patch.object(PV, "__init__", lambda x: None)
    def test_sun_azimuth_happy_flow(self):
        # with patch.object(PV, "__init__", lambda x: None):
        self.pv = PV()
        self.pv.sun_az = -175.14
        self.assertEqual(self.pv.sun_azimuth(), self.pv.sun_az)
    
    @patch.object(PV, "__init__", lambda x: None)
    @patch.object(PV, "unpack_inputs", lambda x, y: {'G_Gh':0, 'G_Dh':0, 'G_Bn':0, 'Ta':0, 'hs':0, 'FF':0, 'Az':0})
    @patch.object(PV, "output", lambda x:{'pv_gen':3})
    @patch.object(PV, "set_outputs", lambda x, y: None)
    def test_step_happy_flow(self):
        self.pv = PV()
        self.pv._model = PV()
        self.pv._model.time_step_size = 150
        step = self.pv.step(0, None, max_advance=900)
        self.assertEqual(step, 150)
        self.assertEqual(self.pv.G_Gh, 0)
        self.assertEqual(self.pv.G_Dh, 0)
        self.assertEqual(self.pv.G_Bn, 0)
        self.assertEqual(self.pv.Ta, 0)
        self.assertEqual(self.pv.hs, 0)
        self.assertEqual(self.pv.FF, 0)
        self.assertEqual(self.pv.Az, 0)

    @patch.object(PV, "__init__", lambda x: None)
    @patch.object(PV, "sun_elevation", lambda x: 1)
    @patch.object(PV, "sun_azimuth", lambda x: 1)
    def test_aoi_happy_flow(self):
        self.pv = PV()
        self.pv.m_tilt = 1
        self.pv.m_az = 1
        self.assertAlmostEqual(float(self.pv.aoi()), 0.85879257)

    
    # @patch.object(PV, "__init__", lambda x: None)
    # @patch.object(PV, "sun_elevation", lambda x: 1)
    # @patch.object(PV, "sun_azimuth", lambda x: -(math.inf))
    # def test_aoi_neg_infinity(self):
    #     self.pv = PV()
    #     self.pv.m_tilt = 1
    #     self.pv.m_az = 1
    #     self.assertEqual(float(self.pv.aoi()), math.nan)




