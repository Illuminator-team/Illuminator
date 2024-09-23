import mosaik_api
import pandas as pd
try:
    import Models.Valves.qvalve_model as qvalve_model
except ModuleNotFoundError:
    import qvalve_model as qvalve_model
else:
    import Models.Valves.qvalve_model as qvalve_model
import sys
sys.path.insert(1,'/home/illuminator/Desktop/Final_illuminator')

META = {
    'type': 'event-based',
    'models': {
        'Qvalve': {
            'public': True,
            'params': ['sim_start'],
            'attrs': ['valve_id', 'q_eboiler', 'q_stor',
                      'q_eboiler_net', 'q_stor_net',
                      'q_eboiler_stor'],
            'trigger': [],
        },
    },
}
incremental_attributes = []

class qvalveSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'Qvalve_'
        self.entities = {}
        self._cache = {}


    def init(self, sid, time_resolution, step_size=1):
        self.step_size = step_size
        self.sid = sid
        self.time_resolution = time_resolution
        self.time = 0

        return self.meta

    def create(self, num, model, sim_start, **model_params):
        self.start = pd.to_datetime(sim_start)
        self._entities = []

        for i in range(num):
            eid = '%s%d' % (self.eid_prefix, i)
            model_instance = qvalve_model.qvalve_python(**model_params)  #1
            self.entities[eid] = model_instance  #2
            self._entities.append({'eid': eid, 'type': model})
        return self._entities

    def step(self, time, inputs, max_advance):
        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution,
                                     unit='seconds'))  # timedelta represents a duration of time
        self.time = time
        print('from q valve %%%%%%%%%', current_time)

        for eid, attrs in inputs.items():
            q_elec = 0
            q_stor = 0
            q_fc = 0
            for attr, vals in attrs.items():
                if attr == 'q_eboiler':
                    q_elec = sum(vals.values())
                if attr == 'q_stor':
                    q_stor = sum(vals.values())

            self._cache[eid] = self.entities[eid].route(q_elec, q_stor)

        return None

    def get_data(self, outputs):            # to be implemented
        data = {}
        for eid, attrs in outputs.items():

            data[eid] = {}
            for attr in attrs:
                # if attr in self.incr_attr:
                #     # Extract index from attribute string
                #     index = int(attr.split('[')[1].split(']')[0])
                #     data[eid][attr] = self._cache[eid][attr.split('[')[0]][index]
                if attr == 'q_eboiler':
                    data[eid][attr] = self._cache[eid]['q_eboiler']
                elif attr == 'q_stor':
                    data[eid][attr] = self._cache[eid]['q_stor']
                elif attr == 'q_eboiler_net':
                    data[eid][attr] = self._cache[eid]['q_eboiler_net']
                elif attr == 'q_stor_net':
                    data[eid][attr] = self._cache[eid]['q_stor_net']
                elif attr == 'q_eboiler_stor':
                    data[eid][attr] = self._cache[eid]['q_eboiler_stor']

        return data
def main():
    mosaik_api.start_simulation(qvalveSim(), 'Qvalve-Illuminator')
if __name__ == '__main__':
    main()
