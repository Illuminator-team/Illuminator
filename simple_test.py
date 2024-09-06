import mosaik.util
# pv_set, pv_panel_set and realtimefactor ar the only things missing. So an import * is excessive
# also buildmodelset is just a list of predefined variables
from configuration.buildmodelset import *

# ERRORS:
# No errors found, passes

START_DATE = '2012-01-02 00:00:00'
# QUESTION: Why do you prefer to use a duration in seconds instead of a datetime object?
end = 1 * 24 * 3600  # last one interval is not computed


# 
PV_DATA = 'Scenarios/pv_data_Rotterdam_NL-15min.txt'


# Configuration for collector, 
sim_config={
    'Collector':{'python':'Models.collector:Collector'},
    'CSVB':{'python':'Models.mosaik_csv:CSV'},
    'PV':{'python':'Models.PV.pv_mosaik:PvAdapter'},
}


world = mosaik.World(sim_config, debug=True)

collector = world.start('Collector', start_date=START_DATE,
                        results_show={'write2csv':True, 'dashboard_show':False, 'Finalresults_show':False,'database':False, 'mqtt':False},
                        output_file='Result/forecast.csv',db_file='Result/result3.db',
                        mqtt_broker='mqtt://192.168.10.90:1883', mqtt_topic='TGVFCBB75')
monitor = collector.Monitor()

solardata = world.start('CSVB', sim_start=START_DATE, datafile=PV_DATA)
pvsim = world.start('PV')
pv = pvsim.PVset.create(1, sim_start=START_DATE, panel_data=pv_panel_set,
                        m_tilt=pv_set['m_tilt'], m_az=pv_set['m_az'], cap=pv_set['cap'],
                        output_type=pv_set['output_type'])
solarprofile_data = solardata.Solar_data.create(1)
world.connect(solarprofile_data[0], pv[0], 'G_Gh', 'G_Dh', 'G_Bn', 'Ta', 'hs', 'FF', 'Az')
world.connect(pv[0], monitor,'pv_gen')
if realtimefactor == 0:
    world.run(until=end)
else:
    world.run(until=end, rt_factor=realtimefactor)
