import mosaik_api
import pandas as pd

try:
    import Controllers.NetVoltageControllerSim.controller as controller_model
except ModuleNotFoundError:
    import controller as controller_model
else:
    import Controllers.NetVoltageControllerSim.controller as controller_model
#import Battery.model as batterymodel
import sys

import itertools
META = {
    'type': 'event-based',

    'models': {
        'Ctrl': {
            'public': True,
            'params': ['net', 'room'],
            'attrs': ['controller_id', 'vm_pu', 'p_mw','q_mvar'],
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
        self.temp = 0
        # self.start_date = None

    # the following API call is will be called only once when we initiate the model in the scenario file.
    # we can use this to pass additional initialization tasks

    def init(self, sid, time_resolution, step_size=1):
        self.step_size = step_size
        self.sid = sid
        # print('hi, you have entered init')  # working (20220524)
        self.time_resolution = time_resolution
        # print('Exited init os SimAPI')  # working (20220524)
        self.attr_names = []
        # print(next_eid)  # working (20220524)
        self.attr_names = [f'p_m_update{i}' for i in range(19)]
        self.attr_names.extend([f'q_war_update{i}' for i in range(19)])
        self.meta['models']['Ctrl']['attrs'].extend(self.attr_names)

        return self.meta

    def create(self, num, model,**model_params):
        # print('hi, you have entered create of SimAPI')  # working (20220524)
        # print(type(self.entities))
        # next_eid = len(self.entities)
        # print('from create of SimAPI:', next_eid)
        self._entities = []

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

        _cache = {}
        u = []
        for eid, attrs in inputs.items():
            # print('#eid: ', eid)
            print('#attrs: ', attrs)

            for attr, vals in attrs.items():

                if attr == 'p_mw':
                    p_mw = vals.values()
                elif attr == 'vm_pu':
                    vm_pu = vals.values()
                elif attr =='q_mvar':
                    q_mvar = vals.values()

            _cache[eid] = self.entities[eid].control(p_mw,q_mvar,vm_pu,self.attr_names)
            self._cache = _cache
        print(p_mw,vm_pu)
        return None

    def get_data(self, outputs):
        data = {}
        print('1')
        for eid, attrs in outputs.items():
            # model = self.entities[eid]
            # data['time'] = self.time
            data[eid] = {}
            for attr in attrs:
                # if we want more values to print in the output file, mimic the below for new attributes and make sure
                # those parameters are present in the re_params in the python file of the technology
                if attr in ['controller_id', 'vm_pu', 'p_mw','q_mvar']:
                    pass
                else:
                    data[eid][attr] = self._cache[eid][attr]

        return data
def main():
    mosaik_api.start_simulation(controlSim(), 'Controller-Illuminator')
if __name__ == '__main__':
    main()