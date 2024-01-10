import mosaik_api

# import Qstorage.qstorage_model as heat_storage
try:
    import Models.Heatstorage.qstorage_model as heat_storage
except ModuleNotFoundError:
    import qstorage_model as heat_storage
else:
    import Models.Heatstorage.qstorage_model as heat_storage
import pandas as pd

META = {
    'type': 'event-based',
    'models': {
        'HeatStorage': {
            'public': True,
            'params': ['sim_start', 'soc_init','max_temperature', 'min_temperature', 'insulation',
                       'ext_temp', 'therm_cond',  'length', 'diameter', 'density', 'c', 'eff', 'max_q', 'min_q'],
            'attrs': ['qstorage_id',
                      'flow2qs',
                      'q_soc',
                      'mod',
                      'flag',
                      'q_soc',
                      'q_flow',
                      'q_loss',
                      't_int'],
            'trigger': [],
        },
    },
}


class heatstorageSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'qstorage_'
        self.entities = {}
        self._cache = {}
        self.soc = {}

    def init(self, sid, time_resolution):
        self.time_resolution = time_resolution
        return self.meta

    def create(self, num, model, sim_start, **model_params):
        self.start = pd.to_datetime(sim_start)
        self._entities = []

        # num is the number of models of battery we want.
        for i in range(num):
            self.eid = '%s%d' % (self.eid_prefix, i)
            qstorage_instance = heat_storage.heatstorage_python(**model_params)
            self.entities[self.eid] = qstorage_instance
            self._entities.append({'eid': self.eid, 'type': model, 'rel': [], })
        return self._entities

    def step(self, time, inputs, max_advance):
        self.time = time
        current_time = (self.start + pd.Timedelta(time * self.time_resolution, unit='seconds'))
        print('from heat storage %%%%%%%%', current_time)
        for eid, attrs in inputs.items():
            for attr, vals in attrs.items():
                if attr == 'flow2qs':
                    self._cache[eid] = self.entities[eid].output_q(sum(vals.values()))

        return None

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            for attr in attrs:
                if attr == 'q_soc':
                    data[eid][attr] = self._cache[eid]['q_soc']
                elif attr == 'mod':
                    data[eid][attr] = self._cache[eid]['mod']
                elif attr == 'flag':
                    data[eid][attr] = self._cache[eid]['flag']
                elif attr == 'q_flow':
                    data[eid][attr] = self._cache[eid]['q_flow']
                elif attr == 't_int':
                    data[eid][attr] = self._cache[eid]['t_int']
                elif attr == 'q_loss':
                    data[eid][attr] = self._cache[eid]['q_loss']
        return data

def main():
    mosaik_api.start_simulation(heatstorageSim(), 'HeatStorage-Simulator')


if __name__ == "__main__":
    main()
