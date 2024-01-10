import mosaik_api
import pandas as pd
from Agents.prosumer_S_model import *

try:
    import Agents.prosumer_model as prosumer_model
except ModuleNotFoundError:
    import prosumer_model as prosumer_model
else:
    import Agents.prosumer_model as prosumer_model
import sys
sys.path.insert(1,'/home/illuminator/Desktop/Final_illuminator')

META = {
    'type': 'hybrid',
    'models': {
        'Prosumer': {
            'public': True,
            'params': ['sim_start', 'forecasted_data', 'metrics', 'strategy'],
            'attrs': ['agent_id', 'em_supply_bids', 'em_demand_bids', 'em_accepted_bids', 'p2em', 'p2p2p',
                      'p2p_supply_offers', 'p2p_demand_requests', 'p2p_transactions', 'rt_buy', 'rt_sell'],
            'trigger': [],
        },
    },
}
incremental_attributes = ['generator', 'demand', 'storage']

class prosumerSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'prosumer_'
        self.entities = {}
        self._cache = {}

    def init(self, sid, time_resolution, step_size=900):
        self.step_size = step_size
        self.sid = sid
        self.time_resolution = time_resolution
        self.time = 0
        self.incr_attr = []
        for attr in META['models']['Prosumer']['attrs']:
            for inc_attr in incremental_attributes:
                if attr.startswith(inc_attr) and inc_attr[-1] == ']':
                    self.incr_attr.append(attr)
        return self.meta

    def create(self, num, model, sim_start, strategy, **model_params):
        self.start = pd.to_datetime(sim_start)
        self._entities = []

        for i in range(num):
            eid = '%s%s_%d' % (self.eid_prefix, strategy, i)
            if strategy == 's1':
                model_instance = prosumer_S1(eid, **model_params)
            elif strategy == 's2':
                model_instance = prosumer_S2(eid, **model_params)
            elif strategy == 's3':
                model_instance = prosumer_S3(eid, **model_params)
            else:
                raise ValueError(f"Invalid model: {model}")

            self.entities[eid] = model_instance
            self._entities.append({'eid': eid, 'type': model})

        return self._entities

    def step(self, time, inputs, max_advance):
        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution,
                                     unit='seconds'))  # timedelta represents a duration of time
        self.time = time
        print('from prosumer %%%%%%%%%', current_time)
        _cache = {}

        for eid, attrs in inputs.items():               # configuration possible inputs
            generators = pd.DataFrame()
            demands = pd.DataFrame()
            storages = pd.DataFrame()
            generators_data = []
            demand_data = []
            storage_data = []
            em_accepted_bids = []
            p2p_transactions = []

            # Loop through the dictionary and extract generator, load and storage data
            for key, value in inputs[eid].items():
                for k, v in value.items():
                    if 'generator' in key:
                        generator_item = {'input': key.split('[')[1].split(']')[0],
                                          'from': k.split('.')[1],
                                          'name': key,
                                          'p_gen': v}
                        generators_data.append(generator_item)

                    elif 'demand' in key:
                        demand_item = {'input': key.split('[')[1].split(']')[0],
                                       'from': k.split('.')[1],
                                       'name': key,
                                        'p_dem': v}
                        demand_data.append(demand_item)

                    elif 'storage' in key:
                        storage_item = {'input': key.split('[')[1].split(']')[0],
                                        'from': k.split('.')[1],
                                        'name': key,
                                        'soc': v}
                        storage_data.append(storage_item)

                    elif 'em_accepted_bids' in key:
                        if v and v != 0 and v is not None:
                            try:
                                em_accepted_bids = v[eid]
                            except KeyError:
                                continue
                    elif 'p2p_transactions' in key:
                        if v and v != 0 and v is not None:
                            try:
                                p2p_transactions = v[eid]
                            except KeyError:
                                continue

            if generators_data:
                generators = pd.DataFrame(generators_data).set_index('input').sort_index()
            if demand_data:
                demands = pd.DataFrame(demand_data).set_index('input').sort_index()
            if storage_data:
                storages = pd.DataFrame(storage_data).set_index('input').sort_index()

            _cache[eid] = self.entities[eid].prosumer(
                self.start, current_time, generators, demands, storages, em_accepted_bids, p2p_transactions)

        self._cache = _cache
        return self.time + self.step_size

    def get_data(self, outputs):            # to be implemented
        data = {}
        for eid, attrs in outputs.items():
            # model = self.entities[eid]
            # data['time'] = self.time
            data[eid] = {}
            for attr in attrs:
                if attr in self.incr_attr:
                    # Extract index from attribute string
                    index = int(attr.split('[')[1].split(']')[0])
                    data[eid][attr] = self._cache[eid][attr.split('[')[0]][index]
                elif attr == 'em_supply_bids':
                    try:
                        data[eid][attr] = self._cache[eid]['em_supply_bids']
                    except KeyError:
                        data[eid][attr] = None
                elif attr == 'em_demand_bids':
                    try:
                        data[eid][attr] = self._cache[eid]['em_demand_bids']
                    except KeyError:
                        data[eid][attr] = None
                elif attr == 'p2p_supply_offers':
                    try:
                        data[eid][attr] = self._cache[eid]['p2p_supply_offers']
                    except KeyError:
                        data[eid][attr] = None
                elif attr == 'p2p_demand_requests':
                    try:
                        data[eid][attr] = self._cache[eid]['p2p_demand_requests']
                    except KeyError:
                        data[eid][attr] = None
                elif attr == 'rt_buy':
                    try:
                        data[eid][attr] = self._cache[eid]['rt_buy']
                    except KeyError:
                        data[eid][attr] = 0
                elif attr == 'rt_sell':
                    try:
                        data[eid][attr] = self._cache[eid]['rt_sell']
                    except KeyError:
                        data[eid][attr] = 0
                elif attr == 'p2em':
                    try:
                        data[eid][attr] = self._cache[eid]['p2em']
                    except KeyError:
                        data[eid][attr] = 0
                elif attr == 'p2p2p':
                    try:
                        data[eid][attr] = self._cache[eid]['p2p2p']
                    except KeyError:
                        data[eid][attr] = 0
        return data
def main():
    mosaik_api.start_simulation(prosumerSim(), 'Prosumer-Illuminator')
if __name__ == '__main__':
    main()
