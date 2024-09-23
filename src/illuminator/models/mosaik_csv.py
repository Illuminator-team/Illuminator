import arrow

import mosaik_api


__version__ = '1.2.0'


class CSV(mosaik_api.Simulator):
    def __init__(self):
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

    def init(self, sid, time_resolution, sim_start, datafile, date_format='YYYY-MM-DD HH:mm:ss',
             delimiter=','):
        self.time_resolution = float(time_resolution)
        self.delimiter = delimiter
        self.date_format = date_format
        self.start_date = arrow.get(sim_start, self.date_format)
        self.next_date = self.start_date

        self.datafile = open(datafile)
        self.modelname = next(self.datafile).strip()

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

    def create(self, num, model):
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

    def step(self, time, inputs, max_advance):
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

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            if eid not in self.eids:
                raise ValueError('Unknown entity ID "%s"' % eid)

            data[eid] = {}
            for attr in attrs:
                data[eid][attr] = self.cache[attr]

        return data

    def _read_next_row(self):
        try:
            self.next_row = next(self.datafile).strip().split(self.delimiter)
            self.next_row[0] = arrow.get(self.next_row[0], self.date_format)
        except StopIteration:
            self.next_row = None

    def finalize(self):
        self.datafile.close()


def main():
    return mosaik_api.start_simulation(CSV(), 'mosaik-csv simulator')


if __name__ == "__main__":
    main()
