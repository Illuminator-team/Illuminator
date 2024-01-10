import mosaik_api
try:
    import Models.Heatdemand.qdemand_model as qdemand_model
except ModuleNotFoundError:
    import qdemand_model as qdemand_model
else:
    import Models.Heatdemand.qdemand_model as qdemand_model

import pandas as pd

META = {
    'type': 'event-based',

    'models': {
        'qdemandmodel': {
            'public': True,
            'params': ['sim_start', 'utilities'],
            'attrs': ['qdemand_id','qdemand_dem','qdemand'],
            'trigger': [],
        },
    },
}


class qdemandSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'qdemand_'
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
            model_instance = qdemand_model.qdemand_python(**model_params)
            self.entities[eid] = model_instance
            entities.append({'eid': eid, 'type': model})
        return entities

    def step(self, time, inputs, max_advance):
        self.time = time
        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution,
                                     unit='seconds'))  # timedelta represents a duration of time
        print('from qdemand %%%%%%%%%%%', current_time)

        for eid, attrs in inputs.items():

            for attr, vals in attrs.items():
                self._cache[eid] = self.entities[eid].demand(list(vals.values())[0])
        return time + 900

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            for attr in attrs:
                if attr == 'qdemand_dem':
                    data[eid][attr] = self._cache[eid]['qdemand_dem']
                    data['time'] = self.time
        return data
def main():
    mosaik_api.start_simulation(qdemandSim(), 'qdemand Simulator')
    
if __name__ == "__main__":
    main()
