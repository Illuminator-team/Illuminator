import mosaik_api
import pandas as pd
try:
    import Models.Valves.h2valve_model as h2valve_model
except ModuleNotFoundError:
    import h2valve_model as h2valve_model
else:
    import Models.Valves.h2valve_model as h2valve_model
import sys
sys.path.insert(1,'/home/illuminator/Desktop/Final_illuminator')

META = {
    'type': 'event-based',
    'models': {
        'H2Valve': {
            'public': True,
            'params': ['sim_start'],
            'attrs': ['valve_id', 'h2_elec', 'h2_stor','h2_fc',
                      'h2_elec_net', 'h2_stor_net', 'h2_fc_net',
                      'h2_elec_stor', 'h2_stor_fc'],
            'trigger': [],
        },
    },
}
incremental_attributes = []

class h2valveSim(mosaik_api.Simulator):
    def __init__(self) -> None:
        """
        Inherits the Mosaik API Simulator class and is used for python based simulations.
        For more information properly inheriting the Mosaik API Simulator class please read their given documentation.

        ...

        Attributes
        ----------
        self.meta : dict
            Contains metadata of the control sim such as type, models, parameters, attributes, etc.. Created via gpcontrolSim's parent class.
        self.eid_prefix : string
            The prefix with which each entity's name/eid will start
        self.entities : dict
            The stored model entity of the technology model
        self._cache : dict
            Used in the step function to store the values after running the python model of the technology
        """
        super().__init__(META)
        self.eid_prefix = 'H2valve_'
        self.entities = {}
        self._cache = {}


    def init(self, sid:str, time_resolution:float, step_size:int=1) -> dict:
        """
        Initialize the simulator with the ID `sid` and pass the `time_resolution` and additional parameters sent by mosaik.
        Because this method has an additional parameter `step_size` it is overriding the parent method init().

        ...

        Parameters
        ----------
        sid : str
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
        # self.incr_attr = []
        # for attr in META['models']['ElectricityNetwork']['attrs']:
        #     for inc_attr in incremental_attributes:
        #         if attr.startswith(inc_attr):
        #             self.incr_attr.append(attr)
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
            model_instance = h2valve_model.h2valve_python(**model_params)  #1
            self.entities[eid] = model_instance  #2
            self._entities.append({'eid': eid, 'type': model})
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
        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution,
                                     unit='seconds'))  # timedelta represents a duration of time
        self.time = time
        print('from h2 valve %%%%%%%%%', current_time)

        for eid, attrs in inputs.items():
            h2_elec = 0
            h2_stor = 0
            h2_fc = 0
            for attr, vals in attrs.items():
                if attr == 'h2_elec':
                    h2_elec = sum(vals.values())
                if attr == 'h2_stor':
                    h2_stor = sum(vals.values())
                if attr == 'h2_fc':
                    h2_fc = sum(vals.values())

            self._cache[eid] = self.entities[eid].route(h2_elec, h2_stor, h2_fc)

        return None

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
                # if attr in self.incr_attr:
                #     # Extract index from attribute string
                #     index = int(attr.split('[')[1].split(']')[0])
                #     data[eid][attr] = self._cache[eid][attr.split('[')[0]][index]
                if attr == 'h2_elec':
                    data[eid][attr] = self._cache[eid]['h2_elec']
                elif attr == 'h2_stor':
                    data[eid][attr] = self._cache[eid]['h2_stor']
                elif attr == 'h2_fc':
                    data[eid][attr] = self._cache[eid]['h2_fc']
                elif attr == 'h2_elec_net':
                    data[eid][attr] = self._cache[eid]['h2_elec_net']
                elif attr == 'h2_stor_net':
                    data[eid][attr] = self._cache[eid]['h2_stor_net']
                elif attr == 'h2_fc_net':
                    data[eid][attr] = self._cache[eid]['h2_fc_net']
                elif attr == 'h2_elec_stor':
                    data[eid][attr] = self._cache[eid]['h2_elec_stor']
                elif attr == 'h2_stor_fc':
                    data[eid][attr] = self._cache[eid]['h2_stor_fc']
        return data
def main():
    mosaik_api.start_simulation(h2valveSim(), 'H2Valve-Illuminator')
if __name__ == '__main__':
    main()
