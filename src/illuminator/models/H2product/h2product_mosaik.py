import mosaik_api
#import Load.h2product_model as h2product_model
try:
    import Models.H2product.h2product_model as h2product_model
except ModuleNotFoundError:
    import h2product_model as h2product_model
else:
    import Models.H2product.h2product_model as h2product_model

import pandas as pd

META = {
    'type': 'event-based',

    'models': {
        'h2productmodel': {
            'public': True,
            'params': ['sim_start', 'houses'],
            'attrs': ['h2product_id','h2product_gen','h2product'],
            'trigger': [],
        },
    },
}


class h2productSim(mosaik_api.Simulator):
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
        self.time : int
            A representation of time with the unit being arbitrary. Has to be consistent among 
            all simulators used in a simulation.
        """
        super().__init__(META)
        self.eid_prefix = 'h2product_'  # every entity that we create will start with 'wind_'
        self.entities = {}  # we store the model entity of our technology model
        self._cache = {}  # used in the step function to store the values after running the python model of the technology
        self.time = 0
        # self.start_date = None

    # the following API call is will be called only once when we initiate the model in the scenario file.
    # we can use this to pass additional initialization tasks

    def init(self, sid:str, time_resolution:float):
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
        # print('hi, you have entered init')  # working (20220524)
        self.time_resolution = time_resolution
        # print('Exited init os SimAPI')  # working (20220524)
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
        entities : list
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
        # print('hi, you have entered create of SimAPI')  # working (20220524)
        self.start = pd.to_datetime(sim_start)
        # print(type(self.entities))
        # next_eid = len(self.entities)
        # print('from create of SimAPI:', next_eid)
        entities = []
        # print(next_eid)  # working (20220524)

        for i in range(num):
            eid = '%s%d' % (self.eid_prefix, i)
            model_instance = h2product_model.h2product_python(**model_params)
            self.entities[eid] = model_instance
            entities.append({'eid': eid, 'type': model})
        return entities

    def step(self, time:int, inputs:dict, max_advance:int) -> int:
        """
        Perform the next simulation step from time `time` using input values from `inputs`

        ...

        Parameters
        ----------
        time : int
            A representation of time with the unit being arbitrary. Has to be consistent among 
            all simulators used in a simulation. For this specific model it is in seconds rather than minutes.

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
        int
            The new time + a step of 900 seconds. 
            It should be noted other models use time as a representation of minutes rather than seconds.
        """
        self.time = time
        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution,
                                     unit='seconds'))  # timedelta represents a duration of time
        print('from h2product %%%%%%%%%%%', current_time)

        for eid, attrs in inputs.items():

            for attr, vals in attrs.items():
                self._cache[eid] = self.entities[eid].generation(list(vals.values())[0])
        return time + 900

    def get_data(self, outputs:dict) -> dict:
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
                if attr == 'h2product_gen':
                    data[eid][attr] = self._cache[eid]['h2product_gen']
                    data['time'] = self.time
        return data
def main():
    mosaik_api.start_simulation(h2productSim(), 'h2product Simulator')
    
if __name__ == "__main__":
    main()
