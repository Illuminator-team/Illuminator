import collections
import pandas as pd
import mosaik_api_v3 as mosaik_api
import os
import sqlite3
import paho.mqtt.client as mqtt
from urllib.parse import urlparse

META = {
    'type': 'hybrid',
    'models': {
        'Monitor': {
            'public': True,
            'any_inputs': True,
            'params': [],
            'attrs': [],
        },
    },
}
#import wandb
import sqlite3

class Collector(mosaik_api.Simulator):
    def __init__(self) -> None:
        """
        Inherits the Mosaik API Simulator class and is used for python based simulations.
        For more information properly inheriting the Mosaik API Simulator class please read their given documentation.

        ...

        Attributes
        ----------
        self.meta : dict
            Contains metadata of the control sim such as type, models, parameters, attributes, etc.. Created via gpcontrolSim's parent class.
        self.eid : string
            ???
        self.data : dict
            ???
        """
        super().__init__(META)
        self.eid = None
        self.data = collections.defaultdict(lambda: collections.defaultdict(dict))

    def init(self, sid:str, time_resolution:int, start_date, results_show,output_file,
             date_format:str='%Y-%m-%d %H:%M:%S',
             db_file:str='Result/result.db',
             mqtt_broker:str='mqtt://192.168.10.90:1883', mqtt_topic:str='TGVFCBB75',
             print_results:bool=False) -> dict:
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
        start_date : ???
            ???
        results_show : ???
            ???
        output_file : ???
            ???
        date_format : str
            The expected date formatting
        db_file : str
            The path of the database file
        mqtt_broker : str
            ???
        mqtt_topic : str
            ???
        print_results : bool
            Should the results be printed

        Attributes
        ----------
        self.time_resolution : float
            ???
        self.start_date : ???
            ???
        self.output_file : ???
            ???
        self.print_results : boolean
            Should the results be printed
        self.results_show : ???
            ???
        self.db_file : str
            The path of the database file
        self.mqtt_client : ???
            ???
        self.mqtt_topic : str
            ???
        self.mqtt_broker : str
            ???

        Returns
        -------
        self.meta : dict
            The metadata of the class
        """
        self.time_resolution = time_resolution
        self.start_date = pd.to_datetime(start_date, format=date_format)
        self.output_file = output_file
        self.print_results = print_results
        self.results_show=results_show
        self.db_file=db_file
        self.mqtt_client=None
        self.mqtt_topic=mqtt_topic
        self.mqtt_broker=mqtt_broker

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
        print('Collector create: hi')
        if num > 1 or self.eid is not None:
            raise RuntimeError('Can only create one instance of Monitor.')

        self.eid = 'Monitor'
        print('Collector create: bye')

        if self.results_show['database']==True:
            # if os.path.exists(self.db_file):
            #     os.remove(self.db_file)
            self.conn = sqlite3.connect(self.db_file)
            self.cursor = self.conn.cursor()
            #self.cursor.execute("ALTER TABLE pv_gen ADD COLUMN date DATATYPE;")
        if self.results_show['mqtt'] == True:
            self.mqtt_client = mqtt.Client()
            broker_url = urlparse(self.mqtt_broker)
            if broker_url.hostname and broker_url.port:
                self.mqtt_client.connect(broker_url.hostname, broker_url.port)
            else:
                print('hostname:', broker_url.hostname)
                print('port:', broker_url.port)
                raise ValueError('Invalid host.')

        return [{'eid': self.eid, 'type': model}]

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
        # print(inputs)
        current_date = (self.start_date
                        + pd.Timedelta(time * self.time_resolution, unit='seconds'))

        df_dict = {'date': current_date}

        data = inputs.get(self.eid, {})
        for attr, values in data.items():
            for src, value in values.items():
                self.data[src][attr][time] = value
                df_dict[f'{src}-{attr}'] = [value['value']]

        df = pd.DataFrame.from_dict(df_dict)
        columns = list(df.columns)
        # columns.remove('Controller1-0.time-based_0-dump')
        # columns.insert(3, 'Controller1-0.time-based_0-dump')
        # columns.remove('Controller1-0.time-based_0-flow2b')
        # columns.insert(1, 'Controller1-0.time-based_0-flow2b')
        # df = df[columns]
        df = df.set_index('date')

        if self.results_show['dashboard_show']==True:
            # TODO: raise warning, not implemented
            for key, value in df.items():
                wandb.log({key: value[0],
                           "custom_step":time/900})  # TODO replace 900 by something better

        if self.results_show['write2csv'] == True:
            if time == 0:
                # Overwrite the CSV file at the first time step
                df.to_csv(self.output_file, mode='w', header=True)
            else:
                if os.path.exists(self.output_file):
                    # Read existing CSV
                    existing_df = pd.read_csv(self.output_file, index_col='date', parse_dates=True)

                    # Align the columns
                    combined_df = pd.concat([existing_df, df])
                else:
                    combined_df = df

                # Write the merged data to CSV
                combined_df.to_csv(self.output_file, mode='w', header=True)


        if self.results_show['database']==True:
            today_date = pd.Timestamp.now().normalize()

            # Change the date component to today's date, but keep the time component
            df.index = df.index.map(
                lambda dt: pd.Timestamp(year=today_date.year, month=today_date.month, day=today_date.day-1, hour=dt.hour,
                                        minute=dt.minute, second=dt.second))

            df.reset_index(inplace=True)
            df.to_sql(attr, self.conn, if_exists='append', index=False)
            self.conn.commit()
        if self.results_show.get('mqtt', False):
            msg = df.to_json()
            self.mqtt_client.publish(self.mqtt_topic, msg)

        return time + 1 # TODO change +1 to +self.time_resolution do it's not hard coded

    def finalize(self) -> None:
        """
        Prints collected data
        """
        if self.print_results:
            print('Collected data:')
            for sim, sim_data in sorted(self.data.items()):
                print('- %s:' % sim)
                for attr, values in sorted(sim_data.items()):
                    print('  - %s: %s' % (attr, values))

        if self.results_show['database']==True:
            self.conn.close()


if __name__ == '__main__':
    mosaik_api.start_simulation(Collector())