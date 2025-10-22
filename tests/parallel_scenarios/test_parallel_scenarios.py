import pytest
from ruamel.yaml import YAML
from illuminator import parallel_scenarios
import csv
import copy


import os

@pytest.fixture
def parallel_scenario():
    return {
        'scenario': {
            'name': "random_scenario",
            'start_time': '2007-07-02 00:00:00',
            'end_time': '2007-07-02 23:45:00',
            'time_resolution': 900,
            'align_parameters': True
        },
        'models': [
            {
                'name': 'model1',
                'parameters': {
                    'p1': 10,
                    'p2': 7
                },
                'multi_parameters': {
                    'p3': [0.1, 2]
                },
                'states': {
                    's1': 0.5,
                    's2': 0.3,
                    's3': 'active'
                }
            },
            {
                'name': 'model2',
                'parameters': {
                    'pA': 42,
                    'pB': 'text'
                },
                'multi_parameters': {
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
                    'p2': 7
                },
                'states': {
                    's1': 0.5,
                    's2': 0.3,
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


@pytest.fixture
def scenario_multiparams_removed(scenario):
    new_scenario = copy.deepcopy(scenario)
    new_scenario['scenario']['align_parameters'] = True
    return new_scenario
    


# Test _remove_scenario_parallel_items

def test_remove_scenario_parallel_items(scenario_multiparams_removed):
    cleaned_data, removed_items = parallel_scenarios._remove_scenario_parallel_items('tests/parallel_scenarios/data/parallel_scenario.yaml')

    # Check the multi_parameters were removed correctly
    assert cleaned_data == scenario_multiparams_removed

    expected_removed = [
        ('model1', 'parameter', 'p3', [0.1, 2] ),
        ('model2', 'parameter', 'pC', ['file1.txt', 'data/file2.txt'] )
    ]

    # Check removed_items match exactly
    assert expected_removed == removed_items


# Test _generate_combinations_from_removed_items

def test_generate_combinations_cartesian():
    """Test Cartesian product generation (align=False)"""
    items = [
        ('model1', 'parameter', 'p2', [1, 2, 3] ),
        ('model1', 'parameter', 's2', [0.1, 0.2] ),
        ('model2', 'parameter', 'pC', ["file1.txt", "data/file2.txt"] ),
    ]

    # Expected combinations
    expected_combinations = [
        {'simulationID': 1, ('model1','parameter','p2'): 1, ('model1','parameter','s2'): 0.1, ('model2','parameter','pC'): "file1.txt"},
        {'simulationID': 2, ('model1','parameter','p2'): 1, ('model1','parameter','s2'): 0.1, ('model2','parameter','pC'): "data/file2.txt"},
        {'simulationID': 3, ('model1','parameter','p2'): 1, ('model1','parameter','s2'): 0.2, ('model2','parameter','pC'): "file1.txt"},
        {'simulationID': 4, ('model1','parameter','p2'): 1, ('model1','parameter','s2'): 0.2, ('model2','parameter','pC'): "data/file2.txt"},
        {'simulationID': 5, ('model1','parameter','p2'): 2, ('model1','parameter','s2'): 0.1, ('model2','parameter','pC'): "file1.txt"},
        {'simulationID': 6, ('model1','parameter','p2'): 2, ('model1','parameter','s2'): 0.1, ('model2','parameter','pC'): "data/file2.txt"},
        {'simulationID': 7, ('model1','parameter','p2'): 2, ('model1','parameter','s2'): 0.2, ('model2','parameter','pC'): "file1.txt"},
        {'simulationID': 8, ('model1','parameter','p2'): 2, ('model1','parameter','s2'): 0.2, ('model2','parameter','pC'): "data/file2.txt"},
        {'simulationID': 9, ('model1','parameter','p2'): 3, ('model1','parameter','s2'): 0.1, ('model2','parameter','pC'): "file1.txt"},
        {'simulationID': 10, ('model1','parameter','p2'): 3, ('model1','parameter','s2'): 0.1, ('model2','parameter','pC'): "data/file2.txt"},
        {'simulationID': 11, ('model1','parameter','p2'): 3, ('model1','parameter','s2'): 0.2, ('model2','parameter','pC'): "file1.txt"},
        {'simulationID': 12, ('model1','parameter','p2'): 3, ('model1','parameter','s2'): 0.2, ('model2','parameter','pC'): "data/file2.txt"},
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
        ('model1', 'parameter', 's2', [0.1, 0.2] ),
        ('model2', 'parameter', 'pC', ["file1.txt", "data/file2.txt"] ),
    ]

    # Expected combinations
    expected_combinations = [
        {'simulationID': 1, ('model1','parameter','p2'): 1, ('model1','parameter','s2'): 0.1, ('model2','parameter','pC'): "file1.txt"},
        {'simulationID': 2, ('model1','parameter','p2'): 2, ('model1','parameter','s2'): 0.2, ('model2','parameter','pC'): "data/file2.txt"}
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
        ('model1', 'parameter', 's2', [0.1, 0.2] ),
        ('model2', 'parameter', 'pC', ["file1.txt", "data/file2.txt"] ),
    ]
    with pytest.raises(ValueError):
        parallel_scenarios._generate_combinations_from_removed_items(items, align=True)


# Test _get_list_subset

# Case 1: More simulations than MPI processes, divides evenly
def test_get_list_subset_even_division():
    simulations = list(range(8))  # [0..7]
    comm_size = 4  # 4 MPI ranks
    expected = {
        0: [0, 1],
        1: [2, 3],
        2: [4, 5],
        3: [6, 7]
    }

    for rank in range(comm_size):
        result = parallel_scenarios._get_list_subset(simulations, rank, comm_size)
        assert result == expected[rank], f"Rank {rank} got {result}, expected {expected[rank]}"

# Case 2: More simulations than MPI processes, not divisible evenly
def test_get_list_subset_uneven_division():
    simulations = list(range(10))  # 10 sims
    comm_size = 3  # 3 MPI ranks
    # Base distribution: each gets floor(10/3)=3 items
    # Leftovers: 10 % 3 = 1 -> rank 0 gets one extra (last one)
    expected = {
        0: [0, 1, 2, 9],  # + leftover (last element)
        1: [3, 4, 5],
        2: [6, 7, 8],
    }

    for rank in range(comm_size):
        result = parallel_scenarios._get_list_subset(simulations, rank, comm_size)
        assert result == expected[rank], f"Rank {rank} got {result}, expected {expected[rank]}"

# Case 3: More MPI processes than simulations
def test_get_list_subset_more_processes_than_sims():
    simulations = list(range(3))
    comm_size = 5
    expected = {
        0: [0],
        1: [1],
        2: [2],
        3: [],
        4: []
    }

    for rank in range(comm_size):
        result = parallel_scenarios._get_list_subset(simulations, rank, comm_size)
        assert result == expected[rank], f"Rank {rank} got {result}, expected {expected[rank]}"

# Case 4: Edge case — empty simulation list
def test_get_list_subset_empty_list():
    simulations = []
    comm_size = 4
    for rank in range(comm_size):
        result = parallel_scenarios._get_list_subset(simulations, rank, comm_size)
        assert result == [], f"Rank {rank} should get empty list, got {result}"


# Test _generate_scenario

def test_generate_scenario(scenario, scenario_multiparams_removed):
    """Test that parameters are correctly injected and simulationID appended to monitor file."""
    item_to_add = {
        'simulationID': 5,
        ('model1', 'parameter', 'p3'): 0.42,
        ('model2', 'parameter', 'paramX'): "updated_text.txt"
    }

    new_config = parallel_scenarios._generate_scenario(scenario_multiparams_removed, item_to_add)

    # 1. align_parameters should be removed
    assert 'align_parameters' not in new_config['scenario']

    # 2. Ensure other scenario metadata is unchanged
    for key in ['name', 'start_time', 'end_time', 'time_resolution']:
        assert new_config['scenario'][key] == scenario['scenario'][key]

    # 3. model1 parameters: existing + injected p3
    model1 = next(m for m in new_config['models'] if m['name'] == 'model1')
    assert model1['parameters']['p1'] == 10
    assert model1['parameters']['p2'] == 7
    assert model1['parameters']['p3'] == 0.42  # newly injected

    # 4. model2 parameters: existing + injected pC
    model2 = next(m for m in new_config['models'] if m['name'] == 'model2')
    assert model2['parameters']['pA'] == 42
    assert model2['parameters']['pB'] == 'text'
    assert model2['parameters']['paramX'] == "updated_text.txt"

    # 5. Model states should be identical to base scenario
    base_model1 = next(m for m in scenario['models'] if m['name'] == 'model1')
    base_model2 = next(m for m in scenario['models'] if m['name'] == 'model2')
    assert model1['states'] == base_model1['states']
    assert model2['states'] == base_model2['states']

    # 6. monitor file updated
    assert new_config['monitor']['file'] == './out_tutorial4_parallel_5.csv'

    # 7. Other monitor fields should be identical to base scenario
    assert new_config['monitor']['items'] == scenario['monitor']['items']

    # 8. Connections should be identical to base scenario
    assert new_config['connections'] == scenario['connections']


# Test _write_lookup_table

def test_write_lookup_table(tmp_path):
    """Test that _write_lookup_table writes a correct CSV file with tuple keys."""
    filepath = tmp_path / "lookup.csv"

    # Mock input
    simulation_list = [
        {
            'simulationID': 1,
            ('ModelA', 'parameter', 'param1'): 10,
            ('ModelB', 'parameter', 'param2'): 20,
        },
        {
            'simulationID': 2,
            ('ModelA', 'parameter', 'param1'): 15,
            ('ModelB', 'parameter', 'param2'): 25,
        },
    ]

    # Write CSV
    parallel_scenarios._write_lookup_table(simulation_list, str(filepath))

    # Assert file exists
    assert filepath.exists(), "CSV file was not created"

    # Read back file and verify contents
    with open(filepath, newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)

    # Check header (simulationID + sorted tuple keys)
    expected_header = [
        "simulationID",
        "ModelA.parameter.param1",
        "ModelB.parameter.param2"
    ]
    assert rows[0] == expected_header

    # Check first data row
    assert rows[1] == ["1", "10", "20"]
    # Check second data row
    assert rows[2] == ["2", "15", "25"] 