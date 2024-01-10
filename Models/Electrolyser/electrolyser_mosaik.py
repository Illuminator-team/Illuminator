import mosaik_api
#import Electrolyser.electrolyser_model as electrolyser_model
try:
    import Models.Electrolyser.electrolyser_model as electrolyser_model
except ModuleNotFoundError:
    import electrolyser_model as electrolyser_model
else:
    import Models.Electrolyser.electrolyser_model as electrolyser_model

import pandas as pd

META = {
    'type': 'event-based',
    'models': {
        'electrolysermodel': {
            'public': True,
            'params': ['sim_start', 'eff', 'resolution', 'term_eff','rated_power','ramp_rate'],
            'attrs': ['electro_id','h2_gen', 'flow2e', 'q_product', 'e_consume'],
            'trigger': [],
        },
    },
}


class ElectrolyserSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'electrolyser_'
        self.entities = {}
        self._cache = {}

    def init(self, sid, time_resolution):
        self.time_resolution = time_resolution
        return self.meta

    def create(self, num, model, sim_start, **model_params):
        self.start = pd.to_datetime(sim_start)
        entities = []

        for i in range(num):
            eid = '%s%d' % (self.eid_prefix, i)
            model_instance = electrolyser_model.electrolyser_python(**model_params)
            self.entities[eid] = model_instance
            entities.append({'eid': eid, 'type': model})

        return entities

    def step(self, time, inputs, max_advance):

        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution,
                                     unit='seconds'))  # timedelta represents a duration of time
        print('from electrolyser %%%%%%%%%',current_time)

        for eid, attrs in inputs.items():
            for attr, vals in attrs.items():
                if attr == 'flow2e':
                    flow2e = list(vals.values())[0]
                    self._cache[eid] = self.entities[eid].electrolyser(flow2e)

        return None

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            for attr in attrs:
                if attr == 'h2_gen':
                    data[eid][attr] = self._cache[eid]['h2_gen']
                if attr == 'flow2e':
                    data[eid][attr] = self._cache[eid]['flow2e']
                if attr == 'q_product':
                    data[eid][attr] = self._cache[eid]['q_product']
                if attr ==  'e_consume':
                    data[eid][attr] = self._cache[eid]['e_consume']
        return data


def main():
    mosaik_api.start_simulation(ElectrolyserSim(), 'Electrolyser-Simulator')
    
if __name__ == "__main__":
    main()
    
