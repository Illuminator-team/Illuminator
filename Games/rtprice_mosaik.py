import mosaik_api
#import RTprice.rtprice_model as rtprice_model
try:
    import Games.rtprice_model as rtprice_model
except ModuleNotFoundError:
    import rtprice_model as rtprice_model
else:
    import Games.rtprice_model as rtprice_model

import pandas as pd

META = {
    'type': 'hybrid',
    'models': {
        'RTprice': {
            'public': True,
            'params': ['sim_start', 'sim_end'],
            'attrs': ['rtprice_id', 'buy_price', 'sell_price', 'price'],
            'trigger': [],
        },
    },
}

incremental_attributes = ['buy', 'sell']

class rtpriceSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'rtprice_'
        self.entities = {}
        self._cache = {}
        self.time = 0

    def init(self, sid, time_resolution, step_size=900):
        self.step_size = step_size
        self.time_resolution = time_resolution
        return self.meta

    def create(self, num, model, sim_start, **model_params):
        self.start = pd.to_datetime(sim_start)
        entities = []

        for i in range(num):
            eid = '%s%d' % (self.eid_prefix, i)
            model_instance = rtprice_model.rtprice_python(**model_params)
            self.entities[eid] = model_instance
            entities.append({'eid': eid, 'type': model})
        return entities

    def step(self, time, inputs, max_advance):
        self.time = time
        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution,
                                     unit='seconds'))
        print('from rtprice %%%%%%%%%%%', current_time)
        for eid, attrs in inputs.items():               # configuration possible inputs
            _cache = {}
            buy = {}
            sell = {}
            buy_price = 0
            sell_price = 0

            # Loop through the dictionary and extract attributes
            for key, value in inputs[eid].items():
                for k, v in value.items():
                    if 'buy_price' in key:
                        buy_price = v
                    elif 'sell_price' in key:
                        sell_price = v
                    elif 'buy' in key:
                        buy[k.split('.')[1]] = v
                    elif 'sell' in key:
                        sell[k.split('.')[1]] = v

            _cache[eid] = self.entities[eid].clear(current_time, buy_price, sell_price, buy, sell)

        self._cache = _cache
        return self.time + self.step_size


    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            for attr in attrs:
                if attr == 'buy_price':
                    data[eid][attr] = self._cache[eid]['buy_price']
                if attr == 'sell_price':
                    data[eid][attr] = self._cache[eid]['sell_price']
        return data
def main():
    mosaik_api.start_simulation(rtpriceSim(), 'rtprice Simulator')
    
if __name__ == "__main__":
    main()
