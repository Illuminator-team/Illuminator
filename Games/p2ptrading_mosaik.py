import mosaik_api
import pandas as pd
try:
    import Games.p2ptrading_model as p2ptrading_model
except ModuleNotFoundError:
    import p2ptrading_model as p2ptrading_model
else:
    import Games.p2ptrading_model as p2ptrading_model
import sys
sys.path.insert(1,'/home/illuminator/Desktop/Final_illuminator')


META = {
    'type': 'hybrid',
    'models': {
        'P2Ptrading': {
            'public': True,
            'params': ['sim_start'],
            'attrs': ['p2ptrading_id',  'transactions',  'quantity_traded'],
            'trigger': [],
        },
    },
}
incremental_attributes = ['supply_offers', 'demand_requests']

class p2ptradingSim(mosaik_api.Simulator):
    def __init__(self) -> None:
        """
        Inherits the Mosaik API Simulator class and is used for python based simulations.
        For more information properly inheriting the Mosaik API Simulator class please read their given documentation.

        ...

        Attributes
        ----------
        self.meta : dict
            Contains metadata of the control sim such as type, models, parameters, attributes, etc.. Created via p2ptradingSim's parent class.
        self.eid_prefix : string
            The prefix with which each entity's name/eid will start
        self.entities : dict
            The stored model entity of the technology model
        self._cache : dict
            Used in the step function to store the values after running the python model of the technology
        """
        super().__init__(META)
        self.eid_prefix = 'p2ptrading_'
        self.entities = {}
        self._cache = {}  #

    def init(self, sid:str, time_resolution:float, step_size:int=900) -> dict:
        """
        Initialize the simulator with the ID `sid` and pass the `time_resolution` and additional parameters sent by mosaik.
        Because this method has an additional parameter `step_size` it is overriding the parent method init().

        ...

        Parameters
        ----------
        sid : string
            The String ID of the class (???)
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
        for attr in META['models']['P2Ptrading']['attrs']:
            for inc_attr in incremental_attributes:
                if attr.startswith(inc_attr):
                    self.incr_attr.append(attr)
        return self.meta

    def create(self, num:int, model:str, sim_start:str, **model_params) -> list:
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
        **model_params : dict 
            A mapping of parameters (from``meta['models'][model]['params']``) to their values.
        
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
            eid = '%s%d' % (self.eid_prefix, i)
            model_instance = p2ptrading_model.p2ptrading_python(**model_params)  #1
            self.entities[eid] = model_instance  #2
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
        print('from peer-to-peer trading %%%%%%%%%', current_time)
        _cache = {}

        for eid, attrs in inputs.items():               # configuration possible inputs

            # Translator
            players_data = {}

            for key, value in inputs[eid].items():
                for k, v in value.items():
                    input_key = key.split('[')[1].split(']')[0]
                    type_key = k.split('.')[0]
                    name_key = k.split('.')[1]

                    if input_key not in players_data:
                        players_data[input_key] = {'input': input_key, 'type': type_key, 'name': name_key,
                                                   'demand_requests': None, 'supply_offers': None}
                    if 'supply_offers' in key:
                        players_data[input_key]['supply_offers'] = v
                    if 'demand_requests' in key:
                        players_data[input_key]['demand_requests'] = v

            # Check if there are any non-empty and non-zero 'supply_offers' or 'demand_requests'
            non_empty_players = [player for player in players_data.values() if
                                 (player['supply_offers'] is not None and player['supply_offers'] != 0) or (
                                             player['demand_requests'] is not None and player['demand_requests'] != 0)]

            if non_empty_players:
                players = pd.DataFrame(non_empty_players).set_index('input').sort_index()
            else:
                players = pd.DataFrame()

            _cache[eid] = self.entities[eid].p2ptrading(current_time, players)

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

        See Also
        --------
        Time-based simulators have set an entry for all requested attributes, whereas for event-based and hybrid simulators this is optional (e.g.
        if there's no new event). Event-based and hybrid simulators can optionally set a timing of their non-persistent output attributes via a *time* entry, which is valid
        for all given (non-persistent) attributes. If not given, it defaults to the current time of the step. Thus only one output time is possible
        per step. For further output times the simulator has to schedule another self-step (via the step's return value).
        """
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            for attr in attrs:
                if attr in self.incr_attr:
                    # Extract index from attribute string
                    index = int(attr.split('[')[1].split(']')[0])
                    data[eid][attr] = self._cache[eid][attr.split('[')[0]][index]
                elif attr == 'quantity_traded':
                    try:
                        data[eid][attr] = self._cache[eid]['quantity_traded']
                    except TypeError or KeyError:
                        data[eid][attr] = None
                elif attr == 'transactions':
                    try:
                        data[eid][attr] = self._cache[eid]['transactions']
                    except TypeError or KeyError:
                        data[eid][attr] = None
        return data
def main():
    mosaik_api.start_simulation(p2ptradingSim(), 'P2Ptrading-Illuminator')
if __name__ == '__main__':
    main()
