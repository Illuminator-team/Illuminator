from __future__ import annotations

from mosaik_api.datetime import Converter
import mosaik_api
import numpy as np
import influxdb_client as influx
import os


META = {
    "type": "time-based",
    "models": {
        "Database": {
            "public": True,
            "any_inputs": True,
            "params": [
                "url",  # the URL (including port) to Influx
                "token",  # the access token for the Influx database
                "org",  # the organization name inside Influx
                "bucket",  # the bucket to store the data in
                "measurement",  # the measurement under which to store the data
            ],
            "attrs": ["local_time"],
        },
    },
}


EID = "Database"


class Simulator(mosaik_api.Simulator):
    """A mosaik data collector using an Influx database.

    This mosaik simulator is able to take any number of inputs from
    mosaik and stores them in an Influx database.

    The simulator expects to receive the simulation-internal time (as a ISO time
    string) on the `local_time` attribute and saves the data at the corresponding
    time in the database. Alternatively, a `start_date` can be provided which
    will be combined with the `step` and `time_resolution`.

    This simulator will run as a `time-based` simulator when given a
    `step_size`, otherwise it will be `event-based`.
    """

    _eid: str
    _bucket: str
    _measurement: str
    _influx_writer: influx.WriteApi
    _step_size: int | None
    """If _step_size is None, the simulator is running in event-based mode."""
    _time_converter: Converter | None
    """If _time_converter is None, a time needs to be explicitly set in step's input."""

    def __init__(self):
        super().__init__(META)
        self._influx_writer = None  # type: ignore  # will be set in `create`
        self._time_converter = None
        self._step_size = None

    def init(self, sid, time_resolution, start_date=None, step_size=900):
        if step_size is not None:
            self._step_size = step_size
        else:
            self.meta["type"] = "event-based"

        if start_date:
            self._time_converter = Converter(
                start_date=start_date,
                time_resolution=time_resolution,
            )

        return self.meta

    def create(self, num, model, **model_params):
        errmsg = (
            "The Influx store simulator only supports one entity. Create a second "
            "instance of the simulator if you need more."
        )
        assert self._influx_writer is None, errmsg
        assert num == 1, errmsg

        url = model_params["url"]
        org = model_params["org"]
        token = model_params.get("token", os.environ.get("INFLUX_TOKEN", None))
        self._bucket = model_params["bucket"]
        self._measurement = model_params["measurement"]

        self._influx_writer = influx.InfluxDBClient(
            url=url, token=token, org=org
        ).write_api()  # default write mode is "batching"

        return [{"eid": EID, "type": model}]

    def step(self, time, inputs, max_advance):
        data = inputs.get(EID, {})
        if "local_time" in data:
            timestamp = next(iter(data["local_time"].values()))
        elif self._time_converter:
            timestamp = self._time_converter.isoformat_from_step(time)
        else:
            raise ValueError(
                "The Influx simulator needs to be supplied with an ISO timestamp on "
                "`local_time` attribute at each step so it can store data in the "
                "Influx database. (If you're using MIDAS to run your simulation, "
                "you can simply add the `timesim` simulator.) "
                "Alternatively, you can provide a `start_date` when initializing the "
                "simulator."
            )

        for attr, src_ids in data.items():
            for src_id, val in src_ids.items():
                if isinstance(val, np.generic):
                    # Influx cannot handle numpy datatypes, so transform them into
                    # standard Python types.
                    val = val.item()
                src_sim, src_entity = src_id.split(".")
                record = (
                    influx.Point(self._measurement)
                    .tag("src_sim", src_sim)
                    .tag("src_entity", src_entity)
                    .field(attr, val)
                    .time(timestamp)
                )
                self._influx_writer.write(
                    bucket=self._bucket,
                    record=record,
                )

        # Only return a next step if running in time-based mode
        if self._step_size:
            return time + self._step_size

    def get_data(self, outputs):
        return {}

    def finalize(self):
        self._influx_writer.close()


if __name__ == "__main__":
    mosaik_api.start_simulation(Simulator())
