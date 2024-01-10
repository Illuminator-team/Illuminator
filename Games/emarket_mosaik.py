import mosaik_api
import pandas as pd
try:
    import Games.emarket_model as emarket_model
except ModuleNotFoundError:
    import emarket_model as emarket_model
else:
    import Games.emarket_model as emarket_model
import sys
sys.path.insert(1,'/home/illuminator/Desktop/Final_illuminator')


META = {
    'type': 'hybrid',
    'models': {
        'Emarket': {
            'public': True,
            'params': ['sim_start','sim_end' , 'initial_supply_bids', 'initial_demand_bids'],
            'attrs': ['market_id',  'market_price',  'market_quantity', 'accepted_bids'],
            'trigger': [],
        },
    },
}
incremental_attributes = ['supply_bids', 'demand_bids']

class emarketSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'emarket_'
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
        for attr in META['models']['Emarket']['attrs']:
            for inc_attr in incremental_attributes:
                if attr.startswith(inc_attr):
                    self.incr_attr.append(attr)
        return self.meta

    def create(self, num, model, sim_start, sim_end, **model_params):
        self.start = pd.to_datetime(sim_start)
        self._entities = []

        for i in range(num):
            eid = '%s%d' % (self.eid_prefix, i)
            model_instance = emarket_model.emarket_python(sim_start, sim_end, **model_params)  #1
            self.entities[eid] = model_instance  #2
            self._entities.append({'eid': eid, 'type': model})
        return self._entities

    def step(self, time, inputs, max_advance):
        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution,
                                     unit='seconds'))  # timedelta represents a duration of time
        self.time = time
        print('from electricity market %%%%%%%%%', current_time)
        _cache = {}

        for eid, attrs in inputs.items():               # configuration possible inputs
            players_data = []

            # Loop through the dictionary and extract generator, load and storage data
            # for key, value in inputs[eid].items():
            #     for k, v in value.items():
            #         if 'supply_bids' in key:
            #             players_data.append({'input': key.split('[')[1].split(']')[0],
            #                                     'type': k.split('.')[0],
            #                                     'name': k.split('.')[1],
            #                                     'demand_bids': 0,
            #                                     'supply_bids': v})
            #         if 'demand_bids' in key:
            #             players_data.append({'input': key.split('[')[1].split(']')[0],
            #                                     'type': k.split('.')[0],
            #                                     'name': k.split('.')[1],
            #                                     'demand_bids': v,
            #                                     'supply_bids': 0})
            # players = pd.DataFrame()

            # Translator
            players_data = {}

            for key, value in inputs[eid].items():
                for k, v in value.items():
                    input_key = key.split('[')[1].split(']')[0]
                    type_key = k.split('.')[0]
                    name_key = k.split('.')[1]

                    if input_key not in players_data:
                        players_data[input_key] = {'input': input_key, 'type': type_key, 'name': name_key,
                                                   'demand_bids': None, 'supply_bids': None}
                    if 'supply_bids' in key:
                        players_data[input_key]['supply_bids'] = v
                    if 'demand_bids' in key:
                        players_data[input_key]['demand_bids'] = v

            # Check if there are any non-empty and non-zero 'supply_bids' or 'demand_bids'
            non_empty_players = [player for player in players_data.values() if
                                 (player['supply_bids'] is not None and player['supply_bids'] != 0) or (
                                             player['demand_bids'] is not None and player['demand_bids'] != 0)]

            if non_empty_players:
                players = pd.DataFrame(non_empty_players).set_index('input').sort_index()
            else:
                players = pd.DataFrame()

            _cache[eid] = self.entities[eid].emarket(current_time, players)

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
                    elif attr == 'market_price':
                        try:
                            data[eid][attr] = self._cache[eid]['market_price']
                        except TypeError or KeyError:
                            data[eid][attr] = 0
                    elif attr == 'market_quantity':
                        try:
                            data[eid][attr] = self._cache[eid]['market_quantity']
                        except TypeError or KeyError:
                            data[eid][attr] = 0
                    elif attr == 'accepted_bids':
                        try:
                            data[eid][attr] = self._cache[eid]['accepted_bids']
                        except TypeError or KeyError:
                            data[eid][attr] = None
        return data
def main():
    mosaik_api.start_simulation(emarketSim(), 'Emarket-Illuminator')
if __name__ == '__main__':
    main()
