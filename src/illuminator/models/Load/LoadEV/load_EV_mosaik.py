import mosaik_api

# import Load.load_model as load_model
try:
    import Models.Load_EV.load_EV as load_EV
except ModuleNotFoundError:
    import load_EV as load_EV
else:
    import Models.Load_EV.load_EV as load_EV

import pandas as pd
import itertools

META = {
    'type': 'time-based',

    'models': {
        'evloadmodel': {
            'public': True,
            'params': ['sim_start', 'houses_case', 'houses_data'],
            'attrs': ['ev_load_id', 'load_EV', 'power', 'n'], # n is number of EVs charging at a certain point in time
            'trigger': [],
        },
    },
}


class evLoadSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'ev_load_'  # every entity that we create will start with 'load_'
        self.entities = {}  # we store the model entity of our technology model
        self._cache = {}  # used in the step function to store the values after running the python model of the technology
        self.time = 0
        # self.start_date = None

    # the following API call is will be called only once when we initiate the model in the scenario file.
    # we can use this to pass additional initialization tasks

    def init(self, sid, time_resolution):
        # print('hi, you have entered init')  # working (20220524)
        self.time_resolution = time_resolution
        # print('Exited init os SimAPI')  # working (20220524)
        return self.meta

    def create(self, num, model, sim_start, **model_params):
        # print('hi, you have entered create of SimAPI')  # working (20220524)
        self.start = pd.to_datetime(sim_start)
        # print(type(self.entities))
        # next_eid = len(self.entities)
        # print('from create of SimAPI:', next_eid)
        entities = []
        # print(next_eid)  # working (20220524)

        for i in range(num):
            eid = '%s%d' % (self.eid_prefix, i)
            model_instance = load_EV.load_EV(**model_params)
            self.entities[eid] = model_instance
            entities.append({'eid': eid, 'type': model})
        return entities

    def step(self, time, inputs, max_advance):
        self.time = time
        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution,
                                     unit='seconds'))  # timedelta represents a duration of time
        print('from EV load %%%%%%%%%%%', current_time)

        for eid, attrs in inputs.items():
            v = []
            for attr, vals in attrs.items():
                u = list(vals.values())
                v.append(u)
            v_merged = list(itertools.chain(*v))
            self._cache[eid] = self.entities[eid].demand(v_merged[0], v_merged[1])
        return time + 1

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            for attr in attrs:
                if attr == 'load_EV':
                    data[eid][attr] = self._cache[eid]['load_EV']
                    data['time'] = self.time
                if attr == 'n':
                    data[eid][attr] = self._cache[eid]['n']
                    data['time'] = self.time
        return data


def main():
    mosaik_api.start_simulation(evLoadSim(), 'EV load Simulator')

if __name__ == "__main__":
    main()