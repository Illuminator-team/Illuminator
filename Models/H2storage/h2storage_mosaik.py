import mosaik_api
#import H2storage.h2storage_model as hydrogen_storage
try:
    import Models.H2storage.h2storage_model as hydrogen_storage
except ModuleNotFoundError:
    import h2storage_model as hydrogen_storage
else:
    import Models.H2storage.h2storage_model as hydrogen_storage
import pandas as pd

META = {
    'type': 'event-based',
        # storage is an event based event because the event here is a wind speed. It doesnt purely run because of time interval, I think.
        # if I put it to time-based, there is type error:
        # File "C:\Users\ragha\AppData\Local\Programs\Python\Python310\lib\site-packages\mosaik\scheduler.py", line 405, in step
        #     sim.progress_tmp = next_step - 1
        # TypeError: unsupported operand type(s) for -: 'NoneType' and 'int'

    'models': {
        'compressed_hydrogen': {
            'public': True,
            'params': ['sim_start', 'initial_set', 'h2_set'],
            'attrs': ['h2storage_id',
                      'h2_in',  # in the python file this existed in the re_params.
                      'h2_stored',  # re_params returns values from the python file, so we need to have it here so that mosaik
                      # can connect them and enter the values.
                      'h2_soc', 'mod', 'flag', 'time', 'h2storage_soc_max', 'h2storage_soc_min', 'h2_given', 'h2_out'],
            'trigger': [],
        },
    },
}

class compressedhydrogen(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'h2storage_'  # every entity that we create will start with 'wind_'
        self.entities = {}  # we store the model entity of our technology model
        self._cache = {}  # used in the step function to store the values after running the python model of the technology
        # self.start_date = None
        self.soc = {}
        self.flag = {}
        self.h2_stored = {}

    def init(self, sid, time_resolution):
        # print('hi, you have entered init')  # working (20220524)
        self.time_resolution = time_resolution
        # print('Exited init os SimAPI')  # working (20220524)
        return self.meta

    def create(self, num, model, initial_set, h2_set, sim_start):
        self.start = pd.to_datetime(sim_start)
        # next_eid=len(self.model)
        self._entities = []
        # for i in range(next_eid,next_eid+num):

        # num is the number of models of battery we want.
        for i in range(num):
            # we provide an ID to each entity we create. %s%d will be replaced by the values of eid_prefix and i
            self.eid = '%s%d' % (self.eid_prefix, i)


            h2storage_instance = hydrogen_storage.hydrogenstorage_python(initial_set, h2_set)

            self.entities[self.eid] = h2storage_instance
            self.soc[self.eid] = initial_set['initial_soc']
            self.flag[self.eid] = h2_set['flag']
            self._entities.append({'eid': self.eid, 'type': model, 'rel': [], })
            # print(self._entities)

        return self._entities

    def step(self, time, inputs, max_advance):
        self.time = time
        current_time = (self.start + pd.Timedelta(time * self.time_resolution, unit='seconds'))
        # print('from battery %%%%%%%%', current_time)
        for eid, attrs in inputs.items():
            # print(eid)
            # print(attrs)

            # In {'p_ask': {'CSVB-0.BATTEYP_0': 0.5}}, 'p_ask' is the attr, and 0.5 is vals
            for attr, vals in attrs.items():
                if attr == 'h2_in':
                    # of all the values present in the dictionary, we make a list out of it.
                    # the [0] means we are calling the 0th entity in that list
                    h2_in = list(vals.values())[0]
                    print('#hydrogen h2_in input:', h2_in)

                elif attr == 'h2_out':
                    h2_out = list(vals.values())[0]


            self._cache[eid] = self.entities[eid].output_h2(h2_in, h2_out, self.soc[eid])

            self.soc[eid] = self._cache[eid]['h2_soc']
            self.flag = self._cache[eid]['flag']
            self.h2_stored[eid] = self._cache[eid]['h2_stored']
            # print('h2 flag', self.flag)
            print('------------------------->', self.h2_stored)
            # yield self.mosaik.set_data(self._cache)

            # self.battery_flag[eid]=self._cache[eid]['flag']
            soc_val = list(self.soc.values())
            h2_soc = soc_val[0]  # this is so that the value that battery sends is dictionary and not a dictionary of a dictionary.
            out = yield self.mosaik.set_data({'H2storage-0': {'Controller-0.ctrl_0': {'h2_soc': h2_soc}}})  # this code is supposed to hold the soc value and

        return None

    def get_data(self, outputs):
        data = {}
#         # self.test.append(self.flag)  # if we do this code, then we end up with a list which increases with each step. Duh!
#         # try:
#         #     # the following code takes the vale at -2 position in the list. The -2 vale of the list represents the value of the previous step
#         #     self.pflag = self.test[-2]  # first python tries this line of code. If it doesnt work then it follows the code in except.
#         # except:
#         #     self.pflag = self.flag
#
        for eid, attrs in outputs.items():
            model = self.entities[eid]
            # data['time'] = self.time
            data[eid] = {}
            for attr in attrs:
                # data[eid][attr] = getattr(model, attr)  # this line of a code is short form for the following code which is commented out
                if attr == 'h2_soc':
                    data[eid][attr] = self._cache[eid]['h2_soc']
                elif attr == 'mod':
                    data[eid][attr] = self._cache[eid]['mod']
                elif attr == 'h2storage_id':
                    data[eid][attr] = eid
                elif attr == 'flag':
                    data[eid][attr] = self._cache[eid]['flag']
                elif attr == 'h2_stored':
                    data[eid][attr] = self._cache[eid]['h2_stored']
                elif attr == 'h2_given':
                    data[eid][attr] = self._cache[eid]['h2_given']
                elif attr == 'h2_consumed':
                    data[eid][attr] = self._cache[eid]['h2_consumed']
                # if eid in self._cache:
                #     data['time'] = self.time
                #     data.setdefault(eid, {})[attr] = self._cache[eid][attr]

        return data


def main():
    mosaik_api.start_simulation(compressedhydrogen(), 'H2storage-Simulator')
    
if __name__ == "__main__":
    main()
    
