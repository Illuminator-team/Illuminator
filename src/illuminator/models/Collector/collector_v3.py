from illuminator.builder import IlluminatorModel, ModelConstructor
import arrow
import pandas as pd
from illuminator.engine import current_model


# construct the model
class Collector(ModelConstructor):
    """
    A model for writing time series data to CSV files.

    This model writes data to a CSV file line by line, synchronizing with simulation time.
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

        
        #self.datafile = open(self.file_path, 'w', encoding='utf-8')
        #self.modelname = 'CSV'

        #super().__init__(**kwargs)  # re-initialise the outputs now that new outputs are configured 


    # def init(self, sid, time_resolution=1, **sim_params):
    #     # print("check")
    #     meta = super().init(sid, time_resolution, **sim_params)
    #     return meta


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
        self.time += 1  # keep track of the number of calls to step IN THIS FILE
        current_date = self.start_date.shift(seconds=time * self.time_step_size * self.time_resolution)  # start date  +  number of calls * iterations per call * time per iteration, aka time per call

        input_data = self.unpack_inputs(inputs)
    
        df = self.inputs2df(inputs)
        df['datetime'] = current_date.format('YYYY-MM-DD HH:mm:ss')
        df = df.set_index('datetime')
        # df = df[self.items]  # put in the order as defined in the yaml file
        
        if time == 0:
            mode = 'w'
            header = True
        else:
            mode = 'a'
            header = False

        df.to_csv(self.file_path, sep=self.delimiter, mode=mode, header=header, index=True)

        return time + self.time_step_size  # int((self.next_row[0].int_timestamp - date.int_timestamp) / self.time_step_size)

    def inputs2df(self, inputs):
        group = inputs["time-based_0"]
        df = pd.DataFrame([{
            signal: next(iter(signal_payload.values()))["value"]
            for signal, signal_payload in group.items()
        }])
        return df
    
    def unpack_inputs(self, inputs):
        """
        Unpacks input values from connected simulators and processes them based on their message origin.

        Parameters:
        ----------
        inputs : dict
            Dictionary containing input values from connected simulators with their message origin
        return_sources : bool, optional
            If True, returns the sorurces of state messages along with their values. Defaults to False
            
        Returns
        --------
        data : dict
            Dictionary containing processed input values, summed for outputs or single values for states
        """
        data = {}
        for attrs in inputs.values():
            for attr, sources in attrs.items():
                for source, value in sources.items():
                    data[attr] = value['value']

        return data

# if __name__ == '__main__':
#     csv_model = CSV(csv)

#     print(csv_model.step(1))