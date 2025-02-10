"""
A schema for validating a simulation configuration file (YAML)
in the Illuminator. 
"""

import datetime
import re
import os
import json as json_module
from ruamel.yaml import YAML
from schema import Schema, And, Use, Regex, Optional, SchemaError, SchemaUnexpectedTypeError

# valid format for start and end times: YYYY-MM-DD HH:MM:SS"
valid_start_time = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'
# Ip versions 4 and 6 are valid
ipv4_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
# monitor and connections sections enforce a format such as 
# <model>.<input/output/state>
valid_model_item_format = r'^\w+\.\w+$'
# valid_model_item_format = r'^([\w-]+\.?)+$' # This is kept here as an alternative. I believe this might be useful later on



def load_config_file(config_file: str, json:bool=False) -> dict | str:
    """Returns the content of an scenerio file written as YAML after
    validating its content against the Illuminator's Schema.

    Parameters
    ----------
    config_file : str
        The path to the YAML configuration file.
    json : bool
        If True, the content of the configuration file is returned as a JSON string.

    Returns
    -------
    dict
        The content of the configuration file as a dictionary.
    """

    try:
        with open(config_file, 'r', encoding='utf-8') as _file:
            yaml = YAML(typ='safe')
            data = yaml.load(_file)
    except FileNotFoundError:
        print(f"Error: The file {config_file} was not found.")
        return None
    
    try:
        valid_data = schema.validate(data)
    except SchemaUnexpectedTypeError as exc:
        print(f"Error while parsing YAML file. \n Are you passing a file written in YAML?: {exc}")
        return None
  
    if json:
        return json_module.dumps(valid_data, indent=4)
    
    return valid_data


def validate_model_item_format(items: list) -> list:
    """
    Validates the monitor section of the simulation configuration file, as
    follows the format <model>.<item>
    """
    pattern = re.compile(valid_model_item_format)
    for item in items:
        if not pattern.match(item):
            raise SchemaError(f"Invalid format for monitor item: {item}. "
                              "Must be in the format: <model>.<item>")
    return items


def validate_file_path(file_path: str) -> str:
    """
    Validates that a file path exists.
    """
    if not os.path.exists(file_path):
        raise SchemaError(f"File path does not exist: {file_path}")
    return file_path


def validate_directory_path(file_path: str) -> str:
    """
    Validates that a  directory exists.
    """
    directory = os.path.dirname( os.path.abspath(file_path))
    print(directory)
    if not os.path.isdir(directory):
        raise SchemaError(f"Directory does not exist: {directory}")
    return file_path


class ScenarioSchema(Schema):
    """
    A schema for validating the scenario section of the simulation
    configuration file.
    """
    def validate(self, data, _is_scenario_schema=True):  # _is_scenario_schema
        # is a flag to limit validation of the scenario schema
        data = super(ScenarioSchema, self).validate(data,
                                                    _is_scenario_schema=False)
        
        if _is_scenario_schema and data.get("start_time", None) and \
                data.get("end_time", None):
            # convert strings to datetime objects
            start_time_ = datetime.datetime.strptime(data["start_time"],
                                                     "%Y-%m-%d %H:%M:%S")
            end_time_ = datetime.datetime.strptime(data["end_time"],
                                                   "%Y-%m-%d %H:%M:%S")
            if start_time_ >= end_time_:
                raise SchemaError("End time cannot be less than or equal to "
                                  "the start time.")
        return data


# Define the schema for the simulation configuration file
schema = Schema(  # a mapping of mappings
            {
                "scenario": ScenarioSchema(
                    {
                        "name": And(str, len),
                        "start_time": Regex(valid_start_time, error="Invalid "
                                            "start_time format. Must be in "
                                            "the format: YYYY-MM-DDTHH:MM:SS"),
                        "end_time": Regex(valid_start_time, error="Invalid "
                                          "end_time format. Must be in the"
                                          "format: YYYY-MM-DDTHH:MM:SS"),
                        Optional("time_resolution"): And(int, lambda n: n > 0,
                                                  error="time resolution must be a "
                                                  "positive integer"),
                    }
                ),
                "models": Schema(  # a sequence of mappings
                    [{
                        "name": And(str, len),
                        "type": And(str, len),
                        Optional("inputs"): And(dict, len, error="if 'inputs' is used,"
                                      "it must contain at least one key-value "
                                      "pair"),
                        Optional("outputs"): And(dict, len, error="if 'outputs' is used,"
                                       " it must contain at least one "
                                       "key-value pair"),
                        Optional("parameters"): And(dict,
                                                    len,
                                                    error="if 'parameters' is used, it must contain at least one key-value pair"),
                        Optional("states"): And(dict, len, error="if 'states' is used, it must contain at least one key-value pair"),
                        Optional("triggers"): And(list, len, error="if 'trigger' is used, it must contain at least one key-value pair"),
                        Optional("connect"): Schema( # a mapping of mappings
                            {
                                "ip": Regex(ipv4_pattern, error="you must provide an IP address that matches versions IPv4 or IPv6"),
                                Optional("port"): And(int),
                            }
                            ),
                        Optional("time_step_size"): int,
            } ]
        ),
        "connections":  Schema( # a sequence of mappings
            [{
                "from": Regex(valid_model_item_format, error="Invalid format for 'from'. Must be in the format: <model>.<item>"),
                "to": Regex(valid_model_item_format, error="Invalid format for 'to'. Must be in the format: <model>.<item>"),
                Optional("time_shifted", default=False): bool
            }]
        ),
        "monitor":  Schema(
            {
                Optional("file"): And(str, len, Use(validate_directory_path, error="Path for 'file' does not exists..."), error="you must provide a non-empty string for 'file'"),
                "items": And(list, len, Use(validate_model_item_format, error="Items in 'monitor' must have the format: <model>.<item>"), 
                        error="you must provide at least one item to monitor")
            }
        )
    }
)


# TODO: write a validator for model types. It should check that a model exist in the illuminator.models package
# We could generate a list of names in the models package and check that the model name is in that list.
# The list should be updates when new models are added to the package
# TODO: Write a more rubust validator for the monitor section
# Any input, output, or state declared in the monitor section must be declared in the models section
# TODO: Write a more rubust validator for connections section
# Any input, output, or state declared in the connection section must be declared in the models section
# TODO: write a validator for triggers. It should check that the trigger has been declared as input, output, or state. 
