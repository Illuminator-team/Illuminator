import mosaik_api
#import H2storage.h2storage_model as h2trailer
try:
    import Models.H2storage.h2storage_model as hydrogen_storage
except ModuleNotFoundError:
    import h2storage_model as hydrogen_storage
else:
    import Models.H2storage.h2storage_model as hydrogen_storage
import pandas as pd
import itertools
META = {
    'type': 'event-based',
    'models': {
        'compressed_hydrogen': {
            'public': True,
            'params': ['sim_start', 'initial_set', 'h2_set'],
            'attrs': ['h2storage_id',
                      'flow2h2s',
                      'eleh2_in',
                      'fuelh2_out',
                      'h2_flow',
                      'h2_excess_flow',
                      'h2_soc',
                      'mod',
                      'flag',
                      'h2_flow'],
            'trigger': [],
        },
    },
}

class compressedhydrogen(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'h2storage_'
        self.entities = {}
        self._cache = {}
        self.soc = {}
        self.flag = {}
        self.h2_stored = {}

    def init(self, sid, time_resolution):
        self.time_resolution = time_resolution
        return self.meta

    def create(self, num, model, initial_set, h2_set, sim_start):
        self.start = pd.to_datetime(sim_start)
        self._entities = []

        # num is the number of models of battery we want.
        for i in range(num):
            self.eid = '%s%d' % (self.eid_prefix, i)
            h2storage_instance = hydrogen_storage.hydrogenstorage_python(initial_set, h2_set)

            self.entities[self.eid] = h2storage_instance
            self.soc[self.eid] = initial_set['initial_soc']
            self.flag[self.eid] = h2_set['flag']
            self._entities.append({'eid': self.eid, 'type': model, 'rel': [], })
        return self._entities

    def step(self, time, inputs, max_advance):
        self.time = time
        current_time = (self.start + pd.Timedelta(time * self.time_resolution, unit='seconds'))
        print('from h2 storage %%%%%%%%', current_time)
        eleh2_in=0
        flow2h2s=0
        fuelh2_out=0

        for eid, attrs in inputs.items():
            for attr, vals in attrs.items():
                #flow2h2s, eleh2_in, fuelh2_out
                if attr=='eleh2_in':
                    eleh2_in=eleh2_in+list(vals.values())[0]
                elif attr=='fuelh2_out':
                    fuelh2_out=fuelh2_out+list(vals.values())[0]
                elif attr=='flow2h2s':
                    flow2h2s = flow2h2s + list(vals.values())[0]

            self._cache[eid] = self.entities[eid].output_h2(flow2h2s,eleh2_in,fuelh2_out, self.soc[eid])

            self.soc[eid] = self._cache[eid]['h2_soc']
            self.flag = self._cache[eid]['flag']

        return None

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            model = self.entities[eid]
            data[eid] = {}
            for attr in attrs:
                if attr == 'h2_soc':
                    data[eid][attr] = self._cache[eid]['h2_soc']
                elif attr == 'mod':
                    data[eid][attr] = self._cache[eid]['mod']
                elif attr == 'h2storage_id':
                    data[eid][attr] = eid
                elif attr == 'flag':
                    data[eid][attr] = self._cache[eid]['flag']

                elif attr == 'eleh2_in':
                    data[eid][attr] = self._cache[eid]['eleh2_in']
                elif attr == 'fuelh2_out':
                    data[eid][attr] = self._cache[eid]['fuelh2_out']
                elif attr == 'h2_flow':
                    data[eid][attr] = self._cache[eid]['h2_flow']
                elif attr == 'h2_excess_flow':
                    data[eid][attr] = self._cache[eid]['h2_excess_flow']

        return data


def main():
    mosaik_api.start_simulation(compressedhydrogen(), 'H2storage-Simulator')
    
if __name__ == "__main__":
    main()