#! /bin/bash
lxterminal -e ssh Raspinator@145.94.130.178 './Illuminator/configuration/runshfile/runPV.sh 145.94.130.178 5123 /home/Raspinator/Illuminator/src/illuminator/models/'&
lxterminal -e ssh Raspinator@145.94.130.178 './Illuminator/configuration/runshfile/runLED_connection.sh 145.94.130.178 5124 /home/Raspinator/Illuminator/src/illuminator/models/'&
