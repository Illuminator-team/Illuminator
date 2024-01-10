from typing import List, Dict, Union, Any

import mosaik_api
import loadmodel
import pandas as pd
import datetime

meta = {
    'type': 'time_based',
    'models': {
        'LoadModel': {
            'public': True,
            'params': [
                'num',
                'sim_start',  # (str)The start time for the simulation: "YYYY-MM-DD HH:SS"
                'pf_data',
            ],
            'attrs': [
                'P_out',  # Active power [W] of each load
                'name',
            ]
        }
    }
}


class LoadSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(meta)
        self.time_resolution = 1
        self.entities = {}
        self.time = 0
        self.cachedata = {}
        self._timeset=0
        self.model = None
        self.load_id=None


    def init(self, sid, time_resolution=15*60):#time_resolution is senconds

        self.time_resolution = time_resolution
        print("The time_resolution of the load is:", self.time_resolution)
        return self.meta

    def create(self, num, model, sim_start, pf_data):
        #pf_data(dataframe) sim_start(str),num(len(entity)
        entities=[]
        # pf, time_resolution, node_name, load_name
        self.load_id=pf_data.iloc[0].index[1:].to_list()
        self._timeset=pd.to_datetime(sim_start)

        # models=pf.iloc[0].index[1:].to_list()
        # model_series=pd.Series([2,1],index=["node_1,load_1","node_2,load_2"])
        for i in range(num):
            load_instance=loadmodel.LoadModel(pf_data, self.load_id[i])
            self.entities[self.load_id[i]]=load_instance
            entities.append({'id':self.load_id[i],'type':model})
        return entities

    def step(self, time, inputs, max_advance):#time is iteration steps.
        minutes = int(time * self.time_resolution // 60)
        self.time = self._timeset + datetime.timedelta(minutes=minutes)
        cache = {}
        # self.time = self.time + datetime.timedelta(minutes=self.time_resolution )
        for eid, model_instance in self.entities.items():
            if eid in inputs:
                attrs=inputs[eid]
                for attr, values in attrs.items():
                    if attr=='P_out':
                        model_instance.P_out=values
                        print('the p_out of ',model_instance.name,"is changed!")

            data = model_instance.get(self.time)
            for hid, d in enumerate(data):
                cache['%s' % self.load_id[hid]] = d
            self._cache = cache

        return time+1

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            model = self.entities[eid]
            data['time'] = self.time
            data[eid] = {}
            for attr in attrs:
                if attr not in self.meta['models']['ExampleModel']['attrs']:
                    raise ValueError('Unknown output attribute: %s' % attr)
                # Get model.val or model.delta:
                data[eid][attr] = getattr(model, attr)
        return data


def main():
    return mosaik_api.start_simulation(LoadSim())


# if __name__ =='__main__':
#     datafile = 'demo_lv_grid.csv'
#     pf_load = pd.read_csv(datafile)
#     START = '2014-01-01 00:00:00'
#     sim = model_mosaikapi.LoadSim()
#     sim.init('sid')
#     eneti = sim.create(sim_start=START, pf_data=pf_load)
