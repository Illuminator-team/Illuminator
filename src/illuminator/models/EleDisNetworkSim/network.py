import pandapower as pp

from pandas import read_json
def create_cigre_lv_resident():
    """
    Create the CIGRE LV Grid from final Report of Task Force C6.04.02:
    "Benchmark Systems for Network Integration of Renewable and Distributed Energy Resources”, 2014.
    
    ...

    Returns
    -------
    net : object
        The pandapower format network.
    """
    net_cigre_lv = pp.create_empty_network()

    # Linedata
    # UG1
    line_data = {'c_nf_per_km': 0.0, 'r_ohm_per_km': 0.162,
                 'x_ohm_per_km': 0.0832, 'max_i_ka': 1.0,
                 'type': 'cs'}
    pp.create_std_type(net_cigre_lv, line_data, name='UG1', element='line')

    # UG3
    line_data = {'c_nf_per_km': 0.0, 'r_ohm_per_km': 0.822,
                 'x_ohm_per_km': 0.0847, 'max_i_ka': 1.0,
                 'type': 'cs'}
    pp.create_std_type(net_cigre_lv, line_data, name='UG3', element='line')

    # OH1
    line_data = {'c_nf_per_km': 0.0, 'r_ohm_per_km': 0.4917,
                 'x_ohm_per_km': 0.2847, 'max_i_ka': 1.0,
                 'type': 'ol'}
    pp.create_std_type(net_cigre_lv, line_data, name='OH1', element='line')

    # OH2
    line_data = {'c_nf_per_km': 0.0, 'r_ohm_per_km': 1.3207,
                 'x_ohm_per_km': 0.321, 'max_i_ka': 1.0,
                 'type': 'ol'}
    pp.create_std_type(net_cigre_lv, line_data, name='OH2', element='line')

    # OH3
    line_data = {'c_nf_per_km': 0.0, 'r_ohm_per_km': 2.0167,
                 'x_ohm_per_km': 0.3343, 'max_i_ka': 1.0,
                 'type': 'ol'}
    pp.create_std_type(net_cigre_lv, line_data, name='OH3', element='line')

    # Busses
    bus0 = pp.create_bus(net_cigre_lv, name='Bus 0', vn_kv=20.0, type='b', zone='CIGRE_LV')
    busR0 = pp.create_bus(net_cigre_lv, name='Bus R0', vn_kv=20.0, type='b', zone='CIGRE_LV')
    busR1 = pp.create_bus(net_cigre_lv, name='Bus R1', vn_kv=0.4, type='b', zone='CIGRE_LV')
    busR2 = pp.create_bus(net_cigre_lv, name='Bus R2', vn_kv=0.4, type='m', zone='CIGRE_LV')
    busR3 = pp.create_bus(net_cigre_lv, name='Bus R3', vn_kv=0.4, type='m', zone='CIGRE_LV')
    busR4 = pp.create_bus(net_cigre_lv, name='Bus R4', vn_kv=0.4, type='m', zone='CIGRE_LV')
    busR5 = pp.create_bus(net_cigre_lv, name='Bus R5', vn_kv=0.4, type='m', zone='CIGRE_LV')
    busR6 = pp.create_bus(net_cigre_lv, name='Bus R6', vn_kv=0.4, type='m', zone='CIGRE_LV')
    busR7 = pp.create_bus(net_cigre_lv, name='Bus R7', vn_kv=0.4, type='m', zone='CIGRE_LV')
    busR8 = pp.create_bus(net_cigre_lv, name='Bus R8', vn_kv=0.4, type='m', zone='CIGRE_LV')
    busR9 = pp.create_bus(net_cigre_lv, name='Bus R9', vn_kv=0.4, type='m', zone='CIGRE_LV')
    busR10 = pp.create_bus(net_cigre_lv, name='Bus R10', vn_kv=0.4, type='m', zone='CIGRE_LV')
    busR11 = pp.create_bus(net_cigre_lv, name='Bus R11', vn_kv=0.4, type='m', zone='CIGRE_LV')
    busR12 = pp.create_bus(net_cigre_lv, name='Bus R12', vn_kv=0.4, type='m', zone='CIGRE_LV')
    busR13 = pp.create_bus(net_cigre_lv, name='Bus R13', vn_kv=0.4, type='m', zone='CIGRE_LV')
    busR14 = pp.create_bus(net_cigre_lv, name='Bus R14', vn_kv=0.4, type='m', zone='CIGRE_LV')
    busR15 = pp.create_bus(net_cigre_lv, name='Bus R15', vn_kv=0.4, type='m', zone='CIGRE_LV')
    busR16 = pp.create_bus(net_cigre_lv, name='Bus R16', vn_kv=0.4, type='m', zone='CIGRE_LV')
    busR17 = pp.create_bus(net_cigre_lv, name='Bus R17', vn_kv=0.4, type='m', zone='CIGRE_LV')
    busR18 = pp.create_bus(net_cigre_lv, name='Bus R18', vn_kv=0.4, type='m', zone='CIGRE_LV')

    # Lines
    pp.create_line(net_cigre_lv, busR1, busR2, length_km=0.035, std_type='UG1',
                   name='Line R1-R2')
    pp.create_line(net_cigre_lv, busR2, busR3, length_km=0.035, std_type='UG1',
                   name='Line R2-R3')
    pp.create_line(net_cigre_lv, busR3, busR4, length_km=0.035, std_type='UG1',
                   name='Line R3-R4')
    pp.create_line(net_cigre_lv, busR4, busR5, length_km=0.035, std_type='UG1',
                   name='Line R4-R5')
    pp.create_line(net_cigre_lv, busR5, busR6, length_km=0.035, std_type='UG1',
                   name='Line R5-R6')
    pp.create_line(net_cigre_lv, busR6, busR7, length_km=0.035, std_type='UG1',
                   name='Line R6-R7')
    pp.create_line(net_cigre_lv, busR7, busR8, length_km=0.035, std_type='UG1',
                   name='Line R7-R8')
    pp.create_line(net_cigre_lv, busR8, busR9, length_km=0.035, std_type='UG1',
                   name='Line R8-R9')
    pp.create_line(net_cigre_lv, busR9, busR10, length_km=0.035, std_type='UG1',
                   name='Line R9-R10')
    pp.create_line(net_cigre_lv, busR3, busR11, length_km=0.030, std_type='UG3',
                   name='Line R3-R11')
    pp.create_line(net_cigre_lv, busR4, busR12, length_km=0.035, std_type='UG3',
                   name='Line R4-R12')
    pp.create_line(net_cigre_lv, busR12, busR13, length_km=0.035, std_type='UG3',
                   name='Line R12-R13')
    pp.create_line(net_cigre_lv, busR13, busR14, length_km=0.035, std_type='UG3',
                   name='Line R13-R14')
    pp.create_line(net_cigre_lv, busR14, busR15, length_km=0.030, std_type='UG3',
                   name='Line R14-R15')
    pp.create_line(net_cigre_lv, busR6, busR16, length_km=0.030, std_type='UG3',
                   name='Line R6-R16')
    pp.create_line(net_cigre_lv, busR9, busR17, length_km=0.030, std_type='UG3',
                   name='Line R9-R17')
    pp.create_line(net_cigre_lv, busR10, busR18, length_km=0.030, std_type='UG3',
                   name='Line R10-R18')

    # Trafos
    pp.create_transformer_from_parameters(net_cigre_lv, busR0, busR1, sn_mva=0.5, vn_hv_kv=20.0,
                                          vn_lv_kv=0.4, vkr_percent=1.0, vk_percent=4.123106,
                                          pfe_kw=0.0, i0_percent=0.0, shift_degree=30.0,
                                          tap_neutral=0,tap_max=5,tap_min=-5,tap_step_percent=1.0,
                                          tap_pos=0, name='Trafo R0-R1')

    # External grid
    pp.create_ext_grid(net_cigre_lv, bus0, vm_pu=1.0, va_degree=0.0, s_sc_max_mva=100.0,
                       s_sc_min_mva=100.0, rx_max=1.0, rx_min=1.0)

    # Loads
    pp.create_load(net_cigre_lv, busR1, p_mw=0.02, q_mvar=0.00019, name='Load R1')
    pp.create_load(net_cigre_lv, busR2, p_mw=0.02, q_mvar=0.00019, name='Load R2')
    pp.create_load(net_cigre_lv, busR3, p_mw=0.02, q_mvar=0.00019, name='Load R3')
    pp.create_load(net_cigre_lv, busR4, p_mw=0.02, q_mvar=0.00019, name='Load R4')
    pp.create_load(net_cigre_lv, busR5, p_mw=0.02, q_mvar=0.00019, name='Load R5')
    pp.create_load(net_cigre_lv, busR6, p_mw=0.02, q_mvar=0.00019, name='Load R6')
    pp.create_load(net_cigre_lv, busR7, p_mw=0.02, q_mvar=0.00019, name='Load R7')
    pp.create_load(net_cigre_lv, busR8, p_mw=0.02, q_mvar=0.00019, name='Load R8')
    pp.create_load(net_cigre_lv, busR9, p_mw=0.02, q_mvar=0.00019, name='Load R9')
    pp.create_load(net_cigre_lv, busR10, p_mw=0.02, q_mvar=0.00019, name='Load R10')
    pp.create_load(net_cigre_lv, busR11, p_mw=0.02, q_mvar=0.00019, name='Load R11')
    pp.create_load(net_cigre_lv, busR12, p_mw=0.02, q_mvar=0.00019, name='Load R12')
    pp.create_load(net_cigre_lv, busR13, p_mw=0.02, q_mvar=0.00019, name='Load R13')
    pp.create_load(net_cigre_lv, busR14, p_mw=0.02, q_mvar=0.00019, name='Load R14')
    pp.create_load(net_cigre_lv, busR15, p_mw=0.02, q_mvar=0.00019, name='Load R15')
    pp.create_load(net_cigre_lv, busR16, p_mw=0.02, q_mvar=0.00019, name='Load R16')
    pp.create_load(net_cigre_lv, busR17, p_mw=0.02, q_mvar=0.00019, name='Load R17')
    pp.create_load(net_cigre_lv, busR18, p_mw=0.02, q_mvar=0.00019, name='Load R18')

    # Switches
    pp.create_switch(net_cigre_lv, bus0, busR0, et='b', closed=True, type='CB', name='S1')
    net_cigre_lv.bus_geodata = read_json(
        """{"x":{"0":0.2,"1":0.2,"2":-1.4583333333,"3":-1.4583333333,"4":-1.4583333333,
        "5":-1.9583333333,"6":-2.7083333333,"7":-2.7083333333,"8":-3.2083333333,"9":-3.2083333333,
        "10":-3.2083333333,"11":-3.7083333333,"12":-0.9583333333,"13":-1.2083333333,
        "14":-1.2083333333,"15":-1.2083333333,"16":-1.2083333333,"17":-2.2083333333,
        "18":-2.7083333333,"19":-3.7083333333},
        "y":{"0":1.0,"1":1.0,"2":2.0,"3":3.0,"4":4.0,"5":5.0,"6":6.0,"7":7.0,"8":8.0,"9":9.0,
        "10":10.0,"11":11.0,"12":5.0,"13":6.0,"14":7.0,"15":8.0,"16":9.0,"17":8.0,"18":11.0,
        "19":12.0}}""")
    # Match bus.index
    net_cigre_lv.bus_geodata = net_cigre_lv.bus_geodata.loc[net_cigre_lv.bus.index]
    return net_cigre_lv

if __name__ == "__main__":
    net=create_cigre_lv_resident()
    print(net)
