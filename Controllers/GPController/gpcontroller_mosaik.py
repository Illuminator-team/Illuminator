import mosaik_api
import pandas as pd
try:
    import Controllers.GPController.gpcontroller_model as gpcontroller_model
except ModuleNotFoundError:
    import gpcontroller_model as gpcontroller_model
else:
    import Controllers.GPController.gpcontroller_model as gpcontroller_model
import sys
sys.path.insert(1,'/home/illuminator/Desktop/Final_illuminator')

# try:
#     import Models.Battery.battery_model as batterymodel
# except ModuleNotFoundError:
#     import battery_model as batterymodel
# else:
import Models.Battery.battery_model as batterymodel

META = {
    'type': 'hybrid',
    'models': {
        'GPCtrl': {
            'public': True,
            'params': ['sim_start', 'soc_min', 'soc_max', 'h2_soc_min', 'h2_soc_max', 'fc_eff'],
            'attrs': ['controller_id', 'net', 'deficit', 'excess', 'curtail'],
            'trigger': [],
        },
    },
}
incremental_attributes = ['flow2b', 'generator', 'demand', 'storage']

class gpcontrolSim(mosaik_api.Simulator):
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
        self.eid_prefix = 'gpctrl_'
        self.entities = {}
        self._cache = {}  # used in the step function to store the values after running the python model of the technology
        #self.soc_max = {}
        #self.temp = 0
        #self.h2fc = {}
        # self.start_date = None
        
        

    # the following API call is will be called only once when we initiate the model in the scenario file.
    # we can use this to pass additional initialization tasks

    def init(self, sid:str, time_resolution:float, step_size:int=900) -> dict:
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
        self.incr_attr = []
        for attr in META['models']['GPCtrl']['attrs']:
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
        # print(type(self.entities))
        # next_eid = len(self.entities)
        self._entities = []

        for i in range(num):
            eid = '%s%d' % (self.eid_prefix, i)
            model_instance = gpcontroller_model.gpcontroller_python(**model_params)  #1
            self.entities[eid] = model_instance  #2
            # print(self.entities)
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
        print('from controller %%%%%%%%%', current_time)
        _cache = {}

        for eid, attrs in inputs.items():               # configuration possible inputs
            generators_data = []
            demand_data = []
            storage_data = []
            curtail = 0

            # Loop through the dictionary and extract generator, load and storage data
            for key, value in inputs[eid].items():
                for k, v in value.items():
                    if 'generator' in key:
                        generators_data.append({'input': key.split('[')[1].split(']')[0],
                                                'type': k.split('.')[0],
                                                'name': k.split('.')[1],
                                                'p_gen': v})
                    elif 'demand' in key:
                        demand_data.append({'input': key.split('[')[1].split(']')[0],
                                           'type': k.split('.')[0],
                                           'name': k.split('.')[1],
                                           'p_dem': v})
                    elif 'storage' in key:
                        storage_data.append({'input': key.split('[')[1].split(']')[0],
                                           'type': k.split('.')[0],
                                           'name': k.split('.')[1],
                                           'soc': v})
                    elif 'curtail' in key:
                        if v and v != 0 and v is not None:
                            try:
                                curtail = v
                            except KeyError:
                                continue
            generators = pd.DataFrame()
            demands = pd.DataFrame()
            storages = pd.DataFrame()

            if generators_data:
                generators = pd.DataFrame(generators_data).set_index('input').sort_index()
            if demand_data:
                demands = pd.DataFrame(demand_data).set_index('input').sort_index()
            if storage_data:
                storages = pd.DataFrame(storage_data).set_index('input').sort_index()

            _cache[eid] = self.entities[eid].gpcontrol(generators, demands, storages, curtail)

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
            try:
                self._cache[eid]
            except KeyError:
                continue
            for attr in attrs:
                if attr in self.incr_attr:
                    # Extract index from attribute string
                    try:
                        index = int(attr.split('[')[1].split(']')[0])
                        data[eid][attr] = self._cache[eid][attr.split('[')[0]][index]
                    except KeyError and TypeError and IndexError:
                        data[eid][attr] = None

                elif attr == 'excess':  # flow2e = energy to electrolyser
                    data[eid][attr] = self._cache[eid]['excess']
                elif attr == 'deficit':
                    data[eid][attr] = self._cache[eid]['deficit']
                elif attr == 'net':
                    data[eid][attr] = self._cache[eid]['net']
        return data
def main():
    mosaik_api.start_simulation(gpcontrolSim(), 'GPController-Illuminator')
if __name__ == '__main__':
    main()
