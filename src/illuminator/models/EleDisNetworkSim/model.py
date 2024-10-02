"""
This module is Pandapower model for Mosaik Sim API. Grid import could happen through Json or Excel files, and the file
should exist in the working directory.
>>>> load_case(path to the file.json) or (path to the file.xlsx)

In pandapower library there exist a list of standard grids that could be directly imported and simulated:
https://pandapower.readthedocs.io/en/v2.1.0/networks.html

The following list of grid clusters that could be simulated by this model are:
Simbench >>>> load_case(name of the simbench grid)

Cigre networks >>>> load_case(cigre_(voltage level: hv,mv,lv))
Cigre network with DER >>>> load_case (cigre_mv_all) or load_case (cigre_mv_pv_wind)

Power system cases >>>> These networks exist as Json files in ~/pandapower/networks/power_system_test_case_jsons
these files should be copied in the working directory and imported as json file

"""

import json
import math
import os.path

import pandas as pd
import pandapower as pp
from pandapower.timeseries import DFData
from pandapower.timeseries import OutputWriter
from pandapower.control import ConstControl
from pandapower.timeseries.run_time_series import run_timeseries, run_time_step, init_time_series
import pandapower.networks as ppn
import Models.EleDisNetworkSim.network as network
OUTPUT_ATTRS = {
    'Bus': ['p_mw', 'q_mvar', 'vm_pu', 'va_degree'],
    'Load': ['p_mw', 'q_mvar'],
    'Sgen': ['p_mw', 'q_mvar'],
    'Trafo': ['va_lv_degree', 'loading_percent'],
    'Line': ['i_ka', 'loading_percent'],
    'Ext_grid': ['p_mw', 'q_mvar'],
    'Storage': ['p_mw', 'q_mvar'],
}


class pandapower(object):

    def __init__(self):
        self.entity_map = {}

    def load_case(self, path, grid_idx):
        """
        Loads a pandapower network, the network should be ready in a separate json or excel file or as stated above
        TODO: pypower converter and network building with only parameter as input
        """
        loaders = {
            '.json': 1,
            '.xlsx': 2,
            '': 3
        }
        try:
            ext = os.path.splitext(path)[-1]
            loader = loaders[ext]
        except KeyError:
            raise ValueError("Don't know how to open '%s'" % path)

        if loader == 1:
            self.net = pp.from_json(path)
        elif loader == 2:
            self.net = pp.from_excel(path)
        else:
            if path == 'cigre_hv':
                self.net = ppn.create_cigre_network_hv()
            elif path == 'cigre_mv':
                self.net = ppn.create_cigre_network_mv(with_der=False)
            elif path == 'cigre_mv_all':
                self.net = ppn.create_cigre_network_mv(with_der='all')
            elif path == 'cigre_mv_pv_wind':
                self.net = ppn.create_cigre_network_mv(with_der='pv_wind')
            elif path == 'cigre_lv':
                self.net = ppn.create_cigre_network_lv()
            elif path == 'cigre_lv_resident':
                self.net=network.create_cigre_lv_resident()
            else:
                try:
                    import simbench as sb
                    self.net = sb.get_simbench_net(path)
                except:
                    raise ImportError('Loading of simbench grid was not possible. If you want to use a simbench grid, you have to install simbench with "pip install simbench".')

        self.bus_id = self.net.bus.name.to_dict()

        #create virtual loads and gens on each bus ready to be plugged in
        # This is not functional and is creating false loads
        #=======================================================================
        for i in self.bus_id:
            if self.net.ext_grid.bus[0] != i:
                pp.create_load(self.net, i, p_mw=0, name=('ext_load_at_bus-%s' % self.net.bus.name[i]), in_service=False)
                pp.create_sgen(self.net, i, p_mw=0, name=('ext_gen_at_bus-%s' % self.net.bus.name[i]), in_service=False)
        #=======================================================================

        # create elements indices, to create entities
        self.load_id = self.net.load.name.to_dict()
        self.sgen_id = self.net.sgen.name.to_dict()
        self.line_id = self.net.line.name.to_dict()
        self.trafo_id = self.net.trafo.name.to_dict()
        self.switch_id = self.net.switch.name.to_dict()
        self.storage_id = self.net.storage.name.to_dict()

        # load the entity map
        self._get_slack(grid_idx)
        self._get_buses(grid_idx)
        self._get_lines(grid_idx)
        self._get_trafos(grid_idx)
        self._get_loads(grid_idx)
        self._get_sgen(grid_idx)
        self._get_storage(grid_idx)



        entity_map = self.entity_map
        ppc = self.net  # pandapower case

        if 'profiles' in self.net:
            time_steps = range(0, len(self.net.profiles['load']))
            output_dir = os.path.join(os.getcwd(), "time_series_example")
            ow = create_output_writer(self.net, time_steps,
                                      output_dir)  # just created to update res_bus in each time step
            self.ts_variables = init_time_series(self.net, time_steps)
        else:
            pass

        return ppc, entity_map

    def _get_slack(self, grid_idx):
        """Create entity of the slack bus"""

        self.slack_bus_idx = self.net.ext_grid.bus[0]
        bid = self.bus_id[self.slack_bus_idx]
        eid = make_eid(bid, grid_idx)

        self.entity_map[eid] = {
            'etype': 'Ext_grid',
            'idx': self.slack_bus_idx,
            'static': {'vm_pu': self.net.ext_grid['vm_pu'],
                       'va_degree': self.net.ext_grid['va_degree']
                       }
        }
        slack = (0, self.slack_bus_idx)

        return slack

    def _get_buses(self, grid_idx):
        """Create entities of the buses"""
        buses = []

        for idx in self.bus_id:
            if self.slack_bus_idx != idx:
                element = self.net.bus.iloc[idx]
                bid = element['name']
                eid = make_eid(bid, grid_idx)
                buses.append((idx, element['vn_kv']))
                self.entity_map[eid] = {
                    'etype': 'Bus',
                    'idx': idx,
                    'static': {
                        'vn_kv': element['vn_kv']
                    },
                }
            else:
                pass

        return buses

    def _get_loads(self, grid_idx):
        """Create load entities"""
        loads = []

        for idx in self.load_id:
            element = self.net.load.iloc[idx]
            eid = make_eid(element['name'], grid_idx)
            bid = make_eid(self.bus_id[element['bus']], grid_idx)

            element_data = element.to_dict()
            keys_to_del = ['name', 'const_z_percent', 'const_i_percent', 'min_q_mvar', 'min_p_mw', 'max_q_mvar',
                           'max_p_mw']
            element_data_static = {key: element_data[key] for key in element_data if key not in keys_to_del}

            # time series calculation
            if 'profile' in element_data_static:
                if type(element_data_static['profile']) != float:
                    profile_name = element_data_static['profile']

                    datasource = pd.DataFrame()
                    datasource[profile_name + '_pload'] = self.net.profiles['load'][profile_name + '_pload'] * \
                                                          element['p_mw']
                    datasource[profile_name + '_qload'] = self.net.profiles['load'][profile_name + '_qload'] * \
                                                          element['q_mvar']

                    ds = DFData(datasource)

                    ConstControl(self.net, element='load', variable='p_mw', element_index=idx,
                                 data_source=ds, profile_name=profile_name + '_pload')

                    ConstControl(self.net, element='load', variable='q_mvar', element_index=idx,
                                 data_source=ds, profile_name=profile_name + '_qload')
            self.entity_map[eid] = {'etype': 'Load', 'idx': idx, 'static': element_data_static, 'related': [bid]}

            loads.append((bid, element['p_mw'], element['q_mvar'], element['scaling'], element['in_service']))

        return loads

    def _get_storage(self, grid_idx):
        """
        Create storage entities
        :param grid_idx: int with the grid ID
        """
        storages = []

        for idx in self.storage_id:
            
            # TODO check the correct indexing
            element = self.net.storage.iloc[idx]
            eid = make_eid(element['name'], grid_idx)
            bid = make_eid(self.bus_id[element['bus']], grid_idx)

            element_data = element.to_dict()
            keys_to_del = ['name', 'min_q_mvar',
                           'min_p_mw', 'max_q_mvar', 'max_p_mw']
            element_data_static = {
                key: element_data[key] for key in element_data if key not in keys_to_del}

            # time series calculation
            if 'profile' in element_data_static:
                if type(element_data_static['profile']) != float:
                    profile_name = element_data_static['profile']

                    datasource = pd.DataFrame()
                    datasource[profile_name + '_pload'] = self.net.profiles['storage'][profile_name +
                                                                                       '_psto'] * element['p_mw']

                    ds = DFData(datasource)

                    ConstControl(
                        self.net,
                        element='storage',
                        variable='p_mw',
                        element_index=idx,
                        data_source=ds,
                        profile_name=profile_name +
                        '_psto')

            self.entity_map[eid] = {
                'etype': 'Storage',
                'idx': idx,
                'static': element_data_static,
                'related': [bid]}

            storages.append((
                bid,
                element['p_mw'],
                element['q_mvar'],
                element['scaling'],
                element['in_service'],
                element['soc_percent']
            ))

        return storages



    def _get_sgen(self, grid_idx):
        """Create static generator entities"""
        sgens = []

        for idx in self.sgen_id:
            element = self.net.sgen.iloc[idx]
            eid = make_eid(element['name'], grid_idx)
            bid = make_eid(self.bus_id[element['bus']], grid_idx)

            element_data = element.to_dict()
            keys_to_del = ['name', 'min_q_mvar', 'min_p_mw', 'max_q_mvar', 'max_p_mw']
            element_data_static = {key: element_data[key] for key in element_data if key not in keys_to_del}

            # time series calculation
            if 'profile' in element_data_static:
                if type(element_data_static['profile']) != float:
                    profile_name = element_data_static['profile']

                    datasource = pd.DataFrame()
                    datasource[profile_name] = self.net.profiles['renewables'][profile_name] * element['p_mw']

                    ds = DFData(datasource)

                    ConstControl(self.net, element='sgen', variable='p_mw', element_index=idx,
                                 data_source=ds, profile_name=profile_name)

            self.entity_map[eid] = {'etype': 'Sgen', 'idx': idx, 'static': element_data_static, 'related': [bid]}

            sgens.append((bid, element['p_mw'], element['q_mvar'], element['scaling'], element['in_service']))

        return sgens

    def _get_lines(self, grid_idx):
        """create branches entities"""
        lines = []

        for idx in self.line_id:
            element = self.net.line.iloc[idx]
            eid = make_eid(element['name'], grid_idx)
            fbus = make_eid(self.bus_id[element['from_bus']], grid_idx)
            tbus = make_eid(self.bus_id[element['to_bus']], grid_idx)

            f_idx = self.entity_map[fbus]['idx']
            t_idx = self.entity_map[tbus]['idx']

            element_data = element.to_dict()
            keys_to_del = ['name', 'from_bus', 'to_bus']
            element_data_static = {key: element_data[key] for key in element_data if key not in keys_to_del}
            # del element_data_static

            self.entity_map[eid] = {'etype': 'Line', 'idx': idx, 'static': element_data_static,
                                    'related': [fbus, tbus]}

            lines.append((f_idx, t_idx, element['length_km'], element['r_ohm_per_km'], element['x_ohm_per_km'],
                          element['c_nf_per_km'], element['max_i_ka'], element['in_service']))

        return lines

    def _get_trafos(self, grid_idx):
        """Create trafo entities"""
        trafos = []

        for idx in self.trafo_id:
            element = self.net.trafo.iloc[idx]
            eid = make_eid(element['name'], grid_idx)
            hv_bus = make_eid(self.bus_id[element['hv_bus']], grid_idx)
            lv_bus = make_eid(self.bus_id[element['lv_bus']], grid_idx)

            hv_idx = self.entity_map[hv_bus]['idx']
            lv_idx = self.entity_map[lv_bus]['idx']

            element_data = element.to_dict()
            keys_to_del = ['name', 'hv_bus', 'lv_bus']
            element_data_static = {key: element_data[key] for key in element_data if key not in keys_to_del}
            # del element_data_static

            self.entity_map[eid] = {'etype': 'Trafo', 'idx': idx, 'static': element_data_static,
                                    'related': [hv_bus, lv_bus]}

        trafos.append((hv_idx, lv_idx, element['sn_mva'], element['vn_hv_kv'], element['vn_lv_kv'],
                       element['vk_percent'], element['vkr_percent'], element['pfe_kw'], element['i0_percent'],
                       element['shift_degree'], element['tap_side'], element['tap_pos'], element['tap_neutral'],
                       element['tap_min'], element['tap_max'], element['in_service']))

        return trafos

    def set_inputs(self, etype, idx, data, static):
        """setting the input from other simulators"""
        for name, value in data.items():

            if etype in ['Load', 'Storage', 'Sgen']:
                elements = getattr(self.net, etype.lower())
                elements.at[idx, name] = value

            elif etype == 'Trafo':
                if 'tap_turn' in data:
                    tap = 1 / static['tap_pos'][data['tap_turn']]
                    self.net.trafo.at[idx, 'tap_pos'] = tap  # TODO: access number of trafos

            else:
                raise ValueError('etype %s unknown' % etype)

    def powerflow(self):
        """Conduct power flow"""
        pp.runpp(self.net, numba=False)

    def powerflow_timeseries(self, time_step):
        """Conduct power flow series"""

        run_time_step(self.net, time_step, self.ts_variables, _ppc=True, is_elements=True)

    def get_cache_entries(self):
        """cache the results of the power flow to be communicated to other simulators"""

        cache = {}
        case = self.net

        for eid, attrs in self.entity_map.items():
            etype = attrs['etype']
            idx = attrs['idx']
            data = {}
            attributes = OUTPUT_ATTRS[etype]

            if not case.res_bus.empty:
                element_name = f'res_{etype.lower()}'
                if etype != 'Ext_grid':
                    element = getattr(case, element_name).iloc[idx]

                else:
                    element = getattr(case, element_name).iloc[0]

                for attr in attributes:
                    data[attr] = element[attr]

            else:
                # Failed to converge.
                for attr in attributes:
                    data[attr] = float('nan')

            cache[eid] = data
        return cache


def make_eid(name, grid_idx):
    return '%s-%s' % (grid_idx, name)


def create_output_writer(net, time_steps, output_dir):
    """Pandapower output to save results"""
    ow = OutputWriter(net, time_steps, output_path=output_dir, output_file_type=".xls")
    # these variables are saved to the harddisk after / during the time series loop
    for etype, attrs in OUTPUT_ATTRS.items():
        element_name = f'res_{etype.lower()}'
        for attr in attrs:
            ow.log_variable(element_name, attr)

    return ow


if __name__ == "__main__":
    ppc = pandapower()
    x, y = ppc.load_case('cigre_mv_all', 0)
    buss = ppc._get_buses(0)
    stoxx = ppc._get_storage(0)
    ppc.powerflow()
    #busx=ppc._get_loads()
    #busxx = ppc._get_loads(0)
    #busy=ppc._get_branches()
    #buso=ppc._get_trafos()
    #busz=ppc._get_sgen()
    #ppc.entity_map()
    res = ppc.get_cache_entries()

