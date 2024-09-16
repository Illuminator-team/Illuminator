import mosaik_api
import pandas as pd
from illuminator_battery import IlluminatorBattery

META = {
    'type': 'hybrid',
    'models': {
        'BatteryModel': {
            'public': True,
            'params': ['power_flow_max', 'soc_min', 'soc_max'],
            'attrs': ['power_flow', 'soc'],
            'trigger': ['delta'],
        },
    },
}

class Battery(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META) # Required by mosaik API
        self.eid_prefix = 'battery_' # Prefix for entity IDs
        self.entities = {} # Dict with all entities (agents) by their IDs
        self._cache = {} # Cache for the last output of each entity

    def init(self, sid, step_size):
        self.sid = sid # Store the scenario ID
        self.step_size = step_size # Store the step size
        return self.meta

    def create(self, num, model, inputs, outputs, parameters, states):
        entities = []
        for i in range(num): # Create `num` entities
            eid = f'{self.eid_prefix}{i}' # Unique ID for the entity
            model_instance = IlluminatorBattery( # Create a new battery model instance
                inputs=inputs,
                outputs=outputs,
                parameters=parameters,
                states=states
            )
            self.entities[eid] = model_instance # Store the model instance, not the same as the entities list
            entities.append({'eid': eid, 'type': model}) # Add the entity to the list of entities
        return entities

    def step(self, time, inputs):
        # Process inputs and step the battery model
        for eid, entity_inputs in inputs.items():
            battery = self.entities[eid]

            # Set the inptus of the battery model
            battery.inputs['requested_power_flow'] = entity_inputs['requested_power_flow']

            # Perform a simulation step
            battery.step()

            # Update outputs
            self.entities[eid].outputs['effective_power_flow'] = battery.outputs['effective_power_flow']
            self.entities[eid].outputs['soc'] = battery.outputs['soc']

        return time + self.step_size

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            for attr in attrs:
                if attr in self._cache[eid]:
                    data[eid][attr] = self._cache[eid][attr]
        return data


def main():
    mosaik_api.start_simulation(IlluminatorBattery(), 'Battery Simulator')


if __name__ == "__main__":
    main()
