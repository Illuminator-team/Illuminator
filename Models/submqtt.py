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
    def __init__(self):
        super().__init__(META)
        self.time_resolution = None
        self.eid = None
        self.mqtt_client = mqtt.Client()
        self.attrs = []
        self.data_cache = {}
        self.modelname = None

    def init(self, sid, mqtt_broker='localhost', mqtt_port=1883, mqtt_topic='mosaik/data', time_resolution=60, attrs):
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

    def create(self, num, model):
        if num > 1 or self.eid is not None:
            raise RuntimeError('Can only create one instance of MqttReceiver.')

        self.eid = 'MqttReceiver'
        return [{'eid': self.eid, 'type': model}]

    def step(self, time, inputs):
        self.mqtt_client.loop(timeout=1.0)
        return time + self.time_resolution

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {attr: self.data_cache.get(attr, None) for attr in attrs}
        return data

    def on_message(self, client, userdata, message):
        data = message.payload.decode('utf-8')
        attr_name, attr_value = data.split(':')  # Assuming the message format is "attr_name:attr_value"

        if attr_name not in self.attrs:
            self.attrs.append(attr_name)

        self.data_cache[attr_name] = float(attr_value)

    def finalize(self):
        self.mqtt_client.disconnect()


def main():
    return mosaik_api.start_simulation(MqttReceiver(), 'mosaik-mqtt-receiver simulator')


if __name__ == "__main__":
    main()
