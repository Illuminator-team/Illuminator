import mosaik_api
import paho.mqtt.client as mqtt

META = {
    'models': {
        'MqttReceiver': {
            'public': True,
            'params': ['mqtt_broker', 'mqtt_port', 'mqtt_topic'],
            'attrs': [],
        },
    },
}


class MqttReceiver(mosaik_api.Simulator):
    def __init__(self) -> None:
        """
        Inherits the Mosaik API Simulator class and is used for python based simulations.
        For more information properly inheriting the Mosaik API Simulator class please read their given documentation.

        ...

        Attributes
        ----------
        self.meta : dict
            Contains metadata of the control sim such as type, models, parameters, attributes, etc.. Created via gpcontrolSim's parent class.
        self.time_resolution : ???
            ???
        self.eid : string
            The prefix with which each entity's name/eid will start
        self.mqtt_client : ???
            ???
        self.attrs : list
            ???
        self.data_cache : dict
            ???
        self.modelname : ???
            ???
        """
        super().__init__(META)
        self.time_resolution = None
        self.eid = None
        self.mqtt_client = mqtt.Client()
        self.attrs = []
        self.data_cache = {}
        self.modelname = None

    def init(self, sid:str, mqtt_broker:str='localhost', mqtt_port:int=1883, mqtt_topic:str='mosaik/data', time_resolution:int=60, attrs:list) -> dict:
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
            ???
        mqtt_topic : str
            ???
        time_resolution : float
            ???
        attrs : list
            ???
        
        Returns
        -------
        self.meta : dict
            The metadata of the class
        """
        self.time_resolution = time_resolution
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic
        self.modelname = mqtt_topic.split('/')[-1]

        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port)
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.subscribe(self.mqtt_topic)

        for i, attr in enumerate(attrs):
            try:
                # Try stripping comments
                attr = attr[:attr.index('#')]
            except ValueError:
                pass
            attrs[i] = attr.strip()
        self.attrs = attrs


        self.meta['models']['MqttReceiver'] = {
            'public': True,
            'params': [],
            'attrs': self.attrs,
        }

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
            raise RuntimeError('Can only create one instance of MqttReceiver.')

        self.eid = 'MqttReceiver'
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
        self.mqtt_client.loop(timeout=1.0)
        return time + self.time_resolution

    def get_data(self, outputs:dict) -> dict:
        """
        Return the data for the requested attributes in `outputs`
        
        ...

        Parameters
        ----------
        outputs : dict 
            Maps entity IDs to lists of attribute names whose values are requested::

            {
                'eid_1': ['attr_1', 'attr_2', ...],
                ...
            }

        Returns
        -------
        data : dict
            The return value is a dict of dicts mapping entity IDs and attribute names to their values::

            {
                'eid_1: {
                    'attr_1': 'val_1',
                    'attr_2': 'val_2',
                    ...
                },
                ...
                'time': output_time (for event-based sims, optional)
            }

        See Also
        --------
        Time-based simulators have set an entry for all requested attributes, whereas for event-based and hybrid simulators this is optional (e.g.
        if there's no new event). Event-based and hybrid simulators can optionally set a timing of their non-persistent output attributes via a *time* entry, which is valid
        for all given (non-persistent) attributes. If not given, it defaults to the current time of the step. Thus only one output time is possible
        per step. For further output times the simulator has to schedule another self-step (via the step's return value).
        """
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {attr: self.data_cache.get(attr, None) for attr in attrs}
        return data

    def on_message(self, client, userdata, message) -> None:
        """
        Description

        ...

        Parameters
        ----------
        client : ???
            ???
        userdata : ???
            ???
        message : ???
            ???
        """
        data = message.payload.decode('utf-8')
        attr_name, attr_value = data.split(':')  # Assuming the message format is "attr_name:attr_value"

        if attr_name not in self.attrs:
            self.attrs.append(attr_name)

        self.data_cache[attr_name] = float(attr_value)

    def finalize(self) -> None:
        """
        Disconnects the mqtt client object
        """
        self.mqtt_client.disconnect()


def main():
    return mosaik_api.start_simulation(MqttReceiver(), 'mosaik-mqtt-receiver simulator')


if __name__ == "__main__":
    main()
