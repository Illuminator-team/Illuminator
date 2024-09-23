import mosaik_api
import pandas as pd

try:
    import Models.LoadinNetSim.model as Loadmodelset
except ModuleNotFoundError:
    import LoadinNetSim.model as Loadmodelset
else:
    import Models.LoadinNetSim.model as Loadmodelset

meta={
    'type':'time-based',
    'models':{
        'Loadset':{
            'public':True,
            'params':[
                'sim_start', #time start(str)
                'data_info',#data_info = {'start': '2015-02-01 00:00:00', 'resolution': 15 , 'unit': 'W'}
                'profile_file', #profile name
            ],
            'attrs':[],
        },
        'Load':{
            'public':False,
            'params':[],
            'attrs':[
                'P_out',
                'load_num',
                'node_id',

            ],
        },
    },
}

def eid(lid):
    return 'Load_create_%s' %lid


class LoadholdSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(meta)

        self.time_resolution=None
        self.model=None
        self.loads_by_eid={}
        self._file_cache={}
        self._offset=0
        self._cache={}


    def init(self,sid,time_resolution):
        self.time_resolution=float(time_resolution)
        return self.meta

    def create(self, num, model, sim_start,data_info,profile_file):
        if num != 1 or self.model:
            raise ValueError('Can only create one set of loads.')
        if profile_file.endswith('csv'):
            pf=pd.read_csv(profile_file)
        else:
            pf=pd.read_excel(profile_file)

        self.model=Loadmodelset.LoadModel(data_info,pf)
        self.loads_by_eid={
            eid(i):load for i, load in enumerate(self.model.loads)
        }
        # A time offset in minutes from the simulation start to the start
        # of the profiles.
        self._offset = self.model.get_delta(sim_start)
        return[{
            'eid':'Loadset_0',
            'type':'Loadset',
            'rel':[],
            'children':
                [{'eid': eid(i),
                'type':'Load',
                'rel':[],}for i,_ in enumerate(self.model.loads)],
        }]

    def step(self,time,inputs,max_advance):
        # "time" has self.time_resolution (seconds per integer step).
        # Convert to minutes and add the offset if sim start > start date of
        # the profiles.
        minutes=int(time*self.time_resolution // 60)
        minutes_offset=minutes+self._offset
        cache={}
        data=self.model.get(minutes_offset)
        #print(data)
        for hid, d in enumerate(data):
            cache[eid(hid)]=d
        self._cache=cache
        return int((minutes + self.model.resolution) * 60
                   / self.time_resolution)

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            for attr in attrs:
                if attr == 'P_out':
                    val = self._cache[eid]
                else:
                    val = self.loads_by_eid[eid][attr]
                data[eid][attr] = val
        return data

def main():
    return mosaik_api.start_simulation(LoadholdSim(),'Loadholdset simulation')























