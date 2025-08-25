import unittest
from illuminator.models.PV.pv_model_v3 import PV
from unittest.mock import patch
import math


class TestPVModel(unittest.TestCase):
    def setUp(self):
        self.pv = PV()

    def test_step(self):
        val = self.pv.step(0, None, 150)
        self.assertEqual(val, 150)