#! /bin/bash
cd $3
python dummy.py $1:$2 --remote
echo "finished"
