import mosaik_api
import pandas as pd
try:
    import Games.p2ptrading_model as p2ptrading_model
except ModuleNotFoundError:
    import p2ptrading_model as p2ptrading_model
else:
    import Games.p2ptrading_model as p2ptrading_model
import sys
sys.path.insert(1,'/home/illuminator/Desktop/Final_illuminator')


META = {
    'type': 'hybrid',
    'models': {
        'P2Ptrading': {
            'public': True,
            'params': ['sim_start'],
            'attrs': ['p2ptrading_id',  'transactions',  'quantity_traded'],
            'trigger': [],
        },
    },
}
incremental_attributes = ['supply_offers', 'demand_requests']

class p2ptradingSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'p2ptrading_'
        self.entities = {}
        self._cache = {}  #

    def init(self, sid, time_resolution, step_size=900):
        self.step_size = step_size
        self.sid = sid
        self.time_resolution = time_resolution
        self.time = 0
        self.incr_attr = []
        for attr in META['models']['P2Ptrading']['attrs']:
            for inc_attr in incremental_attributes:
                if attr.startswith(inc_attr):
                    self.incr_attr.append(attr)
        return self.meta

    def create(self, num, model, sim_start, **model_params):
        self.start = pd.to_datetime(sim_start)
        self._entities = []

        for i in range(num):
            eid = '%s%d' % (self.eid_prefix, i)
            model_instance = p2ptrading_model.p2ptrading_python(**model_params)  #1
            self.entities[eid] = model_instance  #2
            self._entities.append({'eid': eid, 'type': model})
        return self._entities

    def step(self, time, inputs, max_advance):
        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution,
                                     unit='seconds'))  # timedelta represents a duration of time
        self.time = time
        print('from peer-to-peer trading %%%%%%%%%', current_time)
        _cache = {}

        for eid, attrs in inputs.items():               # configuration possible inputs

            # Translator
            players_data = {}

            for key, value in inputs[eid].items():
                for k, v in value.items():
                    input_key = key.split('[')[1].split(']')[0]
                    type_key = k.split('.')[0]
                    name_key = k.split('.')[1]

                    if input_key not in players_data:
                        players_data[input_key] = {'input': input_key, 'type': type_key, 'name': name_key,
                                                   'demand_requests': None, 'supply_offers': None}
                    if 'supply_offers' in key:
                        players_data[input_key]['supply_offers'] = v
                    if 'demand_requests' in key:
                        players_data[input_key]['demand_requests'] = v

            # Check if there are any non-empty and non-zero 'supply_offers' or 'demand_requests'
            non_empty_players = [player for player in players_data.values() if
                                 (player['supply_offers'] is not None and player['supply_offers'] != 0) or (
                                             player['demand_requests'] is not None and player['demand_requests'] != 0)]

            if non_empty_players:
                players = pd.DataFrame(non_empty_players).set_index('input').sort_index()
            else:
                players = pd.DataFrame()

            _cache[eid] = self.entities[eid].p2ptrading(current_time, players)

        self._cache = _cache
        return self.time + self.step_size

    def get_data(self, outputs):            # to be implemented
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            for attr in attrs:
                if attr in self.incr_attr:
                    # Extract index from attribute string
                    index = int(attr.split('[')[1].split(']')[0])
                    data[eid][attr] = self._cache[eid][attr.split('[')[0]][index]
                elif attr == 'quantity_traded':
                    try:
                        data[eid][attr] = self._cache[eid]['quantity_traded']
                    except TypeError or KeyError:
                        data[eid][attr] = None
                elif attr == 'transactions':
                    try:
                        data[eid][attr] = self._cache[eid]['transactions']
                    except TypeError or KeyError:
                        data[eid][attr] = None
        return data
def main():
    mosaik_api.start_simulation(p2ptradingSim(), 'P2Ptrading-Illuminator')
if __name__ == '__main__':
    main()
