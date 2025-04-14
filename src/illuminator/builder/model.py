from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import illuminator.engine as engine
from mosaik_api_v3 import Simulator

class SimulatorType(Enum):
    TIME_BASED = 'time-based'
    EVENT_BASED = 'event-based'
    HYBRID = 'hybrid'

# TOOD: IMPORTANT 
# each model file must provide a way to run it remotely. In the current implementation,
# that is achieved by including a the folloowing code on the simulator file:
# def main():
#     mosaik_api.start_simulation(eboilerSim(), 'eboiler Simulator')
# if __name__ == "__main__":
#     main()

@dataclass
class IlluminatorModel():
    """ A dataclass for defining the properties of a model in the Illuminator.

    Attributes
    ----------

    parameters: dict
        Properties of the object being modeled, e.g. material the object is
        made of.
    inputs: dict
        One or more name: value pairs to be regarded as inputs to the model.
        Inputs allow users to connect a model to other models.
    outputs: dict
        One or more name: value pairs to be regarded as outputs of the model.
        Outputs allow users to connect a model to other models.
    states: dict
        One or more 'parameters, inputs or outputs' and their initial value
        that are of interest for monitoring or logging during a simulation.
    triggers: list
        A flag [input's or output's name] that causes the `step` method to
        be called.Only relevant when a model is part of an event-based or
        hybrid simulator.
    simulator_type: SimulatorType
        The type of simulator that the model belongs to.
    time_step_size: int
        The time of each simulation step in seconds. Default 900.
    time: int
        The current time of the simulation.
    model_type: str
        A name for the class of model that is being defined. Default 'Model'.
    """

    parameters: Dict = field(default_factory=dict)    
    inputs: Optional[Dict] = field(default_factory=dict) 
    outputs: Dict = field(default_factory=dict)
    states: Dict = field(default_factory=dict)
    triggers: Optional[Dict] = field(default_factory=list)
    simulator_type: SimulatorType = SimulatorType.TIME_BASED
    time_step_size: int = 1   # This is closely related to logic in the step method. 
    # Currently, all models have the same time step size (15 minutes). 
    # This is a global setting for the simulation, not a model-specific setting.
    time: Optional[datetime] = None  # Shouldn't be modified by the user.
    model_type: Optional[str] = "Model" 
    

    def __post_init__(self):
        self._validate_attributes()
        self._validate_triggers()
        # self.validate_simulator_type()
    
    @property
    def simulator_meta(self) -> dict:
        """Returns the metadata required by the mosaik API"""
        
        meta = {
            'type': self.simulator_type.value,
            'models': {
                self.model_type: { # This must be the name of he model 
                    'public': True,
                    'params': list(self.parameters.keys()),
                    'attrs': list(self.inputs.keys()) + list(self.outputs.keys()) + list(self.states.keys())
                }
            }}
        return meta

    def _validate_attributes(self):
        """Check if items in 'states' are also in 'outputs'"""
        # Find overlapping keys
        duplicate_keys = set(self.outputs.keys()) & set(self.states.keys())

        # Raise an error if duplicates exist
        if duplicate_keys:
            raise ValueError(f"Duplicate attribute names found in both outputs and states: {', '.join(duplicate_keys)}")
        
        

    def _validate_triggers(self):
        """Check if triggers are in inputs or outputs"""
        for trigger in self.triggers:
            if trigger not in self.inputs and trigger not in self.outputs:
                raise ValueError(f"Trigger: {trigger} must be either an input "
                                 "or an output")

    def _validate_simulator_type(self):
        """Check if triggers are defined for time-based and event-based
        simulations only
        """
        if self.simulator_type == SimulatorType.TIME_BASED and self.triggers:
            raise ValueError("Triggers are not allowed in time-based "
                             "simulators")

        if self.simulator_type == SimulatorType.EVENT_BASED and \
                not self.triggers:
            raise ValueError("Triggers are required in event-based simulators")


