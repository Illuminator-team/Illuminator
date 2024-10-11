#! /bin/bash
cd $3/Heatpump/controller
python controller_mosaik.py $1:$2 --remote
