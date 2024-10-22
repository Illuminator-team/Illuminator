import mosaik_api
from mosaik_heatpump.controller.controller import Controller

META = {
    'type': 'time-based',
    'models': {
        'Controller': {
            'public': True,
            'params': ['params'],
            'attrs': ['_', 'T_amb', 'heat_source_T', 'hp_demand', 'heat_supply', 'heat_demand', 'sh_demand', 'sh_supply',
                      'dhw_demand', 'dhw_supply', 'sh_in_F', 'sh_in_T', 'sh_out_F', 'dhw_in_F', 'dhw_in_T', 'dhw_out_F',
                      'hp_in_F', 'hp_in_T', 'hp_out_F', 'hp_out_T', 'hp_supply', 'hwt_connections', 'T_mean', 'hwt_mass',
                      'hwt_hr_P_th_set', 'hp_on_fraction', 'hp_cond_m'],
            # 'attrs': ['outside_temperature', 'sh_demand', 'sh_supply', 'dhw_demand', 'dhw_supply', 'hp_demand'],
        },
    },
    'extra_methods': [
        'add_async_request'
        ]
}


class ControllerSimulator(mosaik_api.Simulator):
    def __init__(self) -> None:
        """
        Inherits the Mosaik API Simulator class and is used for python based simulations.
        For more information properly inheriting the Mosaik API Simulator class please read their given documentation.

        ...

        Attributes
        ----------
        self.meta : dict
            Contains metadata of the control sim such as type, models, parameters, attributes, etc.. Created via gpcontrolSim's parent class.
        self.sid : string
            the String ID of the class (???)
        self.eid_prefix : string
            The prefix with which each entity's name/eid will start
        self.step_size : int
            ???
        self.async_requests : dict
            ???
        """
        super().__init__(META)

        self.models = dict()  # contains the model instances
        self.sid = None
        self.eid_prefix = 'Controller_'
        self.step_size = None
        self.async_requests = dict()

    def init(self, sid:str, time_resolution:float, step_size:int) -> dict:
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
        self.time_resolution = float(time_resolution)
        if self.time_resolution != 1.0:
            print('WARNING: %s got a time_resolution other than 1.0, which \
                can not be handled by this simulator.', sid)
        self.sid = sid # simulator id
        self.step_size = step_size
        return self.meta

    def create(self, num:int, model:str, params=None) -> list:
        """
        Create `num` instances of `model` using the provided `model_params`.

        ...

        Parameters
        ----------
        num : int
            The number of model instances to create.
        model : str
            `model` needs to be a public entry in the simulator's ``meta['models']``.
        params : dict(?)
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
        entities = []

        next_eid = len(self.models)
        for i in range(next_eid, next_eid + num):
            eid = '%s%d' % (self.eid_prefix, i)
            if params is not None:
                self.models[eid] = Controller(params)
            else:
                self.models[eid] = Controller()
            entities.append({'eid': eid, 'type': model})
        return entities

    def add_async_request(self, src_id, dest_id, *attr_pairs):
        if not src_id in self.async_requests:
            self.async_requests[src_id] = {dest_id: {}}
        if not dest_id in self.async_requests[src_id]:
            self.async_requests[src_id][dest_id] = {}
        for attr_pair in attr_pairs:
            src_attr, dest_attr = attr_pair
            self.async_requests[src_id][dest_id].update({src_attr: dest_attr})

    def step(self, time:int, inputs:dict, max_advance:int):
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
        
        Yields
        ------
        ???
            ???

        Returns
        -------
        new_step : int
            Return the new simulation time, i.e. the time at which ``step()`` should be called again.
        """
        # print('controller inputs: %s' % inputs)
        for eid, attrs in inputs.items():
            # print(eid, attrs)
            for attr, src_ids in attrs.items():
                if len(src_ids) > 1:
                    raise ValueError('Two many inputs for attribute %s' % attr)
                for val in src_ids.values():
                    setattr(self.models[eid], attr, val)

            self.models[eid].step_size = self.step_size
            self.models[eid].step()

        inputs = {}
        # print('async_reqs: %s' % self.async_requests)
        for src_id, dest_ids in self.async_requests.items():
            eid = src_id.split('.')[1]
            inputs[src_id] = {}
            for dest_id, src_attrs in dest_ids.items():
                inputs[src_id][dest_id] = {}
                for src_attr, dest_attr in src_attrs.items():
                    inputs[src_id][dest_id][dest_attr] = getattr(self.models[eid], src_attr)

        # print('controller inputs: %s' % inputs)
        yield self.mosaik.set_data(inputs)

        return time + self.step_size

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
                if attr not in self.meta['models']['Controller'][
                        'attrs']:
                    raise ValueError('Unknown output attribute: %s' % attr)
                data[eid][attr] = getattr(self.models[eid], attr)
        return data

def main():
    return mosaik_api.start_simulation(ControllerSimulator())

if __name__ == '__main__':
    main()
