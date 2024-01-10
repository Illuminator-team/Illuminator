import mosaik_api
from mosaik_heatpump.controller.controller import Controller

META = {
    'type': 'time-based',
    'models': {
        'Controller': {
            'public': True,
            'params': ['params'],
            'attrs': ['_', 'T_amb', 'heat_source_T', 'hp_demand', 'heat_supply', 'heat_demand', 'sh_demand', 'sh_supply',
                      'dhw_demand', 'dhw_supply', 'sh_in_F', 'sh_in_T', 'sh_out_F', 'dhw_in_F', 'dhw_in_T', 'dhw_out_F',
                      'hp_in_F', 'hp_in_T', 'hp_out_F', 'hp_out_T', 'hp_supply', 'hwt_connections', 'T_mean', 'hwt_mass',
                      'hwt_hr_P_th_set', 'hp_on_fraction', 'hp_cond_m'],
            # 'attrs': ['outside_temperature', 'sh_demand', 'sh_supply', 'dhw_demand', 'dhw_supply', 'hp_demand'],
        },
    },
    'extra_methods': [
        'add_async_request'
        ]
}


class ControllerSimulator(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)

        self.models = dict()  # contains the model instances
        self.sid = None
        self.eid_prefix = 'Controller_'
        self.step_size = None
        self.async_requests = dict()

    def init(self, sid, time_resolution, step_size):
        self.time_resolution = float(time_resolution)
        if self.time_resolution != 1.0:
            print('WARNING: %s got a time_resolution other than 1.0, which \
                can not be handled by this simulator.', sid)
        self.sid = sid # simulator id
        self.step_size = step_size
        return self.meta

    def create(self, num, model, params=None):
        entities = []

        next_eid = len(self.models)
        for i in range(next_eid, next_eid + num):
            eid = '%s%d' % (self.eid_prefix, i)
            if params is not None:
                self.models[eid] = Controller(params)
            else:
                self.models[eid] = Controller()
            entities.append({'eid': eid, 'type': model})
        return entities

    def add_async_request(self, src_id, dest_id, *attr_pairs):
        if not src_id in self.async_requests:
            self.async_requests[src_id] = {dest_id: {}}
        if not dest_id in self.async_requests[src_id]:
            self.async_requests[src_id][dest_id] = {}
        for attr_pair in attr_pairs:
            src_attr, dest_attr = attr_pair
            self.async_requests[src_id][dest_id].update({src_attr: dest_attr})

    def step(self, time, inputs, max_advance):
        # print('controller inputs: %s' % inputs)
        for eid, attrs in inputs.items():
            # print(eid, attrs)
            for attr, src_ids in attrs.items():
                if len(src_ids) > 1:
                    raise ValueError('Two many inputs for attribute %s' % attr)
                for val in src_ids.values():
                    setattr(self.models[eid], attr, val)

            self.models[eid].step_size = self.step_size
            self.models[eid].step()

        inputs = {}
        # print('async_reqs: %s' % self.async_requests)
        for src_id, dest_ids in self.async_requests.items():
            eid = src_id.split('.')[1]
            inputs[src_id] = {}
            for dest_id, src_attrs in dest_ids.items():
                inputs[src_id][dest_id] = {}
                for src_attr, dest_attr in src_attrs.items():
                    inputs[src_id][dest_id][dest_attr] = getattr(self.models[eid], src_attr)

        # print('controller inputs: %s' % inputs)
        yield self.mosaik.set_data(inputs)

        return time + self.step_size

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            for attr in attrs:
                if attr not in self.meta['models']['Controller'][
                        'attrs']:
                    raise ValueError('Unknown output attribute: %s' % attr)
                data[eid][attr] = getattr(self.models[eid], attr)
        return data

def main():
    return mosaik_api.start_simulation(ControllerSimulator())

if __name__ == '__main__':
    main()
