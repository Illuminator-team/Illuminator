"""
Configurations for the mosaik simulations that use models 
from the illuminator package, can be defined as below.

Pre-requisites:
1. Install the illuminator as a Python package
2. The simulation should be run in the same environment where
the illuminator is installed
"""

# Configuration for collector, 
sim_config={
    'Collector':{'python':'illuminator.models.collector:Collector'},
    'CSVB':{'python':'illuminator.models.mosaik_csv:CSV'},
    'PV':{'python':'illuminator.models.PV.pv_mosaik:PvAdapter'},
}
