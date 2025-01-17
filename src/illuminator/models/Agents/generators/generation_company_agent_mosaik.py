import mosaik_api
try:
    import Education_Financial_Balance.Generation_Companies.generation_company_agent as gen_agent
except ModuleNotFoundError:
    import generation_company_agent as gen_agent
else:
    import Education_Financial_Balance.Generation_Companies.generation_company_agent as gen_agent

import pandas as pd

META = {
    'type': 'time-based',

    'models': {
        'genagent': {
            'public': True,
            'params': ['sim_start', 'portfolio', 'company', 'output_type', 'automated_bids', 'bids_manual'],
            'attrs': ['gen_id', 'bids', 'profit'],
            'trigger': [],
        },
    },
}


class GenAgentSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'gen_agent_'  # every entity that we create will start with 'gen_agent_'
        self.entities = {}  # we store the model entity of our technology model
        self._cache = {}  # used in the step function to store the values after running the python model of the technology
        self.time = 0
        # self.start_date = None

    # the following API call is will be called only once when we initiate the model in the scenario file.
    # we can use this to pass additional initialization tasks

    def init(self, sid, time_resolution):
        self.time_resolution = time_resolution
        self.sid = sid
        return self.meta

    def create(self, num, model, sim_start, **model_params):
        # print('hi, you have entered create of SimAPI')  # working (20220524)
        self.start = pd.to_datetime(sim_start)
        # print(type(self.entities))
        next_eid = len(self.entities)
        # print('from create of SimAPI:', next_eid)
        entities = []
        # print(next_eid)  # working (20220524)

        for i in range(next_eid, num + next_eid):
            eid = '%s%d' % (self.eid_prefix, i)
            #print(eid)
            model_instance = gen_agent.GenerationCompanyAgent(**model_params)
            self.entities[eid] = model_instance
            entities.append({'eid': eid, 'type': model})
        #print(self.entities)
        #print(f"entities:{entities}")
        return entities


    def step(self, time, inputs, max_advance):
        self.time = time
        #print('Entered step function Gen Agent')
        #print(inputs.items())
        for eid, model_instance in self.entities.items():
            #print('entered if bid')
            self._cache[eid] = self.entities[eid].bid()
            ##if attr == 'overbid':
            #self._cache[eid] = self.entities[eid].overbid
        return time + 1


    def get_data(self, outputs):
        data = {}


        for eid, attrs in outputs.items():
            model = self.entities[eid]
            # data['time'] = self.time
            data[eid] = {}
            #print(self._cache)
            #print(eid)
            for attr in attrs:
                #data[eid][attr] = getattr(model, attr)
                if attr == 'bids':
                    data[eid][attr] = self._cache[eid]['bids']
                #elif attr == 'overbid':
                   # data[eid][attr] = self._cache[eid]['overbid']
                elif attr == 'profit':
                    data[eid][attr] = self._cache[eid]['profit']

        return data


def main():
    mosaik_api.start_simulation(GenAgentSim(), 'Generation-Company-Simulator')


if __name__ == "__main__":
    main()