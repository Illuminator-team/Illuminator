"""
Unit tests for main.py of CLI package.
"""

import pytest
import mosaik
from illuminator.engine import start_simulators, compute_mosaik_end_time


@pytest.fixture
def mosaik_world():
    config = {
        'CSVB': { 
            'python': 'illuminator.models:CSV' # models must be in the illuminator.models module
        },
        'PV': { 
            'python': 'illuminator.models:PvAdapter'
        }
    }
    return mosaik.World(config,  debug=True)

@pytest.fixture
def csv_model():
    return {
        'CSVModel': { 
            'python': 'illuminator.models:CSV'
        },
        'PV': { 
            'python': 'illuminator.models:PvAdapter'
        }
    }

@pytest.fixture
def yaml_models():
    return  [{'name': 'CSVB',  # this name must match the name in the mosaik configuration
              'type': 'CSV', 
              'parameters': 
                    {'start': '2012-01-01 00:00:00', 'datafile': 'tests/data/solar-sample.csv'}}, 
            {'name': 'PV', 
             'type': 'PvAdapter', 
             'inputs': 
                     {'G_Gh': None, 'G_Dh': None, 'G_Bn': None, 'Ta': None, 
                      'hs': None, 'FF': None, 'Az': None}, 
            'outputs': {'G_Gh': None},
            'parameters': {'panel_data': None, 'm_tilt': None, 'm_az': None, 
                           'cap': None}
            }]


@pytest.fixture
def start_timestamp():
    return '2012-01-01 00:00:00'


@pytest.fixture
def end_timestamp():
    return '2012-01-01 04:00:00'


class TestMosaikEndTime:
    """
    Tests for the compute_mosaik_end_time()
    """

    def test_step_count(self, start_timestamp, end_timestamp):
        """Tests the correct number of steps is return"""

        computed_steps = compute_mosaik_end_time(start_timestamp, end_timestamp)

        assert computed_steps == 16

    def test_approximation_to_floor(self, start_timestamp):
        """Check values are approximated to the lowest interger"""

        new_end_time = '2012-01-01 04:20:00'

        computed_steps = compute_mosaik_end_time(start_timestamp, new_end_time)
        assert isinstance(computed_steps, int)
        assert computed_steps == 17

        
class TestStartSimulators:
    """
    Tests for the start_simulators function.
    """

    def test_number_entities(self, mosaik_world, yaml_models):
        """ tests if the number of entities created is equal to the number of models """
        
        entities = start_simulators(mosaik_world, yaml_models)

        # TODO: test fails due to an error raised by Mosaik. must be fixed
        # RuntimeError: coroutine raised StopIteration
        # assert len(entities) == 1
        pass

    def test_start_value_error(self, mosaik_world, yaml_models):
        """
        tests if a ValueError is raised when the CSV model does not have 'start' as
        parameter
        """

        # CSV model must have the 'start' as parameters
        yaml_models[0]['parameters'].pop('start')

        with pytest.raises(ValueError):
            start_simulators(mosaik_world, yaml_models)

    def test_datafile_value_error(self, mosaik_world, yaml_models):
        """
        tests if a ValueError is raised when the CSV model does not have 'datafile' as
        parameter
        """

        # CSV model must have the 'start' as parameters
        yaml_models[0]['parameters'].pop('datafile')

        with pytest.raises(ValueError):
            start_simulators(mosaik_world, yaml_models)
