# only can build one battery model
import mosaik.scheduler
import mosaik_api_v3 as mosaik_api
# try:
import illuminator.models.Battery.battery_model as batterymodelset
# except ModuleNotFoundError:
#     import battery_model as batterymodelset
# else:
#     import Models.Battery.battery_model as batterymodelset

import pandas as pd

#todo: convert this battery model simAPI to a controller api. This becomes a mosaik API to start the battery and the electrolyser.
#      A condition checks the battery SOC and then initiates the electrolyser.

meta = {
    'type': 'hybrid',
    'models': {
        'Batteryset': {
            'public': True,
            'params': [
                # these are the parameters which we defined in the __init__() of the python file
                'initial_set',  # initial_soc
                'battery_set',  # max_p,min_p,max_energy,charge_efficiency,discharge_efficiency, soc_min,soc_max
                'sim_start',  # this is an additional parameter we are passing.

            ],
            'attrs': [  # anything followed by self. in the python file is an attribute. We can have new ones too.
                'battery_id',  # new attribute we provide here for the first time.
                # 'p_ask',  # present in python file.
                'flow2b',
                'p_out',  # in the python file this existed in the re_params.
                          # re_params returns values from the python file, so we need to have it here so that mosaik
                          # can connect them and allow data flow.
                'p_in',
                'soc',    # present in python file.
                'mod',    # 0:no action, 1:charge, -1:discharge  # in the python file this existed in the re_params.
                          # re_params returns values from the python file, so we need to have it here so that mosaik
                          # can connect them and allow data flow.
                'flag',   # present in the python file.
                'time',
                'energy_drain',
                'energy_consumed',
            ],
            'trigger': [],              #'flag2b' if we want async behaviour
        },
    },
}


