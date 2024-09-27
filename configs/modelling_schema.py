"""
A schema for validating a simulation configuration file
in the Illuminaotr. 
"""
from typing import Any, Dict
from schema import Schema, And, Use, Regex, Optional, SchemaError
import datetime

# format: YYYY-MM-DD HH:MM:SS"
valid_start_time = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'


class ScenarioSchema(Schema):
    """
    A schema for validating the scenario section of the simulation configuration file.
    """
    def validate(self, data, _is_scenario_schema=True): # _is_scenario_schema is a flag to limit validation of the scenario schema
        data = super(ScenarioSchema, self).validate(data, _is_scenario_schema=False)
        
        if _is_scenario_schema and data.get("start_time", None) and data.get("end_time", None):
            # convert strings to datetime objects
            start_time_ = datetime.datetime.strptime(data["start_time"], "%Y-%m-%d %H:%M:%S")
            end_time_ = datetime.datetime.strptime(data["end_time"], "%Y-%m-%d %H:%M:%S")
            if start_time_ >= end_time_:
                raise SchemaError("End time cannot be less than or equal to the start time.")
        return data

# Define the schema for the simulation configuration file
schema = Schema( # a mapping of mappings
            {
                "scenario": ScenarioSchema(
                    {
                    "name": And(str, len),
                    "start_time": Regex(valid_start_time, error="Invalid start_time format. Must be in the format: YYYY-MM-DDTHH:MM:SS"),
                    "end_time": Regex(valid_start_time, error="Invalid end_time format. Must be in the format: YYYY-MM-DDTHH:MM:SS"),
                    }
        ),
        "models": Schema( # a sequence of mappings
            [ {
                "name": And(str, len),
                "type": And(str, len),
                "inputs": And(dict, len, error="if 'inputs' is used, it must contain at least one key-value pair"),
                "outputs": And(dict, len, error="if 'outputs' is used, it must contain at least one key-value pair"),
                Optional("parameters"): And(list, lambda l: all(isinstance(x, str) for x in l)),
                Optional("states"): And(list, lambda l: all(isinstance(x, str) for x in l)),
                Optional("scenario_data"): And(str, len),
            } ]
        ),
        "connections":  Schema( # a sequence of mappings
            [{
                "from": And(str, len),
                "to": And(str, len),
                "data": And(list, lambda l: all(And(isinstance(x, tuple), len(x) == 2 ) for x in l)),
            }]
        ),
        "monitor":  Schema( # a sequence of mappings
            [{
                "name": And(str, len),
                Optional("inputs"):  And(list, lambda l: all(And(isinstance(x, str)) for x in l)),
                Optional("outputs"):  And(list, lambda l: all(And(isinstance(x, str)) for x in l)),
                Optional("states"): And(list, lambda l: all(And(isinstance(x, str)) for x in l)),
            }]
        )
    }
)


# validades monitor contains at least one set of inputs, outputs, or states
def at_least_one_set(d):
    return any(d.get(key) for key in ["inputs", "outputs", "states"])


def validate_monitor(data) -> bool:
    for item in data.get("monitor", []):
        print(item)
        if not at_least_one_set(item):
            raise SchemaError("At least one of 'inputs', 'outputs', or 'states' must be set in each monitor item.")    
    return True
