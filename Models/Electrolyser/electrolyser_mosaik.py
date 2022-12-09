import mosaik_api
#import Electrolyser.electrolyser_model as electrolyser_model
try:
    import Models.Electrolyser.electrolyser_model as electrolyser_model
except ModuleNotFoundError:
    import electrolyser_model as electrolyser_model
else:
    import Models.Electrolyser.electrolyser_model as electrolyser_model

import pandas as pd

META = {
    'type': 'event-based',
    # wind is an event based event because the event here is a wind speed. It doesnt purely run because of time interval, I think.
    # if I put it to time-based, there is type error:
    # File "C:\Users\ragha\AppData\Local\Programs\Python\Python310\lib\site-packages\mosaik\scheduler.py", line 405, in step
    #     sim.progress_tmp = next_step - 1
    # TypeError: unsupported operand type(s) for -: 'NoneType' and 'int'

    'models': {
        'electrolysermodel': {
            'public': True,
            'params': ['sim_start', 'eff', 'fc_eff', 'resolution'],
            'attrs': ['electro_id','h2_gen', 'flow2e', 'fc_eff', 'h2_out',],
            'trigger': [],
        },
    },
}


class ElectrolyserSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'electro_'  # every entity that we create will start with 'wind_'
        self.entities = {}  # we store the model entity of our technology model
        self._cache = {}  # used in the step function to store the values after running the python model of the technology
        # self.start_date = None

    def init(self, sid, time_resolution):
        # print('hi, you have entered init')  # working (20220524)
        self.time_resolution = time_resolution
        # print('Exited init os SimAPI')  # working (20220524)
        return self.meta

    def create(self, num, model, sim_start, **model_params):
        # print('hi, you have entered create of SimAPI')  # working (20220524)
        self.start = pd.to_datetime(sim_start)
        # print(type(self.entities))
        # next_eid = len(self.entities)
        # print('from create of SimAPI:', next_eid)
        entities = []
        # print(next_eid)  # working (20220524)

        for i in range(num):
            eid = '%s%d' % (self.eid_prefix, i)
            model_instance = electrolyser_model.electrolyser_python(**model_params)
            self.entities[eid] = model_instance
            entities.append({'eid': eid, 'type': model})

        return entities

    def step(self, time, inputs, max_advance):

        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution,
                                     unit='seconds'))  # timedelta represents a duration of time
        # print('from electrolyser %%%%%%%%%',current_time)

        for eid, attrs in inputs.items():
            # print(eid)
            # print(attrs)
            for attr, vals in attrs.items():
                if attr == 'flow2e':
                    flow2e = list(vals.values())[0]
                    self._cache[eid] = self.entities[eid].electrolyser(flow2e)  # not necessary to have u in brackets. It is not

        return None

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            for attr in attrs:
                if attr == 'h2_gen':
                    data[eid][attr] = self._cache[eid]['h2_gen']
                # if attr == 'h2_out':
                #     data[eid][attr] = self._cache[eid]['h2_out']
        return data


def main():
    mosaik_api.start_simulation(ElectrolyserSim(), 'Electrolyser-Simulator')
    
if __name__ == "__main__":
    main()
    
