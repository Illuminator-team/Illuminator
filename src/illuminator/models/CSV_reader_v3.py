from illuminator.builder import IlluminatorModel, ModelConstructor
import arrow
from illuminator.engine import current_model


# construct the model
class CSV(ModelConstructor):
    """
    A model for reading time series data from CSV files.

    This model reads data from a CSV file line by line, synchronizing with simulation time.
    The CSV file should contain a header row with column names and a timestamp column.

    Parameters
    ----------
    date_format : str
        Format of the date/time column in the CSV file
    delimiter : str
        Column delimiter character in the CSV file (default ',')
    datafile : str / list
        [list of] Path to the CSV file to read from
    send_row : bool
        If True, sends the entire row as a dictionary under the key 'row'. If False, sends individual columns as separate states.
    

    Inputs
    ----------
    file_index : int (optional)
        If multiple files are provided, this input selects which file to read from.

    Outputs
    ----------
    None

    States
    ----------
    next_row : dict (optional, if send_row is True)
        The next row of data read from the CSV file.
    <column_name> : float (for each column in the CSV file, if send_row is False)
        The value of each column in the current row.
    """

    # parameters={'date_format': '',
    #             'delimiter': ',',
    #             'datafile': '',             
    #             }
    # inputs={'next_row': '',}
    # outputs={}
    # states={}
    # time_step_size=1
    # time=None
    
    def skip_header(self):
        next(self.datafile).strip() # Skip header line
        return

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
        self.tzinfo = self._model.parameters.get('tzinfo', 'Europe/Amsterdam')  # Default timezone is Europe/Amsterdam
        self.start_date = arrow.get(self._model.parameters.get('start'), self.date_format, tzinfo=self.tzinfo)  # Convert start date to Arrow object with timezone 
        self.expected_date = self.start_date  # The date we expect to read from the CSV file at first is the start date
        self.next_date = self.start_date
        self.file_path = self._model.parameters.get('file_path')
        self.send_row = self._model.parameters.get('send_row', False)
        self.cache = {}
        
        # Open the CSV file for reading
        if type(self.file_path) is list:
            self.file_paths = self.file_path
        else:
            self.file_paths = [self.file_path]
        
        self.file_path = self.file_paths[self._model.inputs.get('file_index', 0)]
        self.datafile = open(self.file_path, 'r', encoding='utf-8')
        #self.modelname = 'CSV'

        self.skip_header()
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


    def change_file(self, file_index) -> None:
        """
        Change the CSV file being read based on the 'file_index' input.
        """
        if file_index < 0 or file_index >= len(self.file_paths):
            raise IndexError(f'file_index {file_index} out of range for available files.')
        if self.file_paths[file_index] != self.file_path:
            # Close current file and open new one
            self.datafile.close()
            self.file_path = self.file_paths[file_index]
            self.datafile = open(self.file_path, 'r', encoding='utf-8')
            self.skip_header()
            self._read_next_row()


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
        input_data = self.unpack_inputs(inputs)
        if 'file_index' in input_data:
            self.change_file(file_index=input_data['file_index'])

        data = self.next_row
        # print("NEW CSV DATA: ", data)
        if data is None:
            raise IndexError('End of CSV file reached.')

        # Check date
        date = data[0]
        if date != self.expected_date:
            raise IndexError(f'Wrong date "{date}", expected "{self.expected_date}"')

        # Update expected date for the next step
        self.expected_date = self.expected_date.shift(seconds=self.time_step_size * self.time_resolution)  # expected date is the start date + number of calls * iterations per call * time per iteration, aka time per call

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


    def _read_next_row(self) -> None:
        """
        Reads the next row within the file object.
        """
        try:
            self.next_row = next(self.datafile).strip().split(self.delimiter)
            self.next_row[0] = arrow.get(self.next_row[0], self.date_format, tzinfo=self.tzinfo)  # Convert the first column to an Arrow object
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