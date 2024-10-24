import mosaik_api
import multiprocessing as mp
import json
import os
try:
    import Models.Heatpump.heatpump.Heat_Pump_Model as HeatPump
except ModuleNotFoundError:
    import Heat_Pump_Model as HeatPump
else:
    import Models.Heatpump.heatpump.Heat_Pump_Model as HeatPump

META = {
    'type': 'time-based',
    'models': {
        'HeatPump': {
            'public': True,
            'params': ['params'],
            'attrs': ['Q_Demand', 'Q_Supplied', 'heat_source_T', 'heat_source', 'cons_T', 'P_Required', 'COP',
                      'cond_m', 'cond_in_T', 'T_amb', 'on_fraction', 'cond_m_neg', 'Q_evap', 'step_executed'],
        },
    },
}

JSON_COP_DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), 'cop_m_data.json'))

class HeatPumpSimulator(mosaik_api.Simulator):
    def __init__(self) -> None:
        """
        Inherits the Mosaik API Simulator class and is used for python based simulations.
        For more information properly inheriting the Mosaik API Simulator class please read their given documentation.

        ...

        Attributes
        ----------
        self.meta : dict
            Contains metadata of the control sim such as type, models, parameters, attributes, etc.. Created via gpcontrolSim's parent class.
        self.time_resolution : float
            ???
        self.sid : str
            The String ID of the class (???)
        self.eid_prefix : string
            The prefix with which each entity's name/eid will start
        self.step_size : ???
            The size of the time step. The unit is arbitrary, but it has to be consistent among all simulators used in a simulation.
        self.time : int
            A representation of time with the unit being arbitrary. Has to be consistent among 
            all simulators used in a simulation.
        """
        super().__init__(META)
        self.time_resolution = None
        self.models = dict()  # contains the model instances
        self.sid = None
        self.eid_prefix = 'HeatPump_'
        self.step_size = None
        self.time = 0

        self.parallelization = False
        self.processes = 1
        # start time of simulation as UTC ISO 8601 time string

    def init(self, sid:str, time_resolution:float, step_size:int, same_time_loop:bool=False) -> dict:
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
        same_time_loop : bool
            ???
            
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
        if same_time_loop:
            self.meta['type'] = 'event-based'

        return self.meta

    def create(self, num:int, model:str, params:dict) -> list:
        """
        Create `num` instances of `model` using the provided `model_params`.

        ...

        Parameters
        ----------
        num : int
            The number of model instances to create.
        model : str
            `model` needs to be a public entry in the simulator's ``meta['models']``.
        params : dict 
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

        if 'processes' in params:
            self.parallelization = True
            self.processes = params['processes']
            if num < self.processes:
                self.processes = num

        COP_m_data = None
        if params['calc_mode'] == 'fast' or params['calc_mode'] == 'fixed_hl':
            with open(JSON_COP_DATA, "r") as read_file_1:
                COP_m_data_all = json.load(read_file_1)
                COP_m_data = COP_m_data_all[params['hp_model']]

        next_eid = len(self.models)
        for i in range(next_eid, next_eid + num):
            eid = '%s%d' % (self.eid_prefix, i)
            self.models[eid] = HeatPump.Heat_Pump(params, COP_m_data)
            entities.append({'eid': eid, 'type': model})
        return entities

    def step(self, time:int, inputs:dict, max_advance:int) -> int | None:
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
        
        or

        None
        """
        # print('heatpump inputs: %s' % inputs)
        # print(f"Stepping HP at {time}")
        for eid, attrs in inputs.items():
            if self.meta['type'] == 'event-based':
                if time != self.time:
                    self.time = time
                    setattr(self.models[eid].state, 'step_executed', False)
            for attr, src_ids in attrs.items():
                if len(src_ids) > 1:
                    raise ValueError('Two many inputs for attribute %s' % attr)
                for val in src_ids.values():
                    setattr(self.models[eid].inputs, attr, val)

            self.models[eid].inputs.step_size = self.step_size

        if self.parallelization:
            pool = mp.Pool(processes=self.processes)
            for eid, model in self.models.items():
                pool.apply_async(model.step(), args=())
            pool.close()
            pool.join()
        else:
            for eid, model in self.models.items():
                model.step()

        if self.meta['type'] == 'event-based':
            return None
        else:
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
            if self.models[eid].state.step_executed:
                data[eid] = {}
                for attr in attrs:
                    if attr not in self.meta['models']['HeatPump'][
                            'attrs']:
                        raise ValueError('Unknown output attribute: %s' % attr)
                    data['time'] = self.time
                    if attr != 'step_executed':
                        data[eid][attr] = float(getattr(self.models[eid].state, attr))
                    else:
                        data[eid][attr] = getattr(self.models[eid].state, attr)
        return data

def main():
    return mosaik_api.start_simulation(HeatPumpSimulator())

if __name__ == '__main__':
    main()