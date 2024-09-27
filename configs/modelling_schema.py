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
                Optional("parameters"): And(dict, len, error="if 'parameters' is used, it must contain at least one key-value pair"),
                Optional("states"): And(dict, len, error="if 'states' is used, it must contain at least one key-value pair"),
                Optional("triggers"): And(list, len, error="if 'trigger' is used, it must contain at least one key-value pair"),
                Optional("scenario_data"): And(str, len, error="you must provide a scenario data file if using 'scenario_data'"),
            } ]
        ),
        "connections":  Schema( # a sequence of mappings
            [{
                "from": And(str, len),
                "to": And(str, len),
            }]
        ),
        "monitor":  And(list, len, error="you must provide an item to monitor"),
    }
)


# TODO: Write a more rubust validator for the monitor section
# Any input, output, or state declared in the monitor section must be declared in the models section

# TODO: Write a more rubust validator for connections section
# Any input, output, or state declared in the connection section must be declared in the models section

# TODO: Write a validator for the scenario data file. It should check that the fiel exists 
# TODO: write a validator for triggers. It should check that the trigger is a valid input, output, or state. 