# COTINUE FROM HERE
# need to find a convenient an easy way to define new models
# Ideas:
# - add model definition as a method of the ModelConstructor class. will it work?

class ModelConstructor(ABC, Simulator):
    """A common interface for constructing models in the Illuminator"""
    parameters: Dict = {}
    inputs: Dict = {}
    outputs: Dict = {}
    states: Dict = {}
    time_step_size: int = 1

    # TODO: make this work
    # def multipleModelDecorator(self, function, **kwargs):
    #     for eid, entity in self.entities.items():
    #         function(entity, kwargs)

    def __init__(self, **kwargs) -> None:
        #model: IlluminatorModel
        model_vals = engine.current_model
        
        self.parameters = model_vals.get('parameters', self.parameters)
        self.inputs = model_vals.get('inputs', self.inputs)
        self.outputs = model_vals.get('outputs', self.outputs)
        self.states = model_vals.get('states', self.states)
        self.time_step_size = model_vals.get('time_step_size', self.time_step_size)
        self.model_type = model_vals.get('type', 'Model')

        model = IlluminatorModel(
                parameters=self.parameters, # get the yaml values or the default from the model
                inputs=self.inputs,
                outputs=self.outputs,
                states=self.states,
                model_type=self.model_type,
                time_step_size=self.time_step_size
            )
        super().__init__(meta=model.simulator_meta)
        self._model = model
        self.model_entities = {}
        self.time = 0  # time is an integer without a unit
        self.sid = None
        self.time_resolution = None

    @abstractmethod
    def step(self, time:int, inputs:dict=None, max_advance:int=None) -> int:
        """Defines the computations that need to be performed in each
        simulation step

        Parameters
        ----------
        time: int
            The current time of the simulation.
        inputs: dict
            The inputs to the model.
        max_advance: int
            Time until the simulator can safely advance its internal time without creating a causality error.
            Optional in most cases.


        Returns
        -------
        int
            The new time of the simulation.

        """
        pass


    def init(self, sid, time_resolution=1, **sim_params):  # can be use to update model parameters set in __init__
        # TODO: from engine.py, time_resolution is never passed. hint: check engine self.start call

        print(f"running extra init")
        # This is the standard Mosaik init method signature
        self.sid = sid
        self.time_resolution = time_resolution

        # This bit of code is unused.
        # Assuming sim_params is structured as {'sim_params': {model_name: model_data}}
        sim_params = sim_params.get('sim_params', {})
        if len(sim_params) != 1:
            raise ValueError("Expected sim_params to contain exactly one model.")

        # # Extract the model_name and model_data
        # self.model_name, self.model_data = next(iter(sim_params.items()))
        # self.model = self.load_model_class(self.model_data['model_path'], self.model_data['model_type'])
        return self._model.simulator_meta
    
    def create(self, num:int, model:str, **model_params) -> List[dict]: # This change is mandatory. It MUST contain num and model as parameters otherwise it receives an incorrect number of parameters
        """Creates an instance of the model"""
        new_entities = [] # See below why this was created
        for i in range(num): # this seems ok
            eid = f"{self._model.simulator_type.value}_{i}" # this seems ok
            self.model_entities[eid] = self._model # this seems fine
        # return list(self.model_entities.keys()) # I removed this bit for now. Create is expected to return a list of dictionaries
            new_entities.append({'eid': eid, 'type': model})  # So basically, like this. Later on we can look into other alternatives if needed.
        return new_entities
    
    def current_time(self): 
        """Returns the current time of the simulation"""
        # TODO: implement this method
        return

    def get_data(self, outputs) -> Dict: # TODO remove the print statements here
        """
        Gets data from model outputs based on requested attributes. Used by MOSAIK.

        Parameters
        ----------
        outputs : dict
            Dictionary mapping entity IDs to lists of requested output attributes
            
        Returns
        -------
        data : dict
            Dictionary containing the requested output values for each entity
        """
        data = {}
        # print(f"Here are your outputs: {outputs}")
        # for eid, attrs in self._model.outputs.items():
        for eid, attrs in outputs.items():
            # print(f"eid: {eid}, attrs:{attrs}")
            # print(f"self.model_entities: {self.model_entities}")
            model_instance = self.model_entities[eid]
            data[eid] = {}
            for attr in attrs:
                if attr in model_instance.outputs:
                    data[eid][attr] = model_instance.outputs[attr]
                elif attr in model_instance.states:
                    data[eid][attr] = model_instance.states[attr]
                elif attr in model_instance.inputs:
                    raise RuntimeError(f"'{attr}' is an input of {self.sid}.{eid}, connection reversed?")
                else:
                    raise RuntimeError(f"{self.sid}.{eid} does not have '{attr}' as input, output or state")
            # print(f"data: {data}")
        return data
    
    
    def get_state(self, attr):
        """
        Gets the current value of a state attribute.

        Parameters
        ----------
        attr : str
            Name of the state attribute to retrieve
            
        Returns
        -------
        value : Any
            The current value of the requested state attribute
        """
        if attr in self._model.states:
            if isinstance(self._model.states[attr], dict):  # in the case it was prepared for a connection previously
                return self._model.states[attr]['value']
            
            # TODO instead of doing this, convert all initial values to the connection format somewhere early on
            else: # in the case it was set by an initital value
                return self._model.states[attr]
            return self._model.states[attr]
        else:
            raise RuntimeError(f"simulator {self.sid} does not have '{attr}' as state")

    
    def set_states(self, states):
        """
        Sets state values for the model.

        Parameters
        ----------
        states : dict
            Dictionary containing state names and their values to be set
            
        Returns
        -------
        None
            This method does not return anything
        """
        for attr, value in states.items():
            if attr in self._model.states:
                self._model.states[attr] ={'message_origin': 'state', 'value': value}
            else:
                raise RuntimeError(f"simulator {self.sid} does not have '{attr}' as state")


    def set_outputs(self, outputs):
        """
        Sets output values for the model.

        Parameters
        ----------
        outputs : dict
            Dictionary containing output names and their values to be set
            
        Returns
        -------
        None
            This method does not return anything
        """
        for attr, value in outputs.items():
            if attr in self._model.outputs:
                self._model.outputs[attr] = {'message_origin': 'output', 'value': value}
            else:
                raise RuntimeError(f"simulator {self.sid} does not have '{attr}' as output")


    def unpack_inputs(self, inputs):
        """
        Unpacks input values from connected simulators and processes them based on their message origin.

        Parameters
        ----------
        inputs : dict
            Dictionary containing input values from connected simulators with their message origins
            
        Returns
        -------
        data : dict
            Dictionary containing processed input values, summed for outputs or single values for states
        """
        data = {}
        for attrs in inputs.values():
            for attr, sources in attrs.items():
                messages = list(sources.values())
                if not all(isinstance(message, dict) and 'message_origin' in message for message in messages):
                    raise RuntimeError(f"All messages sent over connections must have an attribute 'message_origin'. Connection: from: {sources}, to: {self.sid},  messages {messages}, input {attr}, make sure to use set_states or set_outputs() and set_states()")
                
                # check if all connections are with the same type, either output (physical) or state (data)
                if not all(message['message_origin'] == messages[0]['message_origin'] for message in messages):
                    raise RuntimeError(f"All values must have the same type: values: {messages}, input {attr}")

                # if the attribute is coming from a connection with an output
                if messages[0]['message_origin'] == 'output':
                    data[attr] = sum(message['value'] for message in messages)
                
                # if the attribute is coming from a connection with a state
                elif messages[0]['message_origin'] == 'state':
                    if len(messages) > 1:
                        data[attr] = [message['value'] for message in messages]
                    else:
                        data[attr] = messages[0]['value']

                # if not coming from output nor from state
                else:
                    raise RuntimeError(f"Connection coming from {messages[0]['message_origin']} not implemented yet")
        return data

if __name__ == "__main__":

    pass