"""
This module implements the mosaik sim API for `Pandapower.

Two options exist to run a power flow:

1. Time series power flow calculation with internal time propagation happens
   through the grid files.
2. Static power flow calculation that could be propagated in time through
   other simulators connected via mosaik.
"""

import logging
import mosaik_api
import arrow

try:
    import Models.EleDisNetworkSim.model as model
except ModuleNotFoundError:
    import EleDisNetworkSim.model as model
else:
    import Models.EleDisNetworkSim.model as model

from Models.EleDisNetworkSim.model import make_eid


logger = logging.getLogger('pandapower.mosaik')

meta = {
    'type': 'hybrid',
    'models': {
        'Grid': {
            'public': True,
            'params': [
                'gridfile',  # Name of the file containing the grid topology.
                'sheetnames',  # Mapping of Excel sheet names, optional.
                'sim_start',  # Starting time of the simulation.
            ],
            'attrs': [],
        },
        'Ext_grid': {
            'public': False,
            'params': [],
            'attrs': [
                'p_mw',   # active power [MW]
                'q_mvar',   # reactive power [MVAr]
            ],

        },
        'Bus': {
            'public': False,
            'params': [],
            'attrs': [
                'p_mw',   # active power [MW]
                'q_mvar',   # reactive power [MVAr]
                'vn_kv',  # Nominal bus voltage [KV]
                'vm_pu',  # Voltage magnitude [p.u]
                'va_degree',  # Voltage angle [deg]
            ],
        },
        'Load': {
            'public': False,
            'params': [],
            'attrs': [
                'p_mw',   # active power [MW]
                'q_mvar',   # reactive power [MVAr]
                'in_service',  # Specifies if the load is in service.
                'controllable',  # States if load is controllable or not.
            ],
        },
        'Sgen': {
            'public': False,
            'params': [],
            'attrs': [
                'p_mw',   # active power [MW]
                'q_mvar',   # reactive power [MVAr]
                'in_service',  # Specifies if the load is in service.
                'controllable',  # States if load is controllable or not.
                'va_degree',  # Voltage angle [deg]
            ],
        },
        'Trafo': {
            'public': False,
            'params': [],
            'attrs': [
                'p_hv_mw',    # Active power at "from" side [MW]
                'q_hv_mvar',    # Reactive power at "from" side [MVAr]
                'p_lv_mw',      # Active power at "to" side [MW]
                'q_lv_mvar',      # Reactive power at "to" side [MVAr]
                'sn_mva',       # Rated apparent power [MVA]
                'max_loading_percent',   # Maximum Loading
                'vn_hv_kv',       # Nominal primary voltage [kV]
                'vn_lv_kv',       # Nominal secondary voltage [kV]
                'pl_mw',       # Active power loss [MW]
                'ql_mvar',       # reactive power consumption of the trafo [Mvar]
                #'pfe_kw',       #  iron losses in kW [kW]
                #'i0_percent',       #  iron losses in kW [kW]
                'loading_percent',       # load utilization relative to rated power [%
                'i_hv_ka',       # current at the high voltage side of the trafo [kA]
                'i_lv_ka',       # current at the low voltage side of the trafo [kA]
                'tap_max',      # maximum possible tap turns
                'tap_min',      # minimum possible tap turns
                'tap_pos',  # Currently active tap turn
            ],
        },
        'Line': {
            'public': False,
            'params': [],
            'attrs': [
                'p_from_mw',    # Active power at "from" side [MW]
                'q_from_mvar',    # Reactive power at "from" side [MVAr]
                'p_to_mw',      # Active power at "to" side [MW]
                'q_to_mvar',      # Reactive power at "to" side [MVAr]
                'max_i_ka',     # Maximum current [KA]
                'length_km',    # Line length [km]
                'pl_mw',    # active power losses of the line [MW]
                'ql_mvar',    # reactive power consumption of the line [MVar]
                'i_from_ka',    # Current at from bus [kA]
                'i_to_ka',    # Current at to bus [kA]
                'loading_percent',   # line loading [%]
                'r_ohm_per_km',  # Resistance per unit length [Ω/km]
                'x_ohm_per_km',  # Reactance per unit length [Ω/km]
                'c_nf_per_km',   # Capacity per unit length [nF/km]
                'in_service',    # Boolean flag (True|False)
            ],
        },
        
        'Storage': {
            'public': False,
            'params': [],
            'attrs': [
                'p_mw',         # active power [MW]
                'max_e_mwh'     # maximum energy content of the storage [MWh]
                'q_mvar',       # reactive power [MVAr]
                'soc_percent'   # state of charge of the storage
                'in_service',   # specifies if the load is in service.
                'controllable', # States if the storage unit is controllable or not.

            ],
        },
        
    },
}


