import mosaik_api
#import H2storage.h2storage_model as h2trailer
try:
    import Models.H2storage.h2storage_model as hydrogen_storage
except ModuleNotFoundError:
    import h2storage_model as hydrogen_storage
else:
    import Models.H2storage.h2storage_model as hydrogen_storage
import pandas as pd
import itertools
META = {
    'type': 'event-based',
    'models': {
        'compressed_hydrogen': {
            'public': True,
            'params': ['sim_start', 'initial_set', 'h2_set'],
            'attrs': ['h2storage_id',
                      'flow2h2s',
                      'eleh2_in',
                      'fuelh2_out',
                      'h2_flow',
                      'h2_excess_flow',
                      'h2_soc',
                      'mod',
                      'flag',
                      'h2_flow'],
            'trigger': [],
        },
    },
}

class compressedhydrogen(mosaik_api.Simulator):
    def __init__(self) -> None:
        """
        Inherits the Mosaik API Simulator class and is used for python based simulations.
        For more information properly inheriting the Mosaik API Simulator class please read their given documentation.

        ...

        Attributes
        ----------
        self.meta : dict
            Contains metadata of the control sim such as type, models, parameters, attributes, etc.. Created via controlSim's parent class.
        self.eid_prefix : string
            The prefix with which each entity's name/eid will start
        self.entities : dict
            The stored model entity of the technology model
        self._cache : dict
            Used in the step function to store the values after running the python model of the technology
        self.soc : dict
            State of charge for a specific battery
        self.flag : dict
            ???
        self.h2_stored : dict
            ???
        """
        super().__init__(META)
        self.eid_prefix = 'h2storage_'
        self.entities = {}
        self._cache = {}
        self.soc = {}
        self.flag = {}
        self.h2_stored = {}

    def init(self, sid:str, time_resolution:float) -> dict:
        """
        Initialize the simulator with the ID `sid` and pass the `time_resolution` and additional parameters sent by mosaik.

        ...

        Parameters
        ----------
        sid : string
            The String ID of the class (???)
        time_resolution : float
            ???

        Returns
        -------
        self.meta : dict
            The metadata of the class
        """
        self.time_resolution = time_resolution
        return self.meta

    def create(self, num:int, model:str, initial_set:dict, h2_set:dict, sim_start:str) -> list:
        """
        Create `num` instances of `model` using the provided `model_params`.

        ...

        Parameters
        ----------
        num : int
            The number of model instances to create.
        model : str
            `model` needs to be a public entry in the simulator's ``meta['models']``.
        initial_set : dict
            ???
        h2_set : dict
            ???
        sim_start : str
            Date and time (YYYY-MM-DD hh:mm:ss) of the start of the simulation in string format
        
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

        # num is the number of models of battery we want.
        for i in range(num):
            self.eid = '%s%d' % (self.eid_prefix, i)
            h2storage_instance = hydrogen_storage.hydrogenstorage_python(initial_set, h2_set)

            self.entities[self.eid] = h2storage_instance
            self.soc[self.eid] = initial_set['initial_soc']
            self.flag[self.eid] = h2_set['flag']
            self._entities.append({'eid': self.eid, 'type': model, 'rel': [], })
        return self._entities

    def step(self, time:int, inputs:dict, max_advance:int) -> None:
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
        """
        self.time = time
        current_time = (self.start + pd.Timedelta(time * self.time_resolution, unit='seconds'))
        print('from h2 storage %%%%%%%%', current_time)
        eleh2_in=0
        flow2h2s=0
        fuelh2_out=0

        for eid, attrs in inputs.items():
            for attr, vals in attrs.items():
                #flow2h2s, eleh2_in, fuelh2_out
                if attr=='eleh2_in':
                    eleh2_in=eleh2_in+list(vals.values())[0]
                elif attr=='fuelh2_out':
                    fuelh2_out=fuelh2_out+list(vals.values())[0]
                elif attr=='flow2h2s':
                    flow2h2s = flow2h2s + list(vals.values())[0]

            self._cache[eid] = self.entities[eid].output_h2(flow2h2s,eleh2_in,fuelh2_out, self.soc[eid])

            self.soc[eid] = self._cache[eid]['h2_soc']
            self.flag = self._cache[eid]['flag']

        return None

    def get_data(self, outputs):
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
            model = self.entities[eid]
            data[eid] = {}
            for attr in attrs:
                if attr == 'h2_soc':
                    data[eid][attr] = self._cache[eid]['h2_soc']
                elif attr == 'mod':
                    data[eid][attr] = self._cache[eid]['mod']
                elif attr == 'h2storage_id':
                    data[eid][attr] = eid
                elif attr == 'flag':
                    data[eid][attr] = self._cache[eid]['flag']

                elif attr == 'eleh2_in':
                    data[eid][attr] = self._cache[eid]['eleh2_in']
                elif attr == 'fuelh2_out':
                    data[eid][attr] = self._cache[eid]['fuelh2_out']
                elif attr == 'h2_flow':
                    data[eid][attr] = self._cache[eid]['h2_flow']
                elif attr == 'h2_excess_flow':
                    data[eid][attr] = self._cache[eid]['h2_excess_flow']

        return data


def main():
    mosaik_api.start_simulation(compressedhydrogen(), 'H2storage-Simulator')
    
if __name__ == "__main__":
    main()