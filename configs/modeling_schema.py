"""
A schema for validating a simulation configuration file
in the Illuminaotr. 
"""
from schema import Schema, And, Use, Regex, Optional, SchemaError

# format: YYYY-MM-DD HH:MM:SS"
valid_start_time = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'

# connection schema
connection = Schema(
       [ {
        "from": And(str, len),
        "to": And(str, len),
        "data": And(list, lambda l: all(And(isinstance(x, tuple), len(x) == 2 ) for x in l)),
    }   
    ]
)

# main schema
schema = Schema(
    {
        "scenario": And(str, len),
        "scenario_data": And(str, len),
        "start_time": Regex(valid_start_time, error="Invalid start time format. Must be in the format: YYYY-MM-DDTHH:MM:SS"),
        "end_time": And(Use(int), lambda n: n > 0),
        "nodes": And(list, lambda l: all(isinstance(x, dict) for x in l)), # nodes must be a sequence of mappings
        "connections": connection # connections must be a sequence of mappings
    }
)


