import mosaik_api
import pandas as pd

try:
    import Controllers.NetVoltageControllerSim.controller as controller_model
except ModuleNotFoundError:
    import controller as controller_model
else:
    import Controllers.NetVoltageControllerSim.controller as controller_model
#import Battery.model as batterymodel
import sys

import itertools
META = {
    'type': 'event-based',

    'models': {
        'Ctrl': {
            'public': True,
            'params': ['net', 'room'],
            'attrs': ['controller_id', 'vm_pu', 'p_mw','q_mvar'],
            'trigger': [],
        },
    },
}

# Same issue as the netvoltagecontrollersim/controller.py
class controlSim(mosaik_api.Simulator):
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
        self.temp : int
            ???
        """
        super().__init__(META)
        self.eid_prefix = 'ctrl_'  # every entity that we create will start with 'wind_'
        self.entities = {}  # we store the model entity of our technology model
        self._cache = {}  # used in the step function to store the values after running the python model of the technology
        self.temp = 0
        # self.start_date = None

    # the following API call is will be called only once when we initiate the model in the scenario file.
    # we can use this to pass additional initialization tasks

    def init(self, sid:str, time_resolution:float, step_size:int=1) -> dict:
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
        # print('hi, you have entered init')  # working (20220524)
        self.time_resolution = time_resolution
        # print('Exited init os SimAPI')  # working (20220524)
        self.attr_names = []
        # print(next_eid)  # working (20220524)
        self.attr_names = [f'p_m_update{i}' for i in range(19)]
        self.attr_names.extend([f'q_war_update{i}' for i in range(19)])
        self.meta['models']['Ctrl']['attrs'].extend(self.attr_names)

        return self.meta

    def create(self, num:int, model:str, **model_params) -> list:
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
        # print('hi, you have entered create of SimAPI')  # working (20220524)
        # print(type(self.entities))
        # next_eid = len(self.entities)
        # print('from create of SimAPI:', next_eid)
        self._entities = []

        for i in range(num):
            eid = '%s%d' % (self.eid_prefix, i)
            model_instance = controller_model.controller_python(**model_params)  #1
            self.entities[eid] = model_instance  #2
            # print(self.entities)
            # self.soc_max[eid] = soc_max
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
        # inputs is a dictionary, which contains another dictionary.
        # print(inputs)

        _cache = {}
        u = []
        for eid, attrs in inputs.items():
            # print('#eid: ', eid)
            print('#attrs: ', attrs)

            for attr, vals in attrs.items():

                if attr == 'p_mw':
                    p_mw = vals.values()
                elif attr == 'vm_pu':
                    vm_pu = vals.values()
                elif attr =='q_mvar':
                    q_mvar = vals.values()

            _cache[eid] = self.entities[eid].control(p_mw,q_mvar,vm_pu,self.attr_names)
            self._cache = _cache
        print(p_mw,vm_pu)
        return None

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
        print('1')
        for eid, attrs in outputs.items():
            # model = self.entities[eid]
            # data['time'] = self.time
            data[eid] = {}
            for attr in attrs:
                # if we want more values to print in the output file, mimic the below for new attributes and make sure
                # those parameters are present in the re_params in the python file of the technology
                if attr in ['controller_id', 'vm_pu', 'p_mw','q_mvar']:
                    pass
                else:
                    data[eid][attr] = self._cache[eid][attr]

        return data
def main():
    mosaik_api.start_simulation(controlSim(), 'Controller-Illuminator')
if __name__ == '__main__':
    main()