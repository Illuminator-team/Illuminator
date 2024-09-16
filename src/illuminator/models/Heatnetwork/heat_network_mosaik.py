import mosaik_api
import pandas as pd
try:
    import Models.Heatnetwork.heat_network_model as heat_network_model
except ModuleNotFoundError:
    import heat_network_model as heat_network_model
else:
    import Models.Heatnetwork.heat_network_model as heat_network_model
import sys

META = {
    'type': 'event-based',
    'models': {
        'HeatNetwork': {
            'public': True,
            'params': ['sim_start', 'max_temperature', 'insulation', 'ext_temp','therm_cond', 'length', 'diameter',
                       'density', 'c'],
            'attrs': ['Qnetwork_id', 't_int', 'q_loss', 'congestion'],
            'trigger': [],
        },
    },
}
incremental_attributes = ['q_in', 'q_out']


class heatnetworkSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'Heatnetwork_'
        self.entities = {}
        self._cache = {}  # used in the step function to store the values after running the python model of the technology
        #self.soc_max = {}
        #self.temp = 0
        #self.h2fc = {}
        # self.start_date = None
        
        

    # the following API call is will be called only once when we initiate the model in the scenario file.
    # we can use this to pass additional initialization tasks

    def init(self, sid, time_resolution, step_size=1):
        self.step_size = step_size
        self.sid = sid
        self.time_resolution = time_resolution
        self.time = 0
        self.incr_attr = []
        for attr in META['models']['HeatNetwork']['attrs']:
            for inc_attr in incremental_attributes:
                if attr.startswith(inc_attr):
                    self.incr_attr.append(attr)
        return self.meta

    def create(self, num, model, sim_start, **model_params):
        self.start = pd.to_datetime(sim_start)
        self._entities = []

        for i in range(num):
            eid = '%s%d' % (self.eid_prefix, i)
            model_instance = heat_network_model.heat_network_python(**model_params)  #1
            self.entities[eid] = model_instance  #2
            self._entities.append({'eid': eid, 'type': model})
        return self._entities

    def step(self, time, inputs, max_advance):
        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution,
                                     unit='seconds'))  # timedelta represents a duration of time
        self.time = time
        print('from heat network %%%%%%%%%', current_time)
        _cache = {}

        for eid, attrs in inputs.items():               # configuration possible inputs
            q_in = []
            q_out = []
            for i in range(len(inputs[eid])):
                if 'q_in[{}]'.format(i) in inputs[eid]:
                    q_in.append(inputs[eid]['q_in[{}]'.format(i)][list(inputs[eid]['q_in[{}]'.format(i)].keys())[0]])
                if 'q_out[{}]'.format(i) in inputs[eid]:
                    q_out.append(inputs[eid]['q_out[{}]'.format(i)][list(inputs[eid]['q_out[{}]'.format(i)].keys())[0]])
            _cache[eid] = self.entities[eid].heatnetwork(q_in, q_out)

        self._cache = _cache
        return None

    def get_data(self, outputs):            # to be implemented
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            for attr in attrs:
                if attr in self.incr_attr:
                    # Extract index from attribute string
                    index = int(attr.split('[')[1].split(']')[0])
                    data[eid][attr] = self._cache[eid][attr.split('[')[0]][index]
                elif attr == 't_int':
                    data[eid][attr] = self._cache[eid]['t_int']
                elif attr == 'q_loss':
                    data[eid][attr] = self._cache[eid]['q_loss']
                elif attr == 'congestion':
                    data[eid][attr] = self._cache[eid]['congestion']
        return data
def main():
    mosaik_api.start_simulation(heatnetworkSim(), 'HeatNetwork-Illuminator')
if __name__ == '__main__':
    main()
