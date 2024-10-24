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

    def __init__(self) -> None:
        """
        Inherits the Mosaik API Simulator class and is used for python based simulations.
        For more information properly inheriting the Mosaik API Simulator class please read their given documentation.

        ...

        Attributes
        ----------
        self._influx_writer : ???
            ???
        self._time_converter : ???
            ???
        self._step_size : : ???
            ???
        """
        super().__init__(META)
        self._influx_writer = None  # type: ignore  # will be set in `create`
        self._time_converter = None
        self._step_size = None

    def init(self, sid:str, time_resolution:float, start_date=None, step_size:int=900) -> dict:
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
        step_size : int
            The size of the time step. The unit is arbitrary, but it has to be consistent among all simulators used in a simulation.

        Returns
        -------
        self.meta : dict
            The metadata of the class
        """
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

    def create(self, num:int, model:str, **model_params) -> list:
        """
        Create `num` instances of `model` using the provided `model_params`.

        ...

        Parameters
        ----------
        num : int
            The number of model instances to create.
        model : str
            `model` needs to be a public entry in the simulator's ``meta['models']``.
        **model_params : dict 
            A mapping of parameters (from``meta['models'][model]['params']``) to their values.
        
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
        """
        Returns empty dictionary object

        Parameters
        ----------
        outputs : dict
            Unused
        
        Returns
        -------
        dict
            Empty dictionary
        """
        return {}

    def finalize(self):
        """
        Runs the `close()` method
        """
        self._influx_writer.close()


if __name__ == "__main__":
    mosaik_api.start_simulation(Simulator())
