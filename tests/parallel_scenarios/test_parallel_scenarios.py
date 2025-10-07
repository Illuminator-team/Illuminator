import pytest
from ruamel.yaml import YAML
from illuminator import parallel_scenarios

import os

@pytest.fixture
def parallel_scenario():
    return {
        'scenario': {
            'name': "random_scenario",
            'start_time': '2007-07-02 00:00:00',
            'end_time': '2007-07-02 23:45:00',
            'time_resolution': 900
        },
        'models': [
            {
                'name': 'model1',
                'parameters': {
                    'p1': 10,
                    'p2': [1, 2, 3]
                },
                'states': {
                    's1': 0.5,
                    's2': [0.1, 0.2],
                    's3': 'active'
                }
            },
            {
                'name': 'model2',
                'parameters': {
                    'pA': 42,
                    'pB': 'text',
                    'pC': ["file1.txt", "data/file2.txt"]
                },
                'states': {
                    'sY': True
                }
            }
        ],
        'connections': [
            {'from': 'CSVload.load1', 'to': 'Load1.load'},
            {'from': 'Load1.load_dem', 'to': 'Controller1.load_dem'}
        ],
        'monitor': {
            'file': './out_tutorial4_parallel.csv',
            'items': [
                'PV1.pv_gen',
                'Load1.load_dem'
            ]
        }
    }


@pytest.fixture
def scenario():
    return {
        'scenario': {
            'name': "random_scenario",
            'start_time': '2007-07-02 00:00:00',
            'end_time': '2007-07-02 23:45:00',
            'time_resolution': 900
        },
        'models': [
            {
                'name': 'model1',
                'parameters': {
                    'p1': 10,
                },
                'states': {
                    's1': 0.5,
                    's3': 'active'
                }
            },
            {
                'name': 'model2',
                'parameters': {
                    'pA': 42,
                    'pB': 'text',
                },
                'states': {
                    'sY': True
                }
            }
        ],
        'connections': [
            {'from': 'CSVload.load1', 'to': 'Load1.load'},
            {'from': 'Load1.load_dem', 'to': 'Controller1.load_dem'}
        ],
        'monitor': {
            'file': './out_tutorial4_parallel.csv',
            'items': [
                'PV1.pv_gen',
                'Load1.load_dem'
            ]
        }
    }


def test_remove_fixture_parallel_params(scenario, parallel_scenario, tmp_path):
    # Create a temporary file for fixture
    temp_file = tmp_path / "temp_parallel_scenario.yaml"
    yaml = YAML()
    with temp_file.open('w') as f:
        yaml.dump(parallel_scenario, f)
    
    # Call the function using the temp file path
    cleaned_data, removed_items = parallel_scenarios._remove_scenario_parallel_items(str(temp_file))

    # Assertions on removed_items
    expected_removed = [
        ('model1', 'parameter', 'p2', [1, 2, 3] ),
        ('model1', 'state', 's2', [0.1, 0.2] ),
        ('model2', 'parameter', 'pC', ["file1.txt", "data/file2.txt"] ),
    ]

     # Assert the removed items match exactly
    assert sorted(removed_items) == sorted(expected_removed)

    # Check that cleaned_data exactly matches the serial scenario
    assert cleaned_data == scenario


def test_remove_file_parallel_params():    
    # Remove lists and ranges
    cleaned_data, removed_items = parallel_scenarios._remove_scenario_parallel_items('tests/parallel_scenarios/data/parallel1.yaml')

    # Assertions on removed_items
    expected_removed = [
        ('CSV_EV_presence', 'parameter', 'file_path', ['./data/data1.csv', './data/data2.csv'] ),
        ('CSVload', 'parameter', 'file_path', ['data3.csv', 'data4.csv']),
        ('PV1', 'parameter', 'm_efficiency_stc', [0.198, 0.350, 2.73, 11.46]),
        ('PV1', 'parameter', 'cap', [500, 750, 1080]),
        ('Battery1', 'parameter', 'max_energy', [1000, 2000, 3000]),
        ('Battery1', 'parameter', 'soc_max', [90, 80, 70]),
        ('Battery1', 'state', 'mod', [0, 1, -1]),
        ('Battery1', 'state', 'soc', [50, 60, 70])
    ]

    # Assert the removed items match exactly
    assert sorted(removed_items) == sorted(expected_removed)

    # Build a dictionary of models in cleaned_data for easy lookup
    clean_models = {}
    for model in cleaned_data.get('models', []):
        model_name = model['name']  # get the model name
        clean_models[model_name] = model

    # Verify that each removed key is actually removed from cleaned_data
    for model_name, section, key, value in expected_removed:
        # Check cleaned_data still contains the model
        assert model_name in clean_models, f"Model '{model_name}' not found in cleaned data"
        clean_model = clean_models[model_name]

        if section == 'parameter':
            assert 'parameters' in clean_model, f"Section 'parameters' missing in model '{model_name}'"
            assert key not in clean_model['parameters'], f"Key '{key}' still present in 'parameters' of model '{model_name}'"
        elif section == 'state':
            assert 'states' in clean_model, f"Section 'states' missing in model '{model_name}'"
            assert key not in clean_model['states'], f"Key '{key}' still present in 'states' of model '{model_name}'"


def test_generate_combinations_cartesian():
    """Test Cartesian product generation (align=False)"""
    items = [
        ('model1', 'parameter', 'p2', [1, 2, 3] ),
        ('model1', 'state', 's2', [0.1, 0.2] ),
        ('model2', 'parameter', 'pC', ["file1.txt", "data/file2.txt"] ),
    ]

    # Expected combinations
    expected_combinations = [
        {'simulationID': 1, ('model1','parameter','p2'): 1, ('model1','state','s2'): 0.1, ('model2','parameter','pC'): "file1.txt"},
        {'simulationID': 2, ('model1','parameter','p2'): 1, ('model1','state','s2'): 0.1, ('model2','parameter','pC'): "data/file2.txt"},
        {'simulationID': 3, ('model1','parameter','p2'): 1, ('model1','state','s2'): 0.2, ('model2','parameter','pC'): "file1.txt"},
        {'simulationID': 4, ('model1','parameter','p2'): 1, ('model1','state','s2'): 0.2, ('model2','parameter','pC'): "data/file2.txt"},
        {'simulationID': 5, ('model1','parameter','p2'): 2, ('model1','state','s2'): 0.1, ('model2','parameter','pC'): "file1.txt"},
        {'simulationID': 6, ('model1','parameter','p2'): 2, ('model1','state','s2'): 0.1, ('model2','parameter','pC'): "data/file2.txt"},
        {'simulationID': 7, ('model1','parameter','p2'): 2, ('model1','state','s2'): 0.2, ('model2','parameter','pC'): "file1.txt"},
        {'simulationID': 8, ('model1','parameter','p2'): 2, ('model1','state','s2'): 0.2, ('model2','parameter','pC'): "data/file2.txt"},
        {'simulationID': 9, ('model1','parameter','p2'): 3, ('model1','state','s2'): 0.1, ('model2','parameter','pC'): "file1.txt"},
        {'simulationID': 10, ('model1','parameter','p2'): 3, ('model1','state','s2'): 0.1, ('model2','parameter','pC'): "data/file2.txt"},
        {'simulationID': 11, ('model1','parameter','p2'): 3, ('model1','state','s2'): 0.2, ('model2','parameter','pC'): "file1.txt"},
        {'simulationID': 12, ('model1','parameter','p2'): 3, ('model1','state','s2'): 0.2, ('model2','parameter','pC'): "data/file2.txt"},
    ]

    combinations = parallel_scenarios._generate_combinations_from_removed_items(items, align=False)

    # Check the amount of combinations
    assert len(combinations) == len(expected_combinations)

    # Check each expected combination is in the actual combinations
    for expected in expected_combinations:
        found = False
        for actual in combinations:
            if actual == expected:
                found = True
                break
        assert found, f"Expected combination not found: {expected}"


def test_generate_combinations_aligned():
    """Test aligned generation (align=True)"""
    items = [
        ('model1', 'parameter', 'p2', [1, 2] ),
        ('model1', 'state', 's2', [0.1, 0.2] ),
        ('model2', 'parameter', 'pC', ["file1.txt", "data/file2.txt"] ),
    ]

    # Expected combinations
    expected_combinations = [
        {'simulationID': 1, ('model1','parameter','p2'): 1, ('model1','state','s2'): 0.1, ('model2','parameter','pC'): "file1.txt"},
        {'simulationID': 2, ('model1','parameter','p2'): 2, ('model1','state','s2'): 0.2, ('model2','parameter','pC'): "data/file2.txt"}
    ]

    combinations = parallel_scenarios._generate_combinations_from_removed_items(items, align=True)

    # Check the amount of combinations
    assert len(combinations) == len(expected_combinations)

    # Check each expected combination is in the actual combinations
    for expected in expected_combinations:
        found = False
        for actual in combinations:
            if actual == expected:
                found = True
                break
        assert found, f"Expected combination not found: {expected}"    

    
def test_generate_combinations_aligned_raises():
    """Test that align=True raises ValueError when lists have different lengths"""
    items = [
        ('model1', 'parameter', 'p2', [1, 2, 3] ),
        ('model1', 'state', 's2', [0.1, 0.2] ),
        ('model2', 'parameter', 'pC', ["file1.txt", "data/file2.txt"] ),
    ]
    with pytest.raises(ValueError):
        parallel_scenarios._generate_combinations_from_removed_items(items, align=True)
