import collections
import pandas as pd
import mosaik_api
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
    def __init__(self):
        super().__init__(META)
        self.eid = None
        self.data = collections.defaultdict(lambda: collections.defaultdict(dict))

    def init(self, sid, time_resolution, start_date, results_show,output_file,
             date_format='%Y-%m-%d %H:%M:%S',
             db_file='Result/result.db',
             mqtt_broker='mqtt://192.168.10.90:1883', mqtt_topic='TGVFCBB75',
             print_results=False):
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

    def create(self, num, model):
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

    def step(self, time, inputs, max_advance):
        # print(inputs)
        current_date = (self.start_date
                        + pd.Timedelta(time * self.time_resolution, unit='seconds'))

        df_dict = {'date': current_date}

        data = inputs.get(self.eid, {})
        for attr, values in data.items():
            for src, value in values.items():
                self.data[src][attr][time] = value
                df_dict[f'{src}-{attr}'] = [value]

        df = pd.DataFrame.from_dict(df_dict)
        df = df.set_index('date')

        if self.results_show['dashboard_show']==True:
            for key, value in df.items():
                wandb.log({key: value[0],
                           "custom_step":time/900})

        if self.results_show['write2csv'] == True:
            if time == 0:
                # Overwrite the CSV file at the first time step
                df.to_csv(self.output_file, mode='w', header=True)
            else:
                if os.path.exists(self.output_file):
                    # Read existing CSV
                    existing_df = pd.read_csv(self.output_file, index_col='date', parse_dates=True)

                    # Align the columns
                    combined_df = existing_df.append(df)

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

        return time + 900

    def finalize(self):
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