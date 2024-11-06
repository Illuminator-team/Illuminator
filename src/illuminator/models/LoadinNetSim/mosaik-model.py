import mosaik_api
import pandas as pd

try:
    import Models.LoadinNetSim.model as Loadmodelset
except ModuleNotFoundError:
    import LoadinNetSim.model as Loadmodelset
else:
    import Models.LoadinNetSim.model as Loadmodelset

meta={
    'type':'time-based',
    'models':{
        'Loadset':{
            'public':True,
            'params':[
                'sim_start', #time start(str)
                'data_info',#data_info = {'start': '2015-02-01 00:00:00', 'resolution': 15 , 'unit': 'W'}
                'profile_file', #profile name
            ],
            'attrs':[],
        },
        'Load':{
            'public':False,
            'params':[],
            'attrs':[
                'P_out',
                'load_num',
                'node_id',

            ],
        },
    },
}

def eid(lid):
    return 'Load_create_%s' %lid


class LoadholdSim(mosaik_api.Simulator):
    def __init__(self) -> None:
        """
        Inherits the Mosaik API Simulator class and is used for python based simulations.
        For more information properly inheriting the Mosaik API Simulator class please read their given documentation.

        ...

        Attributes
        ----------
        self.time_resolution : float
            ???
        self.model : ???
            ???
        self.loads_by_eid : dict
            ???
        self._file_cache : dict
            ???
        self._offset : int
            ???
        self._cache : dict
            Used in the step function to store the values after running the python model of the technology
        """
        super().__init__(meta)

        self.time_resolution=None
        self.model=None
        self.loads_by_eid={}
        self._file_cache={}
        self._offset=0
        self._cache={}


    def init(self, sid:str, time_resolution:float) -> dict:
        """
        Initialize the simulator with the ID `sid` and pass the `time_resolution` and additional parameters sent by mosaik.

        ...

        Parameters
        ----------
        sid : str
            The String ID of the class (???)
        time_resolution : float
            ???
        
        Returns
        -------
        self.meta : dict
            The metadata of the class
        """
        self.time_resolution=float(time_resolution)
        return self.meta

    def create(self, num:int, model:str, sim_start:str, data_info, profile_file) -> list:
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
        data_info : ???
            ???
        profile_file : ???
            ???
        Returns
        -------
        list
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
        if num != 1 or self.model:
            raise ValueError('Can only create one set of loads.')
        if profile_file.endswith('csv'):
            pf=pd.read_csv(profile_file)
        else:
            pf=pd.read_excel(profile_file)

        self.model=Loadmodelset.LoadModel(data_info,pf)
        self.loads_by_eid={
            eid(i):load for i, load in enumerate(self.model.loads)
        }
        # A time offset in minutes from the simulation start to the start
        # of the profiles.
        self._offset = self.model.get_delta(sim_start)
        return[{
            'eid':'Loadset_0',
            'type':'Loadset',
            'rel':[],
            'children':
                [{'eid': eid(i),
                'type':'Load',
                'rel':[],}for i,_ in enumerate(self.model.loads)],
        }]

    def step(self,time:int,inputs:dict,max_advance:int) -> int:
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
        int
            Return the new simulation time, i.e. the time at which ``step()`` should be called again.
        """
        # "time" has self.time_resolution (seconds per integer step).
        # Convert to minutes and add the offset if sim start > start date of
        # the profiles.
        minutes=int(time*self.time_resolution // 60)
        minutes_offset=minutes+self._offset
        cache={}
        data=self.model.get(minutes_offset)
        #print(data)
        for hid, d in enumerate(data):
            cache[eid(hid)]=d
        self._cache=cache
        return int((minutes + self.model.resolution) * 60
                   / self.time_resolution)

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
                if attr == 'P_out':
                    val = self._cache[eid]
                else:
                    val = self.loads_by_eid[eid][attr]
                data[eid][attr] = val
        return data

def main():
    return mosaik_api.start_simulation(LoadholdSim(),'Loadholdset simulation')























