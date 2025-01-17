import mosaik_api
import pandas as pd
from Agents.prosumer_S_model import *

try:
    import Agents.prosumer_model as prosumer_model
except ModuleNotFoundError:
    import prosumer_model as prosumer_model
else:
    import Agents.prosumer_model as prosumer_model
import sys
sys.path.insert(1,'/home/illuminator/Desktop/Final_illuminator')

META = {
    'type': 'hybrid',
    'models': {
        'Prosumer': {
            'public': True,
            'params': ['sim_start', 'forecasted_data', 'metrics', 'strategy'],
            'attrs': ['agent_id', 'em_supply_bids', 'em_demand_bids', 'em_accepted_bids', 'p2em', 'p2p2p',
                      'p2p_supply_offers', 'p2p_demand_requests', 'p2p_transactions', 'rt_buy', 'rt_sell'],
            'trigger': [],
        },
    },
}
incremental_attributes = ['generator', 'demand', 'storage']

class prosumerSim(mosaik_api.Simulator):
    def __init__(self) -> None:
        """
        Inherits the Mosaik API Simulator class and is used for python based simulations.
        For more information properly inheriting the Mosaik API Simulator class please read their given documentation.

        ...

        Attributes
        ----------
        self.meta : dict
            Contains metadata of the control sim such as type, models, parameters, attributes, etc.. Created via prosumerSim's parent class.
        self.eid_prefix : string
            The prefix with which each entity's name/eid will start
        self.entities : dict
            The stored model entity of the technology model
        self._cache : doct
            Used in the step function to store the values after running the python model of the technology
        """
        super().__init__(META)
        self.eid_prefix = 'prosumer_'
        self.entities = {}
        self._cache = {}

    def init(self, sid:str, time_resolution:float, step_size:int=900) -> dict:
        """
        Because this method has an additional sim_param, step_size, it overrides the `init` method defined in mosaik_api.Simulator.

        ...

        Parameters
        ----------
        sid : str
            The String ID of the class
        time_resolution : float
            ???
        step_size : int
            The size of the time step. The unit is arbitrary, but it has to be consistent among all simulators used in a simulation.

        Returns
        -------
        self.meta : dict
            The metadata of the class
        """
        self.step_size = step_size
        self.sid = sid
        self.time_resolution = time_resolution
        self.time = 0
        self.incr_attr = []
        for attr in META['models']['Prosumer']['attrs']:
            for inc_attr in incremental_attributes:
                if attr.startswith(inc_attr) and inc_attr[-1] == ']':
                    self.incr_attr.append(attr)
        return self.meta

    def create(self, num:int, model:str, sim_start:str, strategy:str, **model_params) -> list:
        """
        Create `num` instances of `model` using the provided `model_params`.

        ...

        Parameters
        ----------
        num : int
            The number of model instances to create.
        model : str
            `model` needs to be a public entry in the simulator's ``meta['models']``.
        sim_start : str
            Date and time (YYYY-MM-DD hh:mm:ss) of the start of the simulation in string format
        strategy : str
            A two character string that sets the strategy as one of the following: [s1, s2, s3].

        Returns
        -------
        self._entities : list
            Return a list of dictionaries describing the created model instances (entities). 
            The root list must contain exactly `num` elements. The number of objects in sub-lists is not constrained::

            [
                {
                    'eid': 'eid_1',
                    'type': 'model_name',
                    'rel': ['eid_2', ...],
                    'children': [
                        {'eid': 'child_1', 'type': 'child'},
                        ...
                    ],
                },
                ...
            ]
        
        See Also
        --------
        The entity ID (*eid*) of an object must be unique within a simulator instance. For entities in the root list, `type` must be the same as the
        `model` parameter. The type for objects in sub-lists may be anything that can be found in ``meta['models']``. *rel* is an optional list of
        related entities; "related" means that two entities are somehow connect within the simulator, either logically or via a real data-flow (e.g.,
        grid nodes are related to their adjacent branches). The *children* entry is optional and may contain a sub-list of entities.
        """
        self.start = pd.to_datetime(sim_start)
        self._entities = []

        for i in range(num):
            eid = '%s%s_%d' % (self.eid_prefix, strategy, i)
            if strategy == 's1':
                model_instance = prosumer_S1(eid, **model_params)
            elif strategy == 's2':
                model_instance = prosumer_S2(eid, **model_params)
            elif strategy == 's3':
                model_instance = prosumer_S3(eid, **model_params)
            else:
                raise ValueError(f"Invalid model: {model}")

            self.entities[eid] = model_instance
            self._entities.append({'eid': eid, 'type': model})

        return self._entities

    def step(self, time:int, inputs:dict, max_advance:int) -> int:
        """
        Perform the next simulation step from time `time` using input values from `inputs`

        ...

        Parameters
        ----------
        time : int
            A representation of time with the unit being arbitrary. Has to be consistent among 
            all simulators used in a simulation.

        inputs : dict
            Dict of dicts mapping entity IDs to attributes and dicts of values (each simulator has to decide on its own how to reduce 
            the values (e.g., as its sum, average or maximum)::

            {
                'dest_eid': {
                    'attr': {'src_fullid': val, ...},
                    ...
                },
                ...
            }

        max_advance : int 
            Tells the simulator how far it can advance its time without risking any causality error, i.e. it is guaranteed that no
            external step will be triggered before max_advance + 1, unless the simulator activates an output loop earlier than that. For time-based
            simulators (or hybrid ones without any triggering input) *max_advance* is always equal to the end of the simulation (*until*).
        
        Returns
        -------
        new_step : int
            Return the new simulation time, i.e. the time at which ``step()`` should be called again.
        """
        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution,
                                     unit='seconds'))  # timedelta represents a duration of time
        self.time = time
        print('from prosumer %%%%%%%%%', current_time)
        _cache = {}

        for eid, attrs in inputs.items():               # configuration possible inputs
            generators = pd.DataFrame()
            demands = pd.DataFrame()
            storages = pd.DataFrame()
            generators_data = []
            demand_data = []
            storage_data = []
            em_accepted_bids = []
            p2p_transactions = []

            # Loop through the dictionary and extract generator, load and storage data
            for key, value in inputs[eid].items():
                for k, v in value.items():
                    if 'generator' in key:
                        generator_item = {'input': key.split('[')[1].split(']')[0],
                                          'from': k.split('.')[1],
                                          'name': key,
                                          'p_gen': v}
                        generators_data.append(generator_item)

                    elif 'demand' in key:
                        demand_item = {'input': key.split('[')[1].split(']')[0],
                                       'from': k.split('.')[1],
                                       'name': key,
                                        'p_dem': v}
                        demand_data.append(demand_item)

                    elif 'storage' in key:
                        storage_item = {'input': key.split('[')[1].split(']')[0],
                                        'from': k.split('.')[1],
                                        'name': key,
                                        'soc': v}
                        storage_data.append(storage_item)

                    elif 'em_accepted_bids' in key:
                        if v and v != 0 and v is not None:
                            try:
                                em_accepted_bids = v[eid]
                            except KeyError:
                                continue
                    elif 'p2p_transactions' in key:
                        if v and v != 0 and v is not None:
                            try:
                                p2p_transactions = v[eid]
                            except KeyError:
                                continue

            if generators_data:
                generators = pd.DataFrame(generators_data).set_index('input').sort_index()
            if demand_data:
                demands = pd.DataFrame(demand_data).set_index('input').sort_index()
            if storage_data:
                storages = pd.DataFrame(storage_data).set_index('input').sort_index()

            _cache[eid] = self.entities[eid].prosumer(
                self.start, current_time, generators, demands, storages, em_accepted_bids, p2p_transactions)

        self._cache = _cache
        return self.time + self.step_size

    def get_data(self, outputs:dict) -> dict:            # to be implemented
        """
        Return the data for the requested attributes in `outputs`
        
        ...

        Parameters
        ----------
        outputs : dict 
            Maps entity IDs to lists of attribute names whose values are requested::

            {
                'eid_1': ['attr_1', 'attr_2', ...],
                ...
            }

        Returns
        -------
        data : dict
            The return value is a dict of dicts mapping entity IDs and attribute names to their values::

            {
                'eid_1: {
                    'attr_1': 'val_1',
                    'attr_2': 'val_2',
                    ...
                },
                ...
                'time': output_time (for event-based sims, optional)
            }

        See Alsoe
        --------
        Time-based simulators have set an entry for all requested attributes, whereas for event-based and hybrid simulators this is optional (e.g.
        if there's no new event). Event-based and hybrid simulators can optionally set a timing of their non-persistent output attributes via a *time* entry, which is valid
        for all given (non-persistent) attributes. If not given, it defaults to the current time of the step. Thus only one output time is possible
        per step. For further output times the simulator has to schedule another self-step (via the step's return value).
        """
        data = {}
        for eid, attrs in outputs.items():
            # model = self.entities[eid]
            # data['time'] = self.time
            data[eid] = {}
            for attr in attrs:
                if attr in self.incr_attr:
                    # Extract index from attribute string
                    index = int(attr.split('[')[1].split(']')[0])
                    data[eid][attr] = self._cache[eid][attr.split('[')[0]][index]
                elif attr == 'em_supply_bids':
                    try:
                        data[eid][attr] = self._cache[eid]['em_supply_bids']
                    except KeyError:
                        data[eid][attr] = None
                elif attr == 'em_demand_bids':
                    try:
                        data[eid][attr] = self._cache[eid]['em_demand_bids']
                    except KeyError:
                        data[eid][attr] = None
                elif attr == 'p2p_supply_offers':
                    try:
                        data[eid][attr] = self._cache[eid]['p2p_supply_offers']
                    except KeyError:
                        data[eid][attr] = None
                elif attr == 'p2p_demand_requests':
                    try:
                        data[eid][attr] = self._cache[eid]['p2p_demand_requests']
                    except KeyError:
                        data[eid][attr] = None
                elif attr == 'rt_buy':
                    try:
                        data[eid][attr] = self._cache[eid]['rt_buy']
                    except KeyError:
                        data[eid][attr] = 0
                elif attr == 'rt_sell':
                    try:
                        data[eid][attr] = self._cache[eid]['rt_sell']
                    except KeyError:
                        data[eid][attr] = 0
                elif attr == 'p2em':
                    try:
                        data[eid][attr] = self._cache[eid]['p2em']
                    except KeyError:
                        data[eid][attr] = 0
                elif attr == 'p2p2p':
                    try:
                        data[eid][attr] = self._cache[eid]['p2p2p']
                    except KeyError:
                        data[eid][attr] = 0
        return data
def main():
    mosaik_api.start_simulation(prosumerSim(), 'Prosumer-Illuminator')
if __name__ == '__main__':
    main()
