import collections
import pandas as pd
import mosaik_api
META = {
    'type': 'event-based',
    'models': {
        'Monitor': {
            'public': True,
            'any_inputs': True,
            'params': [],
            'attrs': [],
        },
    },
}
import wandb
class Collector(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid = None
        self.data = collections.defaultdict(lambda: collections.defaultdict(dict))

    def init(self, sid, time_resolution, start_date, results_show,
             date_format='%Y-%m-%d %H:%M:%S', output_file='output/results.csv',
             print_results=False):
        self.time_resolution = time_resolution
        self.start_date = pd.to_datetime(start_date, format=date_format)
        self.output_file = output_file
        self.print_results = print_results
        self.results_show=results_show
        return self.meta

    def create(self, num, model):
        print('Collector create: hi')
        if num > 1 or self.eid is not None:
            raise RuntimeError('Can only create one instance of Monitor.')

        self.eid = 'Monitor'
        print('Collector create: bye')
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
        #wandb.log({"time": time})
        #wandb.log({"data": df['Wind-0.wind_0-wind_gen'][0]})
        if self.results_show['write2csv']==True:
            if time == 0:
                df.to_csv(self.output_file, mode='w', header=True)
            else:
                df.to_csv(self.output_file, mode='a', header=False)

        return None

    def finalize(self):
        if self.print_results:
            print('Collected data:')
            for sim, sim_data in sorted(self.data.items()):
                print('- %s:' % sim)
                for attr, values in sorted(sim_data.items()):
                    print('  - %s: %s' % (attr, values))


if __name__ == '__main__':
    mosaik_api.start_simulation(Collector())
