from collections import namedtuple

import mosaik_api
import numpy as np
import pandas as pd

#import Wind.Wind_model as Wind_model


try:
    import Models.Wind.Wind_model as Wind_model
except ModuleNotFoundError:
    import Wind_model as Wind_model
else:
    import Models.Wind.Wind_model as Wind_model

META = {
    'type': 'event-based',
    #wind is an event based event because the event here is a wind speed. It doesnt purely run because of time interval, I think.
    # if I put it to time-based, there is type error:
    # File "C:\Users\ragha\AppData\Local\Programs\Python\Python310\lib\site-packages\mosaik\scheduler.py", line 405, in step
    #     sim.progress_tmp = next_step - 1
    # TypeError: unsupported operand type(s) for -: 'NoneType' and 'int'

    'models': {
        'windmodel': {
            'public': True,
            'params': ['p_rated', 'u_rated', 'u_cutin', 'u_cutout', 'cp', 'sim_start', 'output_type', 'diameter'],
            'attrs': ['wind_id',
                      'wind_gen',  # in the python file this existed in the re_params.
                          # re_params returns values from the python file, so we need to have it here so that mosaik
                          # can connect them and enter the values.
                      'u'],
        },
    },
}


class WindSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'wind_'  # every entity that we create will start with 'wind_'
        self.entities = {}  # we store the model entity of our technology model
        self._cache = {}  # used in the step function to store the values after running the python model of the technology
        # self.start_date = None

    # the following API call is will be called only once when we initiate the model in the scenario file.
    # we can use this to pass additional initialization tasks
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
            # print ('123checkkkkkkkkkkkkkkk', eid)
            model_instance = Wind_model.wind_py_model(**model_params)
            self.entities[eid] = model_instance
            entities.append({'eid': eid, 'type': model})
        return entities

    def step(self, time, inputs, max_advance):

        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution, unit='seconds')) # timedelta represents a duration of time
        print('from wind %%%%%%%%%%', current_time)

        for eid, attrs in inputs.items():
            # raghav: Inputs come from a CSV file which needs to be read by a Mosaik # CSV reader -
            # and it gives the output in a manner we want. The output from the CSV file will be the Input here.
            # they are connected in the scenario file. ##W1 (see W1 in comments in scenario file to understand)
            # print(eid)
            # print(attrs)
            for attr, vals in attrs.items():
                if attr == 'u':
                    u = list(vals.values())[0]
                    # print(u)
                    self._cache[eid] = self.entities[eid].generation(u)  #not necessary to have u in brackets. It is not
                    # necessary to keep the same name as the one in python file

                    # in the above line, we have called our entity of wind model we created in create followed by a
                    # definition 'generation'. Since self.entities = model_instance and model instance calls out wind
                    # python model, so in this step we are called the function 'generation' and give it a value for u.
                    # This step makes the python file run and do the calculations for us of wind_gen.
                    # print(self._cache[eid])
                    # [wind_gen:,soc:,flag:]
                    # self.soc[eid] = self._cache[eid]['soc']
                    # self.battery_flag[eid]=self._cache[eid]['flag']
                    # print(self._cache)

        return None
        # # CURRENTLY THE INPUT IS THE WIND SPEED FILE BUT IT CAN BE CHANGED TO THE SUM OF pv AND wind AND THE grid load
        # print (' entered STEP of SimAPI')
        # self.time=time
        #
        # for eid, model_instance in self.entities.items():
        #     for i in wind_data:
        #         model_instance.u = i
        #         print(model_instance[0])
        # print('Exited STEP of SimAPI')
        # return time + 300

    def get_data(self, outputs):
        data={}
        for eid, attrs in outputs.items():
            # model = self.entities[eid]
            # data['time'] = self.time
            data[eid]={}
            for attr in attrs:
                # if we want more values to print in the output file, mimic the below for new attributes and make sure
                # those parameters are present in the re_params in the python file of the technology
                if attr == 'wind_gen':
                    data[eid][attr] = self._cache[eid]['wind_gen']
                elif attr == 'u':
                    data[eid][attr] = self._cache[eid]['u']

        return data



def main():
    return mosaik_api.start_simulation(WindSim(), 'WindEnergy Simulator')

if __name__ == "__main__":
    main()
