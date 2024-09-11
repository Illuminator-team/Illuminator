"""
A schema for validating a simulation configuration file
in the Illuminaotr. 
"""
from schema import Schema, And, Use, Regex, Optional, SchemaError

# format: YYYY-MM-DD HH:MM:SS"
valid_start_time = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'

# Define the schema for the simulation configuration file
schema = Schema( # a mapping of mappings
            {
                "scenario": Schema(
                    {
                    "name": And(str, len),
                    "scenario_data": And(str, len),
                    "start_time": Regex(valid_start_time, error="Invalid start time format. Must be in the format: YYYY-MM-DDTHH:MM:SS"),
                    "end_time": And(Use(int), lambda n: n > 0),
                    }
        ),
        "nodes": Schema( # a sequence of mappings
            [ {
                "name": And(str, len),
                "model": And(str, len),
                "inputs": And(list, lambda l: all(isinstance(x, str) for x in l)),
                "outputs": And(list, lambda l: all(isinstance(x, str) for x in l)),
                "parameters": And(list, lambda l: all(isinstance(x, str) for x in l)),
                "states": And(list, lambda l: all(isinstance(x, str) for x in l)),
            } ]
        ),
        "connections":  Schema( # a sequence of mappings
            [{
                "from": And(str, len),
                "to": And(str, len),
                "data": And(list, lambda l: all(And(isinstance(x, tuple), len(x) == 2 ) for x in l)),
            }]
        )
    }
)


