import mosaik_api
import pandas as pd
#import Controller.controller_model as controller_model
try:
    import Controllers.Controller_ResLoad.controller_T1_model as controller_model
except ModuleNotFoundError:
    import controller_T1_model as controller_model
else:
    import Controllers.Controller_ResLoad.controller_T1_model as controller_model
#import Battery.model as batterymodel
import sys
sys.path.insert(1,'/home/illuminator/Desktop/Final_illuminator')

try:
    import Models.Battery.battery_model as batterymodel
except ModuleNotFoundError:
    import battery_model as batterymodel
else:
    import Models.Battery.battery_model as batterymodel

import itertools

# August 2024 JT Riederer
# double check if need to adapt for without battery case

META = {
    'type': 'event-based',
    'models': {
        'Ctrl': {
            'public': True,
            'params': ['sim_start', 'soc_min', 'soc_max', 'max_p'],
            'attrs': ['controller_id', 'res_load', 'flow2b', 'wind_gen', 'load_dem', 'pv_gen', 'soc','dump', 'load_EV'
                      ],
            'trigger': ['load_dem'],
        },
    },
} # left out attribute dump for now 240822


class controlSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'ctrl_'
        self.entities = {} 
        self._cache = {} 
        self.soc_max = {}
        self.temp = 0
        # self.start_date = None

    # the following API call is will be called only once when we initiate the model in the scenario file.
    # we can use this to pass additional initialization tasks

    def init(self, sid, time_resolution=900, step_size=900):
        self.step_size = step_size
        self.sid = sid
        self.time_resolution = time_resolution
        return self.meta

    def create(self, num, model, sim_start, **model_params):
        self.start = pd.to_datetime(sim_start)
        self._entities = []


        for i in range(num):
            eid = '%s%d' % (self.eid_prefix, i)
            model_instance = controller_model.Controller_ResLoad(**model_params)
            self.entities[eid] = model_instance
            self._entities.append({'eid': eid, 'type': model})
        return self._entities

    def step(self, time, inputs, max_advance):
        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution,
                                     unit='seconds'))
        print('from controller %%%%%%%%%', current_time)
        _cache = {}
        u = []
        for eid, attrs in inputs.items():
            # print('#eid: ', eid)
            print('#attrs: ', attrs)
            w = 0
            p = 0
            l = 0
            for attr, vals in attrs.items():
                if attr == 'wind_gen':
                    w = sum(vals.values())
                elif attr == 'pv_gen':
                    p = sum(vals.values())
                elif attr == 'load_dem':
                    l = sum(vals.values())
                elif attr == 'soc':
                    s = list(vals.values())[0]
            try:
                _cache[eid] = self.entities[eid].control(w, p, l, s)
            except:

                s = 50
                _cache[eid] = self.entities[eid].control(w, p, l, s)
            self._cache = _cache
        print(w,p,l,s)
        return time + 1

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            for attr in attrs:
                if attr == 'flow2b':
                    data[eid][attr] = self._cache[eid]['flow2b']
                elif attr == 'res_load':
                    data[eid][attr] = self._cache[eid]['res_load']
                elif attr == 'dump':
                    data[eid][attr] = self._cache[eid]['dump']

        return data
def main():
    mosaik_api.start_simulation(controlSim(), 'Controller-Illuminator')
if __name__ == '__main__':
    main()
