#! /bin/bash
lxterminal -e ssh Raspinator@192.168.27.161 './Illuminator/configuration/runshfile/runPV.sh 192.168.27.161 5123 /home/Raspinator/Illuminator/src/illuminator/models/'&
lxterminal -e ssh Raspinator@192.168.27.161 './Illuminator/configuration/runshfile/runLED_connection.sh 192.168.27.161 5124 /home/Raspinator/Illuminator/src/illuminator/models/'&
lxterminal -e ssh Raspinator@192.168.27.19 './Illuminator/configuration/runshfile/runWind.sh 192.168.27.19 5001 /home/Raspinator/Illuminator/src/illuminator/models/'&
lxterminal -e ssh Raspinator@192.168.27.19 './Illuminator/configuration/runshfile/runLED_connection.sh 192.168.27.19 5124 /home/Raspinator/Illuminator/src/illuminator/models/'&
