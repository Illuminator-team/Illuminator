from collections import namedtuple

import mosaik_api
import numpy as np
import pandas as pd

#import Wind.Wind_model as Wind_model


try:
    import Models.Wind.Wind_model as Wind_model
except ModuleNotFoundError:
    import Wind_model as Wind_model
else:
    import Models.Wind.Wind_model as Wind_model

META = {
    'type': 'event-based',
    #wind is an event based event because the event here is a wind speed. It doesnt purely run because of time interval, I think.
    # if I put it to time-based, there is type error:
    # File "C:\Users\ragha\AppData\Local\Programs\Python\Python310\lib\site-packages\mosaik\scheduler.py", line 405, in step
    #     sim.progress_tmp = next_step - 1
    # TypeError: unsupported operand type(s) for -: 'NoneType' and 'int'

    'models': {
        'windmodel': {
            'public': True,
            'params': ['p_rated', 'u_rated', 'u_cutin', 'u_cutout', 'cp', 'sim_start', 'output_type', 'diameter'],
            'attrs': ['wind_id',
                      'wind_gen',  # in the python file this existed in the re_params.
                          # re_params returns values from the python file, so we need to have it here so that mosaik
                          # can connect them and enter the values.
                      'u'],
        },
    },
}


class WindSim(mosaik_api.Simulator):
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
        self.eid_prefix = 'wind_'  # every entity that we create will start with 'wind_'
        self.entities = {}  # we store the model entity of our technology model
        self._cache = {}  # used in the step function to store the values after running the python model of the technology
        # self.start_date = None

    # the following API call is will be called only once when we initiate the model in the scenario file.
    # we can use this to pass additional initialization tasks
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
        # print(type(self.entities))
        # next_eid = len(self.entities)
        # print('from create of SimAPI:', next_eid)
        entities = []
        # print(next_eid)  # working (20220524)

        for i in range (num):
            eid = '%s%d' % (self.eid_prefix, i)
            # print ('123checkkkkkkkkkkkkkkk', eid)
            model_instance = Wind_model.wind_py_model(**model_params)
            self.entities[eid] = model_instance
            entities.append({'eid': eid, 'type': model})
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
        current_time = (self.start +
                        pd.Timedelta(time * self.time_resolution, unit='seconds')) # timedelta represents a duration of time
        print('from wind %%%%%%%%%%', current_time)

        for eid, attrs in inputs.items():
            # raghav: Inputs come from a CSV file which needs to be read by a Mosaik # CSV reader -
            # and it gives the output in a manner we want. The output from the CSV file will be the Input here.
            # they are connected in the scenario file. ##W1 (see W1 in comments in scenario file to understand)
            # print(eid)
            # print(attrs)
            for attr, vals in attrs.items():
                if attr == 'u':
                    u = list(vals.values())[0]
                    # print(u)
                    self._cache[eid] = self.entities[eid].generation(u)  #not necessary to have u in brackets. It is not
                    # necessary to keep the same name as the one in python file

                    # in the above line, we have called our entity of wind model we created in create followed by a
                    # definition 'generation'. Since self.entities = model_instance and model instance calls out wind
                    # python model, so in this step we are called the function 'generation' and give it a value for u.
                    # This step makes the python file run and do the calculations for us of wind_gen.
                    # print(self._cache[eid])
                    # [wind_gen:,soc:,flag:]
                    # self.soc[eid] = self._cache[eid]['soc']
                    # self.battery_flag[eid]=self._cache[eid]['flag']
                    # print(self._cache)

        return None
        # # CURRENTLY THE INPUT IS THE WIND SPEED FILE BUT IT CAN BE CHANGED TO THE SUM OF pv AND wind AND THE grid load
        # print (' entered STEP of SimAPI')
        # self.time=time
        #
        # for eid, model_instance in self.entities.items():
        #     for i in wind_data:
        #         model_instance.u = i
        #         print(model_instance[0])
        # print('Exited STEP of SimAPI')
        # return time + 300

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
        data={}
        for eid, attrs in outputs.items():
            # model = self.entities[eid]
            # data['time'] = self.time
            data[eid]={}
            for attr in attrs:
                # if we want more values to print in the output file, mimic the below for new attributes and make sure
                # those parameters are present in the re_params in the python file of the technology
                if attr == 'wind_gen':
                    data[eid][attr] = self._cache[eid]['wind_gen']
                elif attr == 'u':
                    data[eid][attr] = self._cache[eid]['u']

        return data



def main():
    return mosaik_api.start_simulation(WindSim(), 'WindEnergy Simulator')

if __name__ == "__main__":
    main()
