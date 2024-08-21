import mosaik_api
import pandas as pd
#import Controller.controller_model as controller_model
try:
    import Models.Controller.controller_model as controller_model
except ModuleNotFoundError:
    import controller_model as controller_model
else:
    import Models.Controller.controller_model as controller_model
#import Battery.model as batterymodel
import sys
sys.path.insert(1, '/home/illuminator/Desktop/Final_illuminator')

try:
    import Models.Battery.battery_model as batterymodel
except ModuleNotFoundError:
    import battery_model as batterymodel
else:
    import Models.Battery.battery_model as batterymodel

import itertools
META = {
    'type': 'event-based',
    # wind is an event based event because the event here is a wind speed. It doesnt purely run because of time interval, I think.
    # if I put it to time-based, there is type error:
    # File "C:\Users\ragha\AppData\Local\Programs\Python\Python310\lib\site-packages\mosaik\scheduler.py", line 405, in step
    #     sim.progress_tmp = next_step - 1
    # TypeError: unsupported operand type(s) for -: 'NoneType' and 'int'

    'models': {
        'Ctrl': {
            'public': True,
            'params': ['sim_start', 'soc_min', 'soc_max', 'h2_soc_min', 'h2_soc_max', 'fc_eff'],
            'attrs': ['controller_id', 'flow2e', 'flow2b', 'wind_gen', 'load_dem', 'pv_gen', 'soc', 'h2_soc', 'dump', 'h2_out',
                      ],
            'trigger': [],
        },
    },
}


class controlSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'ctrl_'  # every entity that we create will start with 'wind_'
        self.entities = {}  # we store the model entity of our technology model
        self._cache = {}  # used in the step function to store the values after running the python model of the technology
        self.soc_max = {}
        self.temp = 0
        self.h2fc = {}
        # self.start_date = None

    # the following API call is will be called only once when we initiate the model in the scenario file.
    # we can use this to pass additional initialization tasks

    def init(self, sid, time_resolution, step_size=1):
        self.step_size = step_size
        self.sid = sid
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
        self._entities = []
        # print(next_eid)  # working (20220524)

        for i in range(num):
            eid = '%s%d' % (self.eid_prefix, i)
            model_instance = controller_model.controller_python(**model_params)  #1
            self.entities[eid] = model_instance  #2
            # print(self.entities)
            # self.soc_max[eid] = soc_max
            self._entities.append({'eid': eid, 'type': model})
        return self._entities

    def step(self, time, inputs, max_advance):
        # inputs is a dictionary, which contains another dictionary.
        # print(inputs)
        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution,
                                     unit='seconds'))  # timedelta represents a duration of time
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
                #print('#attr: ', attr)
                # print('#vals: ', vals)

                # s=0
                # h=0
                ###################################
                if attr == 'wind_gen':
                    w = sum(vals.values())
                elif attr == 'pv_gen':
                    p = sum(vals.values())
                elif attr == 'load_dem':
                    l = sum(vals.values())
                elif attr == 'soc':
                    s = list(vals.values())[0]
                elif attr == 'h2_soc':
                    h = list(vals.values())[0]
            try:
                _cache[eid] = self.entities[eid].control(w, p, l, s, h)
            except:

                s = 50
                h = 0
                _cache[eid] = self.entities[eid].control(w, p, l, s, h)
            self._cache = _cache
        print(w,p,l,s,h)
        return None

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            # model = self.entities[eid]
            # data['time'] = self.time
            data[eid] = {}
            for attr in attrs:
                # if we want more values to print in the output file, mimic the below for new attributes and make sure
                # those parameters are present in the re_params in the python file of the technology
                if attr == 'flow2b':  # e2b = energy to battery
                    data[eid][attr] = self._cache[eid]['flow2b']
                elif attr == 'flow2e':  # flow2e = energy to electrolyser
                    data[eid][attr] = self._cache[eid]['flow2e']
                elif attr == 'dump':
                    data[eid][attr] = self._cache[eid]['dump']
                elif attr == 'h2_out':
                    data[eid][attr] = self._cache[eid]['h2_out']
                # print(data)
        return data
def main():
    mosaik_api.start_simulation(controlSim(), 'Controller-Illuminator')
if __name__ == '__main__':
    main()
