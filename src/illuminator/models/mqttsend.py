import collections
import pandas as pd
import mosaik_api
import paho.mqtt.client as mqtt

META = {
    'type': 'hybrid',
    'models': {
        'MqttSend': {
            'public': True,
            'any_inputs': True,
            'params': ['mqtt_broker', 'mqtt_port', 'mqtt_topic'],
            'attrs': [],
        },
    },
}

class MqttSendModel(mosaik_api.Simulator):
    def __init__(self) -> None:
        """
        Inherits the Mosaik API Simulator class and is used for python based simulations.
        For more information properly inheriting the Mosaik API Simulator class please read their given documentation.

        ...

        Attributes
        ----------
        self.meta : dict
            Contains metadata of the control sim such as type, models, parameters, attributes, etc.. Created via gpcontrolSim's parent class.
        self.eid : string
            The prefix with which each entity's name/eid will start
        self.data : dict
            ???
        self._cache : ???
            ???
        """
        super().__init__(META)
        self.eid = None
        self.data = collections.defaultdict(lambda: collections.defaultdict(dict))
        self.mqtt_client = mqtt.Client()

    def init(self, sid:str, mqtt_broker:str='localhost', mqtt_port:int=1883, mqtt_topic:str='mosaik/data') -> dict:
        """
        Initialize the simulator with the ID `sid` and pass the `time_resolution` and additional parameters sent by mosaik.
        Because this method has an additional parameter `step_size` it is overriding the parent method init().

        ...

        Parameters
        ----------
        sid : str
            The String ID of the class (???)
        mqtt_broker : str
            ???
        mqtt_port : int
            The port value
        mqtt_topic : str
            ???

        Returns
        -------
        self.meta : dict
            The metadata of the class
        """
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port)

        return self.meta

    def create(self, num:int, model:str) -> list:
        """
        Create `num` instances of `model` using the provided `model_params`.

        ...

        Parameters
        ----------
        num : int
            The number of model instances to create.
        model : str
            `model` needs to be a public entry in the simulator's ``meta['models']``.
         
        Returns
        -------
        entities : list
            Return a list of dictionaries describing the created model instances (entities). 
            The root list must contain exactly `num` elements. The number of objects in sub-lists is not constrained::

            [
                {
                    'eid': 'eid_1',
                    'type': 'model_name',
                    'rel': ['eid_2', ...],
                    'children': [
                        {'eid': 'child_1', 'type': 'child'},
                        ...
                    ],
                },
                ...
            ]
        
        See Also
        --------
        The entity ID (*eid*) of an object must be unique within a simulator instance. For entities in the root list, `type` must be the same as the
        `model` parameter. The type for objects in sub-lists may be anything that can be found in ``meta['models']``. *rel* is an optional list of
        related entities; "related" means that two entities are somehow connect within the simulator, either logically or via a real data-flow (e.g.,
        grid nodes are related to their adjacent branches). The *children* entry is optional and may contain a sub-list of entities.
        """
        if num > 1 or self.eid is not None:
            raise RuntimeError('Can only create one instance of MqttSend.')

        self.eid = 'MqttSend'
        return [{'eid': self.eid, 'type': model}]

    def step(self, time:int, inputs:dict) -> int:
        """
        Perform the next simulation step from time `time` using input values from `inputs`

        ...

        Parameters
        ----------
        time : int
            A representation of time with the unit being arbitrary. Has to be consistent among 
            all simulators used in a simulation.

        inputs : dict
            Dict of dicts mapping entity IDs to attributes and dicts of values (each simulator has to decide on its own how to reduce 
            the values (e.g., as its sum, average or maximum)::

            {
                'dest_eid': {
                    'attr': {'src_fullid': val, ...},
                    ...
                },
                ...
            }

        Returns
        -------
        new_step : int
            Return the new simulation time, i.e. the time at which ``step()`` should be called again.
        """
        data = inputs.get(self.eid, {})
        for attr, values in data.items():
            for src, value in values.items():
                self.data[src][attr][time] = value
                self.mqtt_client.publish(self.mqtt_topic, payload=str(value))

        return time + 60  # Adjust the step time as necessary

    def finalize(self) -> None:
        """
        Disconnects the mqtt client object
        """
        self.mqtt_client.disconnect()
        print('Disconnected from MQTT broker')

if __name__ == '__main__':
    mosaik_api.start_simulation(MqttSendModel())
