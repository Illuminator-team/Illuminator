
import itertools
import mosaik_api_v3 as mosaik_api
#import PV.PV_model as PV_model
try:
    import illuminator.models.PV.pv_model as PV_model
except ModuleNotFoundError:
    raise ModuleNotFoundError('PV model not found')
    # import illuminator.models.PV as PV_model
# else:
#     import Models.PV.pv_model as PV_model
import pandas as pd
import itertools

meta = {
    'type': 'event-based', #if reading from a csv file then it is time based
    'models': {
        'PvAdapter': { # This must match the model type name in YAMl config file
            'public': True,
            'params': ['panel_data',
                       'm_tilt','m_az', 'cap',  'sim_start', 'output_type'],
            # and are attrs the specific outputs we want from the code? to connect with other models
            'attrs': ['pv_id', 'G_Gh', 'G_Dh', 'G_Bn', 'Ta', 'hs', 'FF', 'Az', 'pv_gen', 'total_irr'],
        },
    },
}

class PvAdapter(mosaik_api.Simulator):
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
        self.mods : dict
            ???
        self._cache : dict
            Used in the step function to store the values after running the python model of the technology
        """
        super(PvAdapter, self).__init__(meta)
        self.eid_prefix='pv_'
        self.entities = {}  # every entity that we create of PV gets stored in this dictionary as a list
        self.mods = {}
        self._cache = {}  #we store the final outputs after calling the python model (#PV1) here.

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
        entities = []
        for i in range (num):
            eid = '%s%d' % (self.eid_prefix, i)

            # we are creating an instance for PV and call the python file for that. **model_params refers to the
            # parameters we have mentioned above in the META. New instance will have those parameters.
            model_instance = PV_model.PV_py_model(**model_params)
            self.entities[eid] = model_instance
            entities.append({'eid': eid, 'type': model})
        # print(entities)
        return entities

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
        # in this method, we call the python file at every data interval and perform the calculations.
        current_time = (self.start + pd.Timedelta(time * self.time_resolution,
                                                  unit='seconds'))  # timedelta represents a duration of time
        print('from pv %%%%%%%%%', current_time)
        # print('#inouts: ', inputs)
        for eid, attrs in inputs.items():
            # print('#eid: ', eid)
            # print('#attrs: ', attrs)
            # and relate it with the information in mosaik document.
            v = []  # we create this empty list to hold all the input values we want to give since we have more than 2
            for attr, vals in attrs.items():

                # print('#attr: ', attr)
                # print('#vals: ', vals)
                # inputs is a dictionary, which contains another dictionary.
                # value of U is a list. we need to combine all the values into a single list. But is we just simply
                #   append them in v, we have a nested list, hence just 1 list. that creates a problem as it just
                #   gives all 7 values to only sun_az in the python model and we get an error that other 6 values are missing.
                u = list(vals.values())
                # print('#u: ', u)
                v.append(u)  # we append every value of u to v from this command.
            # print('#v: ', v)

            # the following code helps us to convert the nested list into a simple plain list and we can use that simply
            v_merged = list(itertools.chain(*v))
            # print('#v_merged: ', v_merged)
            self._cache[eid] = self.entities[eid].connect(v_merged[0], v_merged[1], v_merged[2], v_merged[3],
                                                          v_merged[4], v_merged[5], v_merged[6]) # PV1
            # print(self._cache)
            # print('# cache[eid]: ', self._cache[eid])
    # the following code desnt work because it just put one value 7 times :/! Dumb move
                    # self._cache[eid] = self.entities[eid].connect(u, u, u, u, u, u, u)
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

        # to write the data in an external file, we use this method. This API inturn calls a file within Mosaik
        # which handles the writing of the outputs provided the attrs are present in the base python model file you made

        for eid, attrs in outputs.items():
            # model = self.entities[eid]
            # data['time'] = self.time
            data[eid] = {}

            for attr in attrs:
                # if we want more values to print in the output file, mimic the below for new attributes and make sure
                # those parameters are present in the re_params in the python file of the model
                if attr == 'pv_gen':
                    data[eid][attr] = self._cache[eid]['pv_gen']
                elif attr == 'total_irr':
                    data[eid][attr] = self._cache[eid]['total_irr']
        return data

def main():
    mosaik_api.start_simulation(PvAdapter(), 'PV-Illuminator')
if __name__ == '__main__':
    main()
