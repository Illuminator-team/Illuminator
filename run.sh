#! /bin/bash
lxterminal -e ssh Raspinator@10.89.147.122 'source .venvs/ill-cluster/bin/activate; ./Illuminator/configuration/runshfile/runLED_connection.sh 10.89.147.122 5124 /home/Raspinator/Illuminator/src/illuminator/models/'&
