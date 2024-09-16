import mosaik_api
try:
    import Models.H2demand.h2demand_model as h2demand_model
except ModuleNotFoundError:
    import h2demand_model as h2demand_model
else:
    import Models.H2demand.h2demand_model as h2demand_model

import pandas as pd

META = {
    'type': 'event-based',

    'models': {
        'h2demandmodel': {
            'public': True,
            'params': ['sim_start', 'houses'],
            'attrs': ['h2demand_id','h2demand_dem','h2demand'],
            'trigger': [],
        },
    },
}


class h2demandSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'h2demand_'
        self.entities = {}
        self._cache = {}
        self.time = 0


    def init(self, sid, time_resolution):
        self.time_resolution = time_resolution
        return self.meta

    def create(self, num, model, sim_start, **model_params):
        self.start = pd.to_datetime(sim_start)
        entities = []

        for i in range(num):
            eid = '%s%d' % (self.eid_prefix, i)
            model_instance = h2demand_model.h2demand_python(**model_params)
            self.entities[eid] = model_instance
            entities.append({'eid': eid, 'type': model})
        return entities

    def step(self, time, inputs, max_advance):
        self.time = time
        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution,
                                     unit='seconds'))  # timedelta represents a duration of time
        print('from h2demand %%%%%%%%%%%', current_time)

        for eid, attrs in inputs.items():

            for attr, vals in attrs.items():
                self._cache[eid] = self.entities[eid].demand(list(vals.values())[0])
        return time + 900

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            for attr in attrs:
                if attr == 'h2demand_dem':
                    data[eid][attr] = self._cache[eid]['h2demand_dem']
                    data['time'] = self.time
        return data
def main():
    mosaik_api.start_simulation(h2demandSim(), 'h2demand Simulator')
    
if __name__ == "__main__":
    main()