class BatteryholdSim(mosaik_api.Simulator):  # this is the main class that is running in Mosaik.
    def __init__(self) -> None:
        """
        Inherits the Mosaik API Simulator class and is used for python based simulations.
        For more information properly inheriting the Mosaik API Simulator class please read their given documentation.

        ...

        Attributes
        ----------
        self.meta : dict
            Contains metadata of the control sim such as type, models, parameters, attributes, etc.. Created via controlSim's parent class.
        self.entities : dict
            The stored model entity of the technology model
        self.eid_prefix : string
            The prefix with which each entity's name/eid will start
        self._cache : dict
            Used in the step function to store the values after running the python model of the technology
        self._data_next : dict
            ???
        self.soc : dict
            State of charge for a specific battery
        self.flag : dict
            ???
        self.test : list
            ???
        self.pflag : list
            ???
        """
        super().__init__(meta)  # through this command we are passing more information about the model to the subclass we have created under the main
        # class - simulator

        # all these attributes are being stored in the common data flow reference model of Mosaik
        self.entities = {}  # we store the model entity of our technology model
        self.eid_prefix = 'Battery_' # every entity that we create will start with 'Battery_
        self._cache = {}
        self._data_next = {}
        self.soc = {}
        self.flag = {}
        self.test = []
        self.pflag = []



        # this command runs only once when the simulation starts from the scenario file
    def init(self, sid:str, time_resolution:float,step_size:int=900) -> dict:  # sid and time_resolution are the positional arguments. Rest all we want to put will be keyword argument
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
        self.sid = sid
        self.time_resolution = time_resolution
        self.step_size = step_size
        return self.meta

    def create(self, num:int, model:str, initial_set:dict, battery_set:dict, sim_start:str) -> list:
        """
        Create `num` instances of `model` using the provided parameters

        ...

        Parameters
        ----------
        num : int
            The number of model instances to create
        model : str
            `model` needs to be a public entry in the simulator's ``meta['models']``
        initial_set : dict
            Gives the initial state of charge values
        battery_set : dict
            Gives the initial battery data (soc_max, soc_min, flag, discharge efficiency, etc.)
        sim_start : str
            Date and time (YYYY-MM-DD hh:mm:ss) of the start of the simulation in string format
        
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
        # next_eid=len(self.model)
        self._entities = []

        # for i in range(next_eid,next_eid+num):

        # num is the number of models of battery we want.
        for i in range(num):
            # we provide an ID to each entity we create. %s%d will be replaced by the values of eid_prefix and i
            self.eid = '%s%d' % (self.eid_prefix, i)

            # new instance of the battery is created
            # batterymodelset is the name we gave to the model (the battery python model) while importing it
            # BatteryModel is the class present in the model (the battery python model)
            # initial_set and battery_set are the parameters we want our battery_instance to have
            battery_instance = batterymodelset.BatteryModel(initial_set, battery_set)
            # self.model is an empty dictionary which will hold the entities we create. So sor every eid_b, the
            # self.model dictionary will hold a corresponding battery_instance !
            self.entities[self.eid] = battery_instance
            # self.battery_set[eid_b]=battery_set
            # self.battery_initial[eid_b]=initial_set

            # for every eid_b, we want to communicate the initial soc, and hence for every eid_b, we store the soc value.
            self.soc[self.eid] = initial_set['initial_soc']
            self.flag[self.eid] = battery_set['flag']
            self._cache[self.eid] = {'soc': self.soc[self.eid], 'flag': self.flag[self.eid], 'p_out': 0, 'p_in' : 0, 'mod' : 0}
            # self.battery_flag={}

            # the empty entities list will hold the following information.
            self._entities.append({'eid': self.eid, 'type': model, 'rel': [], })
            # print(self._entities)

        return self._entities

# the step method tells the Mosaik when to initiate the next step and perform the calculations and repeat all the process again.
    # for the input, we need the values coming from another mosaik file. which means that file's output is our input.
    # the input has to be of a specific format.
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
        self.time = time
        current_time = (self.start + pd.Timedelta(time * self.time_resolution, unit='seconds'))
        print('from battery %%%%%%%%', current_time)
        for eid, attrs in inputs.items():  #raghav: In this model, the input should come from the controller p_ask
            # print(eid)
            # print(attrs)

            for attr, vals in attrs.items():
                if attr == 'flow2b':
                    self._cache[eid] = self.entities[eid].output_power(sum(vals.values()), self.soc[eid])

                    # self._cache[eid] = self.entities[eid].output_power(energy_ask, self.soc[eid])          # * max_advance if trigger

                    # print(self._cache[eid])
                    # [p_out:,soc:,flag:]
                    self.soc[eid] = self._cache[eid]['soc']
                    self.flag = self._cache[eid]['flag']
                    check = list(self.soc.values())
                    check2 = check[0]  # this is so that the value that battery sends is dictionary and not a dictionary of a dictionary.
                #    out = yield self.mosaik.set_data({'Battery-0': {'Controller-0.ctrl_0': {'soc': check2}}})  # this code is supposed to hold the soc value and


        return None

# this method is used to get the specific values we want and write them in a new file.
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
#         # self.test.append(self.flag)  # if we do this code, then we end up with a list which increases with each step. Duh!
#         # try:
#         #     # the following code takes the vale at -2 position in the list. The -2 vale of the list represents the value of the previous step
#         #     self.pflag = self.test[-2]  # first python tries this line of code. If it doesnt work then it follows the code in except.
#         # except:
#         #     self.pflag = self.flag
#
        for eid, attrs in outputs.items():
            model = self.entities[eid]
            # data['time'] = self.time
            data[eid] = {}
            for attr in attrs:
                # data[eid][attr] = getattr(model, attr)  # this line of a code is short form for the following code which is commented out
                if attr == 'p_out':
                    data[eid][attr] = self._cache[eid]['p_out']
                elif attr == 'soc':
                    data[eid][attr] = self._cache[eid]['soc']
                elif attr == 'mod':
                    data[eid][attr] = self._cache[eid]['mod']
                elif attr == 'battery_id':
                    data[eid][attr] = eid
                elif attr == 'flag':
                    data[eid][attr] = self._cache[eid]['flag']
                elif attr == 'p_in':
                    data[eid][attr] = self._cache[eid]['p_in']
                # elif attr == 'energy_consumed':
                #     data[eid][attr] = self._cache[eid]['energy_consumed']
                # elif attr == 'energy_drain':
                #     data[eid][attr] = self._cache[eid]['energy_drain']
                # if eid in self._cache:


        return data


def main():
    mosaik_api.start_simulation(BatteryholdSim(), 'Battery-Simulator')

    import mosaik_api_v3

    mosaik_api_v3.start_simulation()

if __name__ == "__main__":
    main()
