import mosaik_api
import multiprocessing as mp
import json
import os
try:
    import Models.Heatpump.heatpump.Heat_Pump_Model as HeatPump
except ModuleNotFoundError:
    import Heat_Pump_Model as HeatPump
else:
    import Models.Heatpump.heatpump.Heat_Pump_Model as HeatPump

META = {
    'type': 'time-based',
    'models': {
        'HeatPump': {
            'public': True,
            'params': ['params'],
            'attrs': ['Q_Demand', 'Q_Supplied', 'heat_source_T', 'heat_source', 'cons_T', 'P_Required', 'COP',
                      'cond_m', 'cond_in_T', 'T_amb', 'on_fraction', 'cond_m_neg', 'Q_evap', 'step_executed'],
        },
    },
}

JSON_COP_DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), 'cop_m_data.json'))

class HeatPumpSimulator(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.time_resolution = None
        self.models = dict()  # contains the model instances
        self.sid = None
        self.eid_prefix = 'HeatPump_'
        self.step_size = None
        self.time = 0

        self.parallelization = False
        self.processes = 1
        # start time of simulation as UTC ISO 8601 time string

    def init(self, sid, time_resolution, step_size, same_time_loop=False):
        self.time_resolution = float(time_resolution)
        if self.time_resolution != 1.0:
            print('WARNING: %s got a time_resolution other than 1.0, which \
                can not be handled by this simulator.', sid)
        self.sid = sid # simulator id
        self.step_size = step_size
        if same_time_loop:
            self.meta['type'] = 'event-based'

        return self.meta

    def create(self, num, model, params):
        entities = []

        if 'processes' in params:
            self.parallelization = True
            self.processes = params['processes']
            if num < self.processes:
                self.processes = num

        COP_m_data = None
        if params['calc_mode'] == 'fast' or params['calc_mode'] == 'fixed_hl':
            with open(JSON_COP_DATA, "r") as read_file_1:
                COP_m_data_all = json.load(read_file_1)
                COP_m_data = COP_m_data_all[params['hp_model']]

        next_eid = len(self.models)
        for i in range(next_eid, next_eid + num):
            eid = '%s%d' % (self.eid_prefix, i)
            self.models[eid] = HeatPump.Heat_Pump(params, COP_m_data)
            entities.append({'eid': eid, 'type': model})
        return entities

    def step(self, time, inputs, max_advance):
        # print('heatpump inputs: %s' % inputs)
        # print(f"Stepping HP at {time}")
        for eid, attrs in inputs.items():
            if self.meta['type'] == 'event-based':
                if time != self.time:
                    self.time = time
                    setattr(self.models[eid].state, 'step_executed', False)
            for attr, src_ids in attrs.items():
                if len(src_ids) > 1:
                    raise ValueError('Two many inputs for attribute %s' % attr)
                for val in src_ids.values():
                    setattr(self.models[eid].inputs, attr, val)

            self.models[eid].inputs.step_size = self.step_size

        if self.parallelization:
            pool = mp.Pool(processes=self.processes)
            for eid, model in self.models.items():
                pool.apply_async(model.step(), args=())
            pool.close()
            pool.join()
        else:
            for eid, model in self.models.items():
                model.step()

        if self.meta['type'] == 'event-based':
            return None
        else:
            return time + self.step_size

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            if self.models[eid].state.step_executed:
                data[eid] = {}
                for attr in attrs:
                    if attr not in self.meta['models']['HeatPump'][
                            'attrs']:
                        raise ValueError('Unknown output attribute: %s' % attr)
                    data['time'] = self.time
                    if attr != 'step_executed':
                        data[eid][attr] = float(getattr(self.models[eid].state, attr))
                    else:
                        data[eid][attr] = getattr(self.models[eid].state, attr)
        return data

def main():
    return mosaik_api.start_simulation(HeatPumpSimulator())

if __name__ == '__main__':
    main()