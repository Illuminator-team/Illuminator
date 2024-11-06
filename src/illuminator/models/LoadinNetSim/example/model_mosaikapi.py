from typing import List, Dict, Union, Any

import mosaik_api
import loadmodel
import pandas as pd
import datetime

meta = {
    'type': 'time_based',
    'models': {
        'LoadModel': {
            'public': True,
            'params': [
                'num',
                'sim_start',  # (str)The start time for the simulation: "YYYY-MM-DD HH:SS"
                'pf_data',
            ],
            'attrs': [
                'P_out',  # Active power [W] of each load
                'name',
            ]
        }
    }
}


class LoadSim(mosaik_api.Simulator):
    def __init__(self) -> None:
        """
        Inherits the Mosaik API Simulator class and is used for python based simulations.
        For more information properly inheriting the Mosaik API Simulator class please read their given documentation.

        ...

        Attributes
        ----------
        self.meta : dict
            Contains metadata of the control sim such as type, models, parameters, attributes, etc.. Created via gpcontrolSim's parent class.
        self.time_resolution : int
            ???
        self.entities : dict
            The stored model entity of the technology model
        self.time : int
            ???
        self.cache_data : dict
            ???
        self._timeset : int
            ???
        self.model : ???
            ???
        self.load_id : ???
            ???
        """
        super().__init__(meta)
        self.time_resolution = 1
        self.entities = {}
        self.time = 0
        self.cachedata = {}
        self._timeset=0
        self.model = None
        self.load_id=None


    def init(self, sid:str, time_resolution:float=15*60) -> dict:
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
        
        Returns
        -------
        self.meta : dict
            The metadata of the class
        """
        self.time_resolution = time_resolution  #time_resolution is seconds
        print("The time_resolution of the load is:", self.time_resolution)
        return self.meta

    def create(self, num:int, model:str, sim_start:str, pf_data:pd.DataFrame) -> list:
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
        pf_data : pd.DataFrame 
            ???
        
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
        #pf_data(dataframe) sim_start(str),num(len(entity)
        entities=[]
        # pf, time_resolution, node_name, load_name
        self.load_id=pf_data.iloc[0].index[1:].to_list()
        self._timeset=pd.to_datetime(sim_start)

        # models=pf.iloc[0].index[1:].to_list()
        # model_series=pd.Series([2,1],index=["node_1,load_1","node_2,load_2"])
        for i in range(num):
            load_instance=loadmodel.LoadModel(pf_data, self.load_id[i])
            self.entities[self.load_id[i]]=load_instance
            entities.append({'id':self.load_id[i],'type':model})
        return entities

    def step(self, time:int, inputs:dict, max_advance:int) -> int:#time is iteration steps.
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
        minutes = int(time * self.time_resolution // 60)
        self.time = self._timeset + datetime.timedelta(minutes=minutes)
        cache = {}
        # self.time = self.time + datetime.timedelta(minutes=self.time_resolution )
        for eid, model_instance in self.entities.items():
            if eid in inputs:
                attrs=inputs[eid]
                for attr, values in attrs.items():
                    if attr=='P_out':
                        model_instance.P_out=values
                        print('the p_out of ',model_instance.name,"is changed!")

            data = model_instance.get(self.time)
            for hid, d in enumerate(data):
                cache['%s' % self.load_id[hid]] = d
            self._cache = cache

        return time+1

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
            model = self.entities[eid]
            data['time'] = self.time
            data[eid] = {}
            for attr in attrs:
                if attr not in self.meta['models']['ExampleModel']['attrs']:
                    raise ValueError('Unknown output attribute: %s' % attr)
                # Get model.val or model.delta:
                data[eid][attr] = getattr(model, attr)
        return data


def main():
    return mosaik_api.start_simulation(LoadSim())


# if __name__ =='__main__':
#     datafile = 'demo_lv_grid.csv'
#     pf_load = pd.read_csv(datafile)
#     START = '2014-01-01 00:00:00'
#     sim = model_mosaikapi.LoadSim()
#     sim.init('sid')
#     eneti = sim.create(sim_start=START, pf_data=pf_load)
