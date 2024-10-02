import mosaik_api
import pandas as pd
try:
    import Models.Valves.h2valve_model as h2valve_model
except ModuleNotFoundError:
    import h2valve_model as h2valve_model
else:
    import Models.Valves.h2valve_model as h2valve_model
import sys
sys.path.insert(1,'/home/illuminator/Desktop/Final_illuminator')

META = {
    'type': 'event-based',
    'models': {
        'H2Valve': {
            'public': True,
            'params': ['sim_start'],
            'attrs': ['valve_id', 'h2_elec', 'h2_stor','h2_fc',
                      'h2_elec_net', 'h2_stor_net', 'h2_fc_net',
                      'h2_elec_stor', 'h2_stor_fc'],
            'trigger': [],
        },
    },
}
incremental_attributes = []

class h2valveSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'H2valve_'
        self.entities = {}
        self._cache = {}


    def init(self, sid, time_resolution, step_size=1):
        self.step_size = step_size
        self.sid = sid
        self.time_resolution = time_resolution
        self.time = 0
        # self.incr_attr = []
        # for attr in META['models']['ElectricityNetwork']['attrs']:
        #     for inc_attr in incremental_attributes:
        #         if attr.startswith(inc_attr):
        #             self.incr_attr.append(attr)
        return self.meta

    def create(self, num, model, sim_start, **model_params):
        self.start = pd.to_datetime(sim_start)
        self._entities = []

        for i in range(num):
            eid = '%s%d' % (self.eid_prefix, i)
            model_instance = h2valve_model.h2valve_python(**model_params)  #1
            self.entities[eid] = model_instance  #2
            self._entities.append({'eid': eid, 'type': model})
        return self._entities

    def step(self, time, inputs, max_advance):
        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution,
                                     unit='seconds'))  # timedelta represents a duration of time
        self.time = time
        print('from h2 valve %%%%%%%%%', current_time)

        for eid, attrs in inputs.items():
            h2_elec = 0
            h2_stor = 0
            h2_fc = 0
            for attr, vals in attrs.items():
                if attr == 'h2_elec':
                    h2_elec = sum(vals.values())
                if attr == 'h2_stor':
                    h2_stor = sum(vals.values())
                if attr == 'h2_fc':
                    h2_fc = sum(vals.values())

            self._cache[eid] = self.entities[eid].route(h2_elec, h2_stor, h2_fc)

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
                if attr == 'h2_elec':
                    data[eid][attr] = self._cache[eid]['h2_elec']
                elif attr == 'h2_stor':
                    data[eid][attr] = self._cache[eid]['h2_stor']
                elif attr == 'h2_fc':
                    data[eid][attr] = self._cache[eid]['h2_fc']
                elif attr == 'h2_elec_net':
                    data[eid][attr] = self._cache[eid]['h2_elec_net']
                elif attr == 'h2_stor_net':
                    data[eid][attr] = self._cache[eid]['h2_stor_net']
                elif attr == 'h2_fc_net':
                    data[eid][attr] = self._cache[eid]['h2_fc_net']
                elif attr == 'h2_elec_stor':
                    data[eid][attr] = self._cache[eid]['h2_elec_stor']
                elif attr == 'h2_stor_fc':
                    data[eid][attr] = self._cache[eid]['h2_stor_fc']
        return data
def main():
    mosaik_api.start_simulation(h2valveSim(), 'H2Valve-Illuminator')
if __name__ == '__main__':
    main()
