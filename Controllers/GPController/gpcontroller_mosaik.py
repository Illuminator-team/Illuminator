import mosaik_api
import pandas as pd
try:
    import Controllers.GPController.gpcontroller_model as gpcontroller_model
except ModuleNotFoundError:
    import gpcontroller_model as gpcontroller_model
else:
    import Controllers.GPController.gpcontroller_model as gpcontroller_model
import sys
sys.path.insert(1,'/home/illuminator/Desktop/Final_illuminator')

# try:
#     import Models.Battery.battery_model as batterymodel
# except ModuleNotFoundError:
#     import battery_model as batterymodel
# else:
import Models.Battery.battery_model as batterymodel

META = {
    'type': 'hybrid',
    'models': {
        'GPCtrl': {
            'public': True,
            'params': ['sim_start', 'soc_min', 'soc_max', 'h2_soc_min', 'h2_soc_max', 'fc_eff'],
            'attrs': ['controller_id', 'net', 'deficit', 'excess', 'curtail'],
            'trigger': [],
        },
    },
}
incremental_attributes = ['flow2b', 'generator', 'demand', 'storage']

class gpcontrolSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'gpctrl_'
        self.entities = {}
        self._cache = {}  # used in the step function to store the values after running the python model of the technology
        #self.soc_max = {}
        #self.temp = 0
        #self.h2fc = {}
        # self.start_date = None
        
        

    # the following API call is will be called only once when we initiate the model in the scenario file.
    # we can use this to pass additional initialization tasks

    def init(self, sid, time_resolution, step_size=900):
        self.step_size = step_size
        self.sid = sid
        self.time_resolution = time_resolution
        self.time = 0
        self.incr_attr = []
        for attr in META['models']['GPCtrl']['attrs']:
            for inc_attr in incremental_attributes:
                if attr.startswith(inc_attr):
                    self.incr_attr.append(attr)
        return self.meta

    def create(self, num, model, sim_start, **model_params):
        self.start = pd.to_datetime(sim_start)
        # print(type(self.entities))
        # next_eid = len(self.entities)
        self._entities = []

        for i in range(num):
            eid = '%s%d' % (self.eid_prefix, i)
            model_instance = gpcontroller_model.gpcontroller_python(**model_params)  #1
            self.entities[eid] = model_instance  #2
            # print(self.entities)
            self._entities.append({'eid': eid, 'type': model})
        return self._entities

    def step(self, time, inputs, max_advance):
        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution,
                                     unit='seconds'))  # timedelta represents a duration of time
        self.time = time
        print('from controller %%%%%%%%%', current_time)
        _cache = {}

        for eid, attrs in inputs.items():               # configuration possible inputs
            generators_data = []
            demand_data = []
            storage_data = []
            curtail = 0

            # Loop through the dictionary and extract generator, load and storage data
            for key, value in inputs[eid].items():
                for k, v in value.items():
                    if 'generator' in key:
                        generators_data.append({'input': key.split('[')[1].split(']')[0],
                                                'type': k.split('.')[0],
                                                'name': k.split('.')[1],
                                                'p_gen': v})
                    elif 'demand' in key:
                        demand_data.append({'input': key.split('[')[1].split(']')[0],
                                           'type': k.split('.')[0],
                                           'name': k.split('.')[1],
                                           'p_dem': v})
                    elif 'storage' in key:
                        storage_data.append({'input': key.split('[')[1].split(']')[0],
                                           'type': k.split('.')[0],
                                           'name': k.split('.')[1],
                                           'soc': v})
                    elif 'curtail' in key:
                        if v and v != 0 and v is not None:
                            try:
                                curtail = v
                            except KeyError:
                                continue
            generators = pd.DataFrame()
            demands = pd.DataFrame()
            storages = pd.DataFrame()

            if generators_data:
                generators = pd.DataFrame(generators_data).set_index('input').sort_index()
            if demand_data:
                demands = pd.DataFrame(demand_data).set_index('input').sort_index()
            if storage_data:
                storages = pd.DataFrame(storage_data).set_index('input').sort_index()

            _cache[eid] = self.entities[eid].gpcontrol(generators, demands, storages, curtail)

        self._cache = _cache
        return self.time + self.step_size

    def get_data(self, outputs):            # to be implemented
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            try:
                self._cache[eid]
            except KeyError:
                continue
            for attr in attrs:
                if attr in self.incr_attr:
                    # Extract index from attribute string
                    try:
                        index = int(attr.split('[')[1].split(']')[0])
                        data[eid][attr] = self._cache[eid][attr.split('[')[0]][index]
                    except KeyError and TypeError and IndexError:
                        data[eid][attr] = None

                elif attr == 'excess':  # flow2e = energy to electrolyser
                    data[eid][attr] = self._cache[eid]['excess']
                elif attr == 'deficit':
                    data[eid][attr] = self._cache[eid]['deficit']
                elif attr == 'net':
                    data[eid][attr] = self._cache[eid]['net']
        return data
def main():
    mosaik_api.start_simulation(gpcontrolSim(), 'GPController-Illuminator')
if __name__ == '__main__':
    main()
