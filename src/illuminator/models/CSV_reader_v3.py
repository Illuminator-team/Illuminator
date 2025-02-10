from illuminator.builder import IlluminatorModel, ModelConstructor
import arrow
from illuminator.engine import current_model

# Define the model parameters, inputs, outputs...
# csv = IlluminatorModel(
#     parameters={'time_resolution': None,
#                 'start': None,
#                 'date_format': None,
#                 'delimiter': ',',
#                 'datafile': None,             
#                 },
#     inputs={},
#     outputs={'next_row'},
#     states={'next_row'},
#     time_step_size=1,
#     time=None
# )

# construct the model
class CSV(ModelConstructor):
    """
    CSV is a model for reading CSV files.
    parameters : dict
        Default parameters for the CSV reader.
        Input attributes for the model.
        Output attributes for the model.
    states : dict
        State attributes for the model.
    time_step_size : int
        The size of each time step in the simulation.
    time : None
        The current time in the simulation.
    """

    parameters={'date_format': '',
                'delimiter': ',',
                'datafile': '',             
                }
    inputs={}
    outputs={'next_row': ''}
    states={}
    time_step_size=1
    time=None

    # start_date = None
    # date_format = None
    # delimiter = None
    # datafile = None
    # next_row = None
    # modelname = None
    # attrs = None
    # #self.eids = []
    # cache = None

    def __init__(self, **kwargs) -> None:
        """
        Initializes the CSV reader model with the provided parameters.
        Keyword Args:

        Raises:
            ValueError: If the start date is not found in the CSV file.
        Attributes:
            delimiter (str): The delimiter used in the CSV file.
            date_format (str): The date format used in the CSV file.
            start_date (Arrow): The start date as an Arrow object.
            next_date (Arrow): The next date as an Arrow object.
            file_path (str): The file path to the CSV file.
            datafile (file object): The file object for the opened CSV file.
            attrs (list): The list of attribute names from the CSV file.
        """
        super().__init__(**kwargs)
        self.delimiter = self._model.parameters.get('delimiter')
        self.date_format = self._model.parameters.get('date_format')
        self.start_date = arrow.get(self._model.parameters.get('start'), self.date_format)
        self.next_date = self.start_date
        self.file_path = self._model.parameters.get('file_path')
        self.send_row = self._model.parameters.get('send_row', False)
        self.cache = {}
        
        # Open the CSV file for reading
        self.datafile = open(self.file_path, 'r', encoding='utf-8')
        #self.modelname = 'CSV'

        next(self.datafile).strip() # Skip header line
        # Get attribute names and strip optional comments
        self.columns = next(self.datafile).strip().split(self.delimiter)
        if self.send_row:
            self.attrs = ['row']
            current_model.setdefault('states', {})['row'] = None  # add attribute to states (non-physical message)
        else:
            attrs = self.columns[1:]  # get rid of the TIME column
            for i, attr in enumerate(attrs):
                try:
                    # Try stripping comments
                    attr = attr[:attr.index('#')]
                except ValueError:
                    pass
                attr = attr.strip()
                attrs[i] = attr
                current_model.setdefault('states', {})[attr] = None  # add attribute to states (non-physical message)
            self.attrs = attrs

        super().__init__(**kwargs)  # re-initialise the outputs now that new outputs are configured 

        self._read_next_row()
        if self.start_date < self.next_row[0]:
            raise ValueError('Start date "%s" not in CSV file.' %
                             self.start_date.format(self.date_format))
        while self.start_date > self.next_row[0]:
            self._read_next_row()
            if self.next_row is None:
                raise ValueError('Start date "%s" not in CSV file.' %
                                 self.start_date.format(self.date_format))
    
    # 
    # run super().init(self, sid, time_resolution=1, **sim_params)


    def init(self, sid, time_resolution=1, **sim_params):
        # print("check")
        meta = super().init(sid, time_resolution, **sim_params)
        return meta


    def step(self, time, inputs, max_advance=900) -> None:
        """
        Perform one step of the simulation.

        Parameters:
        -----------
        time : int
            The current time of the simulation.
        inputs : dict
            Input values for the simulation step.
        max_advance : int
            Maximum time the simulator can advance (default is 900 seconds).

        Returns:
        --------
        int
            The next simulation time.
        """
        data = self.next_row
        # print("NEW CSV DATA: ", data)
        if data is None:
            raise IndexError('End of CSV file reached.')

        # Check date
        date = data[0]
        expected_date = self.start_date.shift(seconds=time * self.time_step_size * self.time_resolution)  # start date  +  number of calls * iterations per call * time per iteration, aka time per call
        if date != expected_date:
            raise IndexError(f'Wrong date "{date}", expected "{expected_date}"')

        # Put data into the cache for get_data() calls
        self.cache = {}
        if self.send_row:
            row = {}
            row[self.columns[0]] = date.format(self.date_format)  # make the date a string again to be able to send it as a json
            for key, val in zip(self.columns[1:], data[1:]):
                row[key] = val
            self.cache['row'] = row
        else:
            for attr, val in zip(self.attrs, data[1:]):
                self.cache[attr] = float(val)
            
        self.set_states(self.cache)

        self._read_next_row()
        if self.next_row is not None:
            return time + self.time_step_size  # int((self.next_row[0].int_timestamp - date.int_timestamp) / self.time_step_size)
        else:
            return max_advance
        

    # def get_data(self, outputs:dict) -> dict:
    #     """
    #     Return the data for the requested attributes in `outputs`
        
    #     ...

    #     Parameters
    #     ----------
    #     outputs : dict 
    #         Maps entity IDs to lists of attribute names whose values are requested::

    #         {
    #             'eid_1': ['attr_1', 'attr_2', ...],
    #             ...
    #         }

    #     Returns
    #     -------
    #     data : dict
    #         The return value is a dict of dicts mapping entity IDs and attribute names to their values::

    #         {
    #             'eid_1: {
    #                 'attr_1': 'val_1',
    #                 'attr_2': 'val_2',
    #                 ...
    #             },
    #             ...
    #             'time': output_time (for event-based sims, optional)
    #         }

    #     See Also
    #     --------
    #     Time-based simulators have set an entry for all requested attributes, whereas for event-based and hybrid simulators this is optional (e.g.
    #     if there's no new event). Event-based and hybrid simulators can optionally set a timing of their non-persistent output attributes via a *time* entry, which is valid
    #     for all given (non-persistent) attributes. If not given, it defaults to the current time of the step. Thus only one output time is possible
    #     per step. For further output times the simulator has to schedule another self-step (via the step's return value).
    #     """
    #     data = {}
    #     for eid, attrs in outputs.items():
    #         if eid not in self.model_entities:
    #             raise ValueError('Unknown entity ID "%s"' % eid)

    #         data[eid] = {}
    #         for attr in attrs:
    #             data[eid][attr] = self.cache[attr]

        return data

    def _read_next_row(self) -> None:
        """
        Reads the next row within the file object.
        """
        try:
            self.next_row = next(self.datafile).strip().split(self.delimiter)
            self.next_row[0] = arrow.get(self.next_row[0], self.date_format)
        except StopIteration:
            self.next_row = None

    def finalize(self) -> None:
        """
        Closes the file object within `self.datafile`.
        """
        self.datafile.close()

# if __name__ == '__main__':
#     csv_model = CSV(csv)

#     print(csv_model.step(1))