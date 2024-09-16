
import itertools
import mosaik_api
#import PV.PV_model as PV_model
try:
    import Models.PV.pv_model as PV_model
except ModuleNotFoundError:
    import pv_model as PV_model
else:
    import Models.PV.pv_model as PV_model
import pandas as pd
import itertools

meta = {
    'type': 'event-based', #if reading from a csv file then it is time based
    'models': {
        'PVset': {
            'public': True,
            'params': ['panel_data',
                       'm_tilt','m_az', 'cap', 'sim_start', 'output_type'],
            # and are attrs the specific outputs we want from the code? to connect with other models
            'attrs': ['pv_id', 'G_Gh', 'G_Dh', 'G_Bn', 'Ta', 'hs', 'FF', 'Az', 'pv_gen', 'total_irr'],
        },
    },
}

class PvAdapter(mosaik_api.Simulator):
    def __init__(self):
        super(PvAdapter, self).__init__(meta)
        self.eid_prefix='pv_'
        self.entities = {}  # every entity that we create of PV gets stored in this dictionary as a list
        self.mods = {}
        self._cache = {}  #we store the final outputs after calling the python model (#PV1) here.

    def init(self, sid, time_resolution):
        # print('hi, you have entered init')  # working (20220524)
        self.time_resolution = time_resolution
        # print('Exited init os SimAPI')  # working (20220524)
        return self.meta

    def create(self, num, model, sim_start, **model_params):
        # print('hi, you have entered create of SimAPI')  # working (20220524)
        self.start = pd.to_datetime(sim_start)
        entities = []
        for i in range (num):
            eid = '%s%d' % (self.eid_prefix, i)

            # we are creating an instance for PV and call the python file for that. **model_params refers to the
            # parameters we have mentioned above in the META. New instance will have those parameters.
            model_instance = PV_model.PV_py_model(**model_params)
            self.entities[eid] = model_instance
            entities.append({'eid': eid, 'type': model})
        # print(entities)
        return entities

    def step(self, time, inputs, max_advance):
        # in this method, we call the python file at every data interval and perform the calculations.
        current_time = (self.start + pd.Timedelta(time * self.time_resolution,
                                                  unit='seconds'))  # timedelta represents a duration of time
        print('from pv %%%%%%%%%', current_time)
        # print('#inouts: ', inputs)
        for eid, attrs in inputs.items():
            # print('#eid: ', eid)
            # print('#attrs: ', attrs)
            # and relate it with the information in mosaik document.
            v = []  # we create this empty list to hold all the input values we want to give since we have more than 2
            for attr, vals in attrs.items():

                # print('#attr: ', attr)
                # print('#vals: ', vals)
                # inputs is a dictionary, which contains another dictionary.
                # value of U is a list. we need to combine all the values into a single list. But is we just simply
                #   append them in v, we have a nested list, hence just 1 list. that creates a problem as it just
                #   gives all 7 values to only sun_az in the python model and we get an error that other 6 values are missing.
                u = list(vals.values())
                # print('#u: ', u)
                v.append(u)  # we append every value of u to v from this command.
            # print('#v: ', v)

            # the following code helps us to convert the nested list into a simple plain list and we can use that simply
            v_merged = list(itertools.chain(*v))
            # print('#v_merged: ', v_merged)
            self._cache[eid] = self.entities[eid].connect(v_merged[0], v_merged[1], v_merged[2], v_merged[3],
                                                          v_merged[4], v_merged[5], v_merged[6]) # PV1
            # print(self._cache)
            # print('# cache[eid]: ', self._cache[eid])
    # the following code desnt work because it just put one value 7 times :/! Dumb move
                    # self._cache[eid] = self.entities[eid].connect(u, u, u, u, u, u, u)
        return None

    def get_data(self, outputs):
        data = {}

        # to write the data in an external file, we use this method. This API inturn calls a file within Mosaik
        # which handles the writing of the outputs provided the attrs are present in the base python model file you made

        for eid, attrs in outputs.items():
            # model = self.entities[eid]
            # data['time'] = self.time
            data[eid] = {}

            for attr in attrs:
                # if we want more values to print in the output file, mimic the below for new attributes and make sure
                # those parameters are present in the re_params in the python file of the model
                if attr == 'pv_gen':
                    data[eid][attr] = self._cache[eid]['pv_gen']
                elif attr == 'total_irr':
                    data[eid][attr] = self._cache[eid]['total_irr']
        return data

def main():
    mosaik_api.start_simulation(PvAdapter(), 'PV-Illuminator')
if __name__ == '__main__':
    main()