class Pandapower(mosaik_api.Simulator):
    def __init__(self):
        super(Pandapower, self).__init__(meta)
        self.step_size = None
        self.simulator = model.pandapower()
        self.start_time_Profiles = None
        self.end_time_Profiles = None
        self.sim_start = None
        self.delta_of_simulation_start = None
        self.time_step_index = 0
        #
        #There are three elements that have power values based on the generator
        #  viewpoint (positive active power means power consumption), which are:
        #gen, sgen, ext_grid
        #For all other bus elements the signing is based on the consumer viewpoint
        # (positive active power means power consumption):bus, load

        self._entities = {}
        self._relations = []  # List of pair-wise related entities (IDs)
        self._ppcs = []  # The pandapower cases
        self._cache = {}  # Cache for load flow outputs

    def init(self, sid, time_resolution, step_size, trigger=False, mode='pf'):
        #TODO: check if we need to implement signs for loads/generators
        if step_size is not None:
            logger.debug("Power flow will be computed every %d seconds." %
                         (step_size*time_resolution))
        else:
            logger.debug("Pandapower is only stepped when triggered by other "
                         "simulators' input")
        if trigger or step_size is None:
            # Add trigger for all attributes of all models:
            for imodel in self.meta['models']:
                self.meta['models'][imodel]['trigger'] = True
        #signs = ('positive', 'negative')
        #logger.debug('Loads will be %s numbers, feed-in %s numbers.' %
         #            signs if pos_loads else tuple(reversed(signs)))

        self.step_size = step_size
        self.mode = mode

        return self.meta

    def create(self, num, modelname, gridfile, sim_start=None):
        if sim_start != None:
            self.sim_start = arrow.get(sim_start,'YYYY-MM-DD HH:mm:ss')
        if modelname != 'Grid':
            raise ValueError('Unknown model: "%s"' % modelname)

        grids = []
        for i in range(num):
            grid_idx = len(self._ppcs)
            ppc, entities = self.simulator.load_case(gridfile,grid_idx)
            self._ppcs.append(ppc)

            if self.sim_start is not None:
                time_profiles = ppc.profiles['load']['time']
                start_time_profiles = arrow.get(time_profiles[0], 'DD.MM.YYYY HH:mm')
                end_time_profiles = arrow.get(time_profiles[len(time_profiles) - 1], 'DD.MM.YYYY HH:mm')
                if self.sim_start == start_time_profiles:
                    print('Simulation start and start of load profiles in pandapower is equal.')
                elif self.sim_start > start_time_profiles:
                    if self.sim_start < end_time_profiles:
                        print(
                            'The simulation starts later than the profiles of pandapower start (sim_start < end_time_Profiles)')
                        self.delta_of_simulation_start = self.sim_start - start_time_profiles
                        delta_seconds = (self.delta_of_simulation_start.days * 24 * 60 * 60) + \
                                        self.delta_of_simulation_start.seconds
                        self.time_step_index = int(delta_seconds / self.step_size)
                    else:
                        print('The simulation start is outside the time horizon of the load profiles of pandapower')
                else:
                    print('The simulation start is ealier than the load profiles in pandapower start')

            children = []
            for eid, attrs in sorted(entities.items()):
                assert eid not in self._entities
                self._entities[eid] = attrs

                # We'll only add relations from line to nodes (and not from
                # nodes to lines) because this is sufficient for mosaik to
                # build the entity graph.
                relations = []
                if attrs['etype'] in ['Trafo', 'Line','Load','Sgen', 'Storage']:
                    relations = attrs['related']

                children.append({
                    'eid': eid,
                    'type': attrs['etype'],
                    'rel': relations,
                })

            grids.append({
                'eid': make_eid('grid', grid_idx),
                'type': 'Grid',
                'rel': [],
                'children': children,
            })

        return grids

    def setup_done(self):
        inv_load_id = {v: k for k, v in self.simulator.load_id.items()}
        inv_gen_id = {v: k for k, v in self.simulator.sgen_id.items()}

        related_entities = yield self.mosaik.get_related_entities()
        for edge in related_entities['edges']:
            idx = None
            name = None
            if 'ext_load' in edge[0] or 'ext_load' in edge[1]:
                if 'ext_load' in edge[0] and edge[1].split('-')[-1] not in edge[0]:
                    name = edge[0].split('-')[-2:-1][0] + '-' + edge[0].split('-')[-1:][0]
                elif 'ext_load' in edge[1] and edge[0].split('-')[-1] not in edge[1]:
                    name = edge[1].split('-')[-2:-1][0] + '-' + edge[1].split('-')[-1:][0]
                if name:
                    idx = inv_load_id[name]
            elif 'ext_gen' in edge[0] or 'ext_gen' in edge[1]:
                if 'ext_gen' in edge[0] and edge[1].split('-')[-1] not in edge[0]:
                    name = edge[0].split('-')[-2:-1][0] + '-' + edge[0].split('-')[-1:][0]
                elif 'ext_gen' in edge[1] and edge[0].split('-')[-1] not in edge[1]:
                    name = edge[1].split('-')[-2:-1][0] + '-' + edge[1].split('-')[-1:][0]
                if name:
                    idx = inv_gen_id[name]
            if idx:
                self.simulator.net.sgen.in_service.at[idx] = True


    def step(self, time, inputs, max_advance):
        for eid, attrs in inputs.items():
            idx = self._entities[eid]['idx']
            etype = self._entities[eid]['etype']
            static = self._entities[eid]['static']
            for name, values in attrs.items():
                if name=='in_service' or name=='controllable':
                    attrs[name] = values.values()[0]
                else:
                    attrs[name] = sum(float(v) for v in values.values())

            self.simulator.set_inputs(etype, idx, attrs, static,)

        # TODO: Why is `powerflow_timeseries` not done if there's input?
        if self.mode == 'pf_timeseries' and not bool(inputs):
            self.simulator.powerflow_timeseries(self.time_step_index)
        elif self.mode == 'pf':
            self.simulator.powerflow()

        self._cache = self.simulator.get_cache_entries()

        self.time_step_index += 1

        if self.step_size:
            next_step = time + self.step_size
        else:
            next_step = None
        return next_step

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            for attr in attrs:
                try:
                    val = self._cache[eid][attr]
                except KeyError:
                    val = self._entities[eid]['static'][attr]
                data.setdefault(eid, {})[attr] = val

        return data


def main():
    mosaik_api.start_simulation(Pandapower(), 'The mosaik-Pandapower adapter')
    
if __name__ == "__main__":
    main()
