import arrow

import mosaik_api_v3 as mosaik_api


__version__ = '1.2.0'


class CSV(mosaik_api.Simulator): # simulator that reads a CSV file and provides data to entities. 
    def __init__(self) -> None:
       # this is an a middleware that reads a CSV file and provides data to entities and connects to another model.
        """
        Inherits the Mosaik API Simulator class and is used for python based simulations.
        For more information properly inheriting the Mosaik API Simulator class please read their given documentation.

        ...

        Attributes
        ----------
        self.time_resolution : ???
            ???
        self.start_date : ???
            ???
        self.date_format : ???
            ???
        self.delimiter : ???
            ???
        self.datafile : ???
            The file object which will be used for reading
        self.next_row : ???
            ???
        self.modelname : ???
            ???
        self.attrs : ???
            ???
        self.eids : list
            ???
        self.cache : ???
            ???
        """

        super().__init__({'models': {}})
        self.time_resolution = None
        self.start_date = None
        self.date_format = None
        self.delimiter = None
        self.datafile = None
        self.next_row = None
        self.modelname = None
        self.attrs = None
        self.eids = []
        self.cache = None

    def init(self, sid:str, time_resolution:float, sim_start, datafile, date_format:str='YYYY-MM-DD HH:mm:ss',
             delimiter:str=',') -> dict:
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
        sim_start : ???
            ???
        datafile : ???
            ???
        date_format : str
            The expected date format
        delimitre : str
            The character which will be used as a delimiter

        Returns
        -------
        self.meta : dict
            The metadata of the class
        """
        self.time_resolution = float(time_resolution)
        self.delimiter = delimiter
        self.date_format = date_format
        self.start_date = arrow.get(sim_start, self.date_format)
        self.next_date = self.start_date

        self.datafile = open(datafile)
        self.modelname = 'CSV' # next(self.datafile).strip() 
        # model name in META is set to the first line of the CSV file

        next(self.datafile).strip() # Skip header line
        # Get attribute names and strip optional comments
        attrs = next(self.datafile).strip().split(self.delimiter)[1:]
        for i, attr in enumerate(attrs):
            try:
                # Try stripping comments
                attr = attr[:attr.index('#')]
            except ValueError:
                pass
            attrs[i] = attr.strip()
        self.attrs = attrs

        self.meta['type'] = 'time-based'

        self.meta['models'][self.modelname] = {
            'public': True,
            'params': [],
            'attrs': attrs,
        }

        # Check start date
        self._read_next_row()
        if self.start_date < self.next_row[0]:
            raise ValueError('Start date "%s" not in CSV file.' %
                             self.start_date.format(self.date_format))
        while self.start_date > self.next_row[0]:
            self._read_next_row()
            if self.next_row is None:
                raise ValueError('Start date "%s" not in CSV file.' %
                                 self.start_date.format(self.date_format))

        return self.meta

    def create(self, num:int, model:str) -> list:
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
        if model != self.modelname:
            raise ValueError('Invalid model "%s" % model')

        start_idx = len(self.eids)
        entities = []
        for i in range(num):
            eid = '%s_%s' % (model, i + start_idx)
            entities.append({
                'eid': eid,
                'type': model,
                'rel': [],
            })
            self.eids.append(eid)
        return entities

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
        data = self.next_row
        if data is None:
            raise IndexError('End of CSV file reached.')

        # Check date
        date = data[0]
        expected_date = self.start_date.shift(seconds=time*self.time_resolution)
        if date != expected_date:
            raise IndexError('Wrong date "%s", expected "%s"' % (
                date.format(self.date_format),
                expected_date.format(self.date_format)))

        # Put data into the cache for get_data() calls
        self.cache = {}
        for attr, val in zip(self.attrs, data[1:]):
            self.cache[attr] = float(val)

        self._read_next_row()
        if self.next_row is not None:
            return time + int((self.next_row[0].int_timestamp - date.int_timestamp)/self.time_resolution)
        else:
            return max_advance

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
            if eid not in self.eids:
                raise ValueError('Unknown entity ID "%s"' % eid)

            data[eid] = {}
            for attr in attrs:
                data[eid][attr] = self.cache[attr]

        return data

    def _read_next_row(self) -> None:
        """
        Reads the next row within the file object
        """
        try:
            self.next_row = next(self.datafile).strip().split(self.delimiter)
            self.next_row[0] = arrow.get(self.next_row[0], self.date_format)
        except StopIteration:
            self.next_row = None

    def finalize(self) -> None:
        """
        Closes the file object within `self.datafile`
        """
        self.datafile.close()


def main():
    return mosaik_api.start_simulation(CSV(), 'mosaik-csv simulator')


if __name__ == "__main__":
    main()
