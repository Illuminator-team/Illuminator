import mosaik_api
import numpy as np
import pandas as pd

#import Fuelcell.fuelcell_model as fc
try:
    import Models.Fuelcell.fuelcell_model as fc
except ModuleNotFoundError:
    import fuelcell_model as fc
else:
    import Models.Fuelcell.fuelcell_model as fc


meta = {
    'type': 'event-based',
    #wind is an event based event because the event here is a wind speed. It doesnt purely run because of time interval, I think.
    # if I put it to time-based, there is type error:
    # File "C:\Users\ragha\AppData\Local\Programs\Python\Python310\lib\site-packages\mosaik\scheduler.py", line 405, in step
    #     sim.progress_tmp = next_step - 1
    # TypeError: unsupported operand type(s) for -: 'NoneType' and 'int'

    'models': {
        'fuelcellmodel': {
            'public': True,
            'params': ['sim_start', 'eff'],
            'attrs': ['h2_consume', 'fc_gen'],
            'trigger': [],
        },
    },
}

class FuelCellSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(meta)
        self.eid_prefix = 'fc_'  # every entity that we create will start with 'wind_'
        self.entities = {}  # we store the model entity of our technology model
        self._cache = {}  # used in the step function to store the values after running the python model of the technology
        # self.start_date = None
        self.fc_gen = {}

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

        for i in range (num):
            eid = '%s%d' % (self.eid_prefix, i)
            # print('########### FC id', eid)
            model_instance = fc.fuelcell_python(**model_params)
            self.entities[eid] = model_instance
            entities.append({'eid': eid, 'type': model})
        return entities

    def step(self, time, inputs, max_advance):
        self.time = time
        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution, unit='seconds'))  # timedelta represents a duration of time
        print('from fc %%%%%%%%%%', current_time)

        for eid, attrs in inputs.items():
            # raghav: Inputs come from a controller. This happens when you define the connection in the scenario file
            # print(eid)
            # print(attrs)
            for attr, vals in attrs.items():
                if attr == 'h2_consume':
                    h2_consume = list(vals.values())[0]
                    # print(h2_consume)
                    self._cache[eid] = self.entities[eid].output(h2_consume)
                    # in the above line, we have called our entity of fuelcell model we created in create followed by a
                    # definition 'output. Since self.entities = model_instance and model instance calls out fuelcell
                    # python model, so in this step we are called the function 'output' and give it a value for h2_in.
                    # This step makes the python file run and do the calculations for us of wind_gen.
                    # print(self._cache[eid])
                    # self.fc_gen[eid] = self._cache[eid]['fc_gen']
                    # fc_gen_val = list(self.fc_gen.values())
                    # fc_gen = fc_gen_val[0]
                    # print('+++++++++++++++++++++', fc_gen)
                    # out = yield self.mosaik.set_data({'fc-0': {'ctrl-0.ctrl_0': {'fc_gen': fc_gen}}})
        return None

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            for attr in attrs:
                # if we want more values to print in the output file, mimic the below for new attributes and make sure
                # those parameters are present in the re_params in the python file of the technology
                if attr == 'fc_gen':
                    data[eid][attr] = self._cache[eid]['fc_gen']

        return data

def main():
    mosaik_api.start_simulation(FuelCellSim(), 'FuelCell Simulator')

if __name__ == "__main__":
    main()
