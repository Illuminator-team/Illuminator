"""
Mosaik interface for operator model

"""
import mosaik_api

try:
    import Education_Financial_Balance.Operator.operator as operator
except ModuleNotFoundError:
    import operator as operator
else:
    import Education_Financial_Balance.Operator.operator as operator

import pandas as pd
from Education_Financial_Balance.Operator.operator import Operator_Market

META = {
    'type': 'time-based',
    'models': {
        'operator_market': {
            'public': True,
            'params': ['sim_start','demand', 'companies'], # to add later 'overbid_penalty'
            'attrs': ['bids','market_clearing_price', 'results'], # to add later 'overbid'
        },
    },
}

class OperatorSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'operator_'
        self.entities = {}
        self._cache = {}
        self.data = {}
        self.time = 0

        #self.models = dict()  # contains the model instances
        #self.sid = None
        #self.eid_prefix = 'Operator_'

    def init(self, sid, time_resolution):
        self.time_resolution = time_resolution
        self.sid = sid
        return self.meta

    def create(self, num, model, sim_start, **model_params):
        self.start = sim_start
        self._entities = []
        for i in range(num):
            eid = '%s%d' % (self.eid_prefix, i)
            model_instance = operator.Operator_Market(**model_params)  # 1
            self.entities[eid] = model_instance  # 2
            self._entities.append({'eid': eid, 'type': model})

        return self._entities

    def step(self, time, inputs, max_advance):
        self.time = time
        for eid, attrs in inputs.items():
            #print(f"attributes check {attrs.items()}")
            for attr, vals in attrs.items():
                self._cache[eid] = self.entities[eid].calculate_balance(list(vals.values()))
        return time + 1



