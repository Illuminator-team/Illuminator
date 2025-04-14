import mosaik_api

try:
    import Models.Grid_Connection.grid_connection as grid_connection
except ModuleNotFoundError:
    import grid_connection as grid_connection
else:
    import Models.Grid_Connection.grid_connection as grid_connection

import pandas as pd

META = {
    'type': 'time-based',

    'models': {
        'grid_connection_model': {
            'public': True,
            'params': ['sim_start', 'connection_capacity', 'tolerance_limit', 'critical_limit'],
            'attrs': ['grid_connection_id', 'flag_critical', 'flag_warning', 'dump'],
            'trigger': [],
        },
    },
}


class grid_connection_Sim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'grid_connection_'
        self.entities = {}  # we store the model entity of our technology model
        self._cache = {}  # used in the step function to store the values after running the python model of the technology
        self.time = 0
        # self.start_date = None

    # the following API call is will be called only once when we initiate the model in the scenario file.
    # we can use this to pass additional initialization tasks

    def init(self, sid, time_resolution):

        self.time_resolution = time_resolution

        return self.meta

    def create(self, num, model, sim_start, **model_params):

        self.start = pd.to_datetime(sim_start)
        # print(type(self.entities))
        # next_eid = len(self.entities)
        # print('from create of SimAPI:', next_eid)
        entities = []

        for i in range(num):
            eid = '%s%d' % (self.eid_prefix, i)
            model_instance = grid_connection.grid_connection_python(**model_params)
            self.entities[eid] = model_instance
            entities.append({'eid': eid, 'type': model})
        return entities

    def step(self, time, inputs, max_advance):
        self.time = time
        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution,
                                     unit='seconds'))  # timedelta represents a duration of time
        print('from grid connection %%%%%%%%%%%', current_time)

        for eid, attrs in inputs.items():

            for attr, vals in attrs.items():
                self._cache[eid] = self.entities[eid].check_limits(list(vals.values())[0])
        return time + 1

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            for attr in attrs:
                if attr == 'flag_critical':
                    data[eid][attr] = self._cache[eid]['flag_critical']
                    data['time'] = self.time
                if attr == 'flag_warning':
                    data[eid][attr] = self._cache[eid]['flag_warning']
                    data['time'] = self.time
        return data


def main():
    mosaik_api.start_simulation(grid_connection_Sim(), 'Grid Connection Simulator')


if __name__ == "__main__":
    main()