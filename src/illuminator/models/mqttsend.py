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
    def __init__(self):
        super().__init__(META)
        self.eid = None
        self.data = collections.defaultdict(lambda: collections.defaultdict(dict))
        self.mqtt_client = mqtt.Client()

    def init(self, sid, mqtt_broker='localhost', mqtt_port=1883, mqtt_topic='mosaik/data'):
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port)

        return self.meta

    def create(self, num, model):
        if num > 1 or self.eid is not None:
            raise RuntimeError('Can only create one instance of MqttSend.')

        self.eid = 'MqttSend'
        return [{'eid': self.eid, 'type': model}]

    def step(self, time, inputs):
        data = inputs.get(self.eid, {})
        for attr, values in data.items():
            for src, value in values.items():
                self.data[src][attr][time] = value
                self.mqtt_client.publish(self.mqtt_topic, payload=str(value))

        return time + 60  # Adjust the step time as necessary

    def finalize(self):
        self.mqtt_client.disconnect()
        print('Disconnected from MQTT broker')

if __name__ == '__main__':
    mosaik_api.start_simulation(MqttSendModel())
