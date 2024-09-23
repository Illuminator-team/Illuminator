"""
Store mosaik simulation data in an sql.

"""
import datetime
import mysql.connector
import mosaik_api

__version__ = '0.1'
meta = {
    'models': {
        'mosaik_sql': {
            'public': True,
            'any_inputs': True,
            'params': ['hostname', 'username', 'password', 'database', 'scenario', 'create'],
            'attrs': [],
        }
    },
}


class SQL(mosaik_api.Simulator):
    count = 0

    def __init__(self):
        super().__init__(meta)
        self.eid = 'mosaik_sql'
        self.index = 0

        # Set in init()
        self.sid = None
        self.step_size = None
        self.duration = None
        self.hostname = None
        self.username = None
        self.password = None
        self.database = None
        self.create_tables = None  # What type of new database schema should be created?
        self.table_name = None
        self.buf_size = None

        # Set in create()
        self._cur = None
        self._my_connection = None
        self.datetime_object = None

        # Used in step()
        self._query_buf = {}
        self._insert_queries = {}

    def init(self, sid, step_size, sim_start, hostname, username, password, database, create_tables=None,
             table_name=None, buf_size=0):
        '''

        :param sid:
        :param step_size:
        :param sim_start:
        :param hostname:
        :param username:
        :param password:
        :param database:
        :param create_tables: Defines which database schema will be created to store the results. 'single' means
        one table for all values. 'multi' means multiple tables are created. For each entity one.
        :param table_name: If create_tables is 'single' this defines the name of this table.
        :param buf_size: Size of the buffer storing data until it is written to database
        :return:
        '''
        self.sid = sid
        self.step_size = step_size
        self.datetime_object = datetime.datetime.strptime(sim_start, '%Y-%m-%d %H:%M:%S')  # needed to upload timestamp
        self.hostname = hostname
        self.username = username
        self.password = password
        self.database = database
        self.create_tables = create_tables
        self.table_name = table_name
        self.buf_size = buf_size

        return self.meta

    def create(self, num, modelname):
        model_list = []
        for i in range(num):
            model_list.append({
                'eid': "mosaik_sql_" + str(i),
                'type': "mosaik_sql",
                'rel': [],
                'children': []
            })
        self._my_connection = mysql.connector.connect(host=self.hostname,
                                                      user=self.username,
                                                      passwd=self.password,
                                                      db=self.database)
        self._cur = self._my_connection.cursor()
        print('initialized sql_db')

        return model_list

    def setup_done(self):
        print('setup done')

    def step(self, time, inputs):
        timestamp = self.datetime_object + datetime.timedelta(seconds=time)

        attr_dict = {}
        for sink_id, data in inputs.items():
            for attr, data2 in data.items():
                for src_id, value in data2.items():
                    if src_id not in attr_dict:
                        attr_dict[src_id] = []
                    attr_dict[src_id].append((attr, value))
        if time == 0 and self.create_tables:
            self.create_database(attr_dict)

        self.insert_values(attr_dict, timestamp)
        # self.insert_meo(timestamp, inputs)

        return time + self.step_size

    def create_database(self, attr_dict):
        if self.create_tables == 'multi':
            for src_id in attr_dict:
                query_drop_if_exists = "DROP TABLE IF EXISTS `" + src_id + "`;"
                # print(query_drop_if_exists)
                self._cur.execute(query_drop_if_exists)

                query_start = "CREATE TABLE `" + src_id + "` (ts DATETIME PRIMARY KEY, "
                query_attr = ""
                query_end = ");"
                attr_list = ['ts']
                for attr, value in attr_dict[src_id]:
                    attr_list.append(attr)
                    if isinstance(value, int):
                        query_attr = query_attr + "`" + attr + "` INT,"
                    if isinstance(value, float):
                        query_attr = query_attr + "`" + attr + "` DOUBLE,"
                    else:
                        query_attr = query_attr + "`" + attr + "` VARCHAR(64)"
                query_attr = query_attr[0: (len(query_attr) - 1)]
                query = query_start + query_attr + query_end
                # print(query)
                self._cur.execute(query)

                self._query_buf[src_id] = []
                attr_list_string = str(attr_list)[1:-1].replace('\'', '')
                placeholder_string = str(['%s' for x in attr_list])[1:-1].replace('\'', '')
                self._insert_queries[src_id] = "INSERT INTO `" + src_id + "` (" + attr_list_string + ") VALUES (" + \
                                                placeholder_string + ")"
        elif self.create_tables == 'single':
            if self.table_name is None:
                print('Table name for single table was not defined. Use MosaikSimulation as table name')
                self.table_name = 'MosaikSimulation'
            query_drop_if_exists = "DROP TABLE IF EXISTS `" + self.table_name + "`;"
            # print(query_drop_if_exists)
            self._cur.execute(query_drop_if_exists)

            query = "CREATE TABLE `" + self.table_name + \
                    "` (id INT PRIMARY KEY, ts DATETIME, src VARCHAR(32), valueName VARCHAR(32), value VARCHAR(32));"
            print(query)
            self._cur.execute(query)
            self._query_buf[self.table_name] = []
            self._insert_queries[self.table_name] = "INSERT INTO `" + self.table_name + \
                                                    "` (id, ts, src, valueName, value ) VALUES (" + \
                                                    "%s,%s,%s,%s,%s)"


    def insert_values(self, attr_dict, timestamp):
        if self.create_tables == 'multi':
            for src_id in attr_dict:
                attr_list = [str(timestamp)]
                for attr, value in attr_dict[src_id]:
                    if value.__class__.__name__.lower() == 'float64':
                        value = float(value)
                    attr_list.append(value)
                self._query_buf[src_id].append(tuple(attr_list))
                # self._cur.executemany(self._insert_queries[src_id], data)

            if self.buf_size == 0 or 0 < self.buf_size < len(self._query_buf):
                self.execute_insert()
        elif self.create_tables == 'single':
            for src_id in attr_dict:
                for attr, value in attr_dict[src_id]:
                    self._query_buf[self.table_name].append((self.index, str(timestamp), str(src_id), str(attr), str(value)))
                    self.index += 1
            if self.buf_size == 0 or 0 < self.buf_size < len(self._query_buf):
                self._cur.executemany(self._insert_queries[self.table_name], self._query_buf[self.table_name])
                self._my_connection.commit()
                self._query_buf[self.table_name] = []

    def execute_insert(self):
        print('execute query')
        for src_id in self._query_buf.keys():
            self._cur.executemany(self._insert_queries[src_id], self._query_buf[src_id])
            self._my_connection.commit()
            self._query_buf[src_id] = []

    def finalize(self):
        if self.buf_size > 0:
            if len(self._query_buf) > 0:
                print('finalize with not empty buffer')
                self.execute_insert()

        self._my_connection.close()


def main():
    mosaik_api.start_simulation(SQL(), 'The mosaik-SQL adapter')


if __name__ == "__main__":
    main()
