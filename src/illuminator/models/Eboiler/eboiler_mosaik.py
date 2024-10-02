import mosaik_api
#import Eboiler.eboiler_model as eboiler_model
try:
    import Models.Eboiler.eboiler_model as eboiler_model
except ModuleNotFoundError:
    import eboiler_model_old as eboiler_model
else:
    import Models.Eboiler.eboiler_model as eboiler_model

import pandas as pd

META = {
    'type': 'event-based',

    'models': {
        'eboilermodel': {
            'public': True,
            'params': ['sim_start', 'eboiler_set'],
            'attrs': ['eboiler_id','eboiler_dem','e_consumed',
                      'q_gen','standby_loss','e_consumed'],
            'trigger': [],
        },
    },
}


class eboilerSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'eboiler_'  # every entity that we create will start with 'wind_'
        self.entities = {}  # we store the model entity of our technology model
        self._cache = {}  # used in the step function to store the values after running the python model of the technology
        self.time = 0
        # self.start_date = None

    # the following API call is will be called only once when we initiate the model in the scenario file.
    # we can use this to pass additional initialization tasks

    def init(self, sid, time_resolution):
        self.time_resolution = time_resolution
        return self.meta

    def create(self, num, model, sim_start, **model_params):
        self.start = pd.to_datetime(sim_start)
        entities = []

        for i in range(num):
            eid = '%s%d' % (self.eid_prefix, i)
            model_instance = eboiler_model.eboiler_python(**model_params)
            self.entities[eid] = model_instance
            entities.append({'eid': eid, 'type': model})
        return entities

    def step(self, time, inputs, max_advance):
        self.time = time
        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution,
                                     unit='seconds'))  # timedelta represents a duration of time
        print('from e-boiler %%%%%%%%%%%', current_time)

        for eid, attrs in inputs.items():

            for attr, vals in attrs.items():
                self._cache[eid] = self.entities[eid].demand(list(vals.values())[0])
        return None

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            for attr in attrs:
                if attr == 'eboiler_dem':
                    data[eid][attr] = self._cache[eid]['eboiler_dem']
                elif attr == 'q_gen':
                    data[eid][attr] = self._cache[eid]['q_gen']
                elif attr == 'standby_loss':
                    data[eid][attr] = self._cache[eid]['standby_loss']
                elif attr == 'e_consumed':
                    data[eid][attr] = self._cache[eid]['e_consumed']
        return data
def main():
    mosaik_api.start_simulation(eboilerSim(), 'eboiler Simulator')
    
if __name__ == "__main__":
    main()
