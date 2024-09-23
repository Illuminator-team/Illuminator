import mosaik_api
import numpy as np
import pandas as pd

#import Fuelcell.fuelcell_model as fc
try:
    import Models.Fuelcell.fuelcell_model as fc
except ModuleNotFoundError:
    import fuelcell_model as fc
else:
    import Models.Fuelcell.fuelcell_model as fc


meta = {
    'type': 'event-based',
    'models': {
        'fuelcellmodel': {
            'public': True,
            'params': ['sim_start', 'eff', 'term_eff','min_flow','max_flow','resolution'],
            'attrs': ['h2fuel','h2_consume', 'fc_gen', 'q_product'],
            'trigger': [],
        },
    },
}

class FuelCellSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(meta)
        self.eid_prefix = 'fc_'
        self.entities = {}
        self._cache = {}
        self.fc_gen = {}

    def init(self, sid, time_resolution):
        self.time_resolution = time_resolution
        return self.meta

    def create(self, num, model, sim_start, **model_params):
        self.start = pd.to_datetime(sim_start)
        entities = []

        for i in range (num):
            eid = '%s%d' % (self.eid_prefix, i)
            model_instance = fc.fuelcell_python(**model_params)
            self.entities[eid] = model_instance
            entities.append({'eid': eid, 'type': model})
        return entities

    def step(self, time, inputs, max_advance):
        self.time = time
        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution, unit='seconds'))
        print('from fuel cell %%%%%%%%%%', current_time)

        for eid, attrs in inputs.items():
            for attr, vals in attrs.items():
                if attr == 'h2_consume':
                    h2_consume = list(vals.values())[0]
                    self._cache[eid] = self.entities[eid].output(h2_consume)
        return None

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            for attr in attrs:
                if attr == 'fc_gen':
                    data[eid][attr] = self._cache[eid]['fc_gen']
                if attr == 'h2_consume':
                    data[eid][attr] = self._cache[eid]['h2_consume']
                if attr == 'q_product':
                    data[eid][attr] = self._cache[eid]['q_product']

                if attr =='h2fuel':
                    data[eid][attr] = self._cache[eid]['h2fuel']
        return data
def main():
    mosaik_api.start_simulation(FuelCellSim(), 'FuelCell Simulator')

if __name__ == "__main__":
    main()
