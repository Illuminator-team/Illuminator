"""
Mosaik interface for the example simulator.
Example from tutorial: https://mosaik.readthedocs.io/en/latest/tutorials/examplesim.htmldd
"""

import mosaik_api
import example_model


"""
tells mosaik which time paradigm it follows (time-based, event-based, or hybrid), 
which models our simulator implements and which parameters and attributes it has
"""

# Define time paradigm and models in a simulation
meta_data = {
    'type': 'hybrid',
    'models': {
        'ExampleModel': {
            'public': True,
            'params': ['init_val'], # define in __init__ # must be parameters in Simulator.create()
            'attrs': ['delta', 'val'], # attributes in MyModel.__init__ 
            'trigger': ['delta'],
        },
    },
}
         
# Create instances of the model
model = example_model.MyModel(init_val=42)

print(model.val)
print(model.delta)


################## Simulator ##################
# define a simulator class that implements the mosaik API

class ExampleSimulator(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(meta_data)
        self.eid_prefix = 'MyModel_' # prefix for entity IDs (entities are instances of MyModel)
        # self.eid = 0
        self.models = {}
        self.entities = {}
        self.time = 0

    def init(self, sid, time_resolution, eid_prefix=None):
        # it will be called when calling world.start

        if float(time_resolution) != 1.:
            raise ValueError('ExampleSim only supports time_resolution=1., but'
                                ' %s was set.' % time_resolution)
        if eid_prefix is not None:
            self.eid_prefix = eid_prefix
        return self.meta

    def create(self, num, model, init_val): # addional params must be listed in meta_data.params
        # called in order to initialize a number of simulation model instances (entities) within that simulator.

        next_eid = len(self.entities)
        entities = []

        for i in range(next_eid, next_eid + num):
            # Uses the custom model 
            model_instance = example_model.MyModel(init_val)
            eid = '%s%d' % (self.eid_prefix, i)
            self.entities[eid] = model_instance
            entities.append({'eid': eid, 'type': model})

        return entities
    

    
    def step(self, time, inputs, max_advance):
        # tells your simulator to perform a simulation step
        self.time = time
        # Check for new delta and do step for each model instance:
        for eid, model_instance in self.entities.items():
            if eid in inputs:
                attrs = inputs[eid]
                for attr, values in attrs.items():
                    new_delta = sum(values.values())
                model_instance.delta = new_delta

            model_instance.step()

        return time + 1  # Step size is 1 second
    
    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            model = self.entities[eid]
            data['time'] = self.time
            data[eid] = {}
            for attr in attrs:
                if attr not in self.meta['models']['ExampleModel']['attrs']:
                    raise ValueError('Unknown output attribute: %s' % attr)
                
                # get model.val or model.delta
                data[eid][attr] = getattr(model, attr)
        return data


def main():
    return mosaik_api.start_simulation(ExampleSimulator())


# Make the simulator executable
if __name__ == '__main__':
    main()