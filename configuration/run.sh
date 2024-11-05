#! /bin/bash
lxterminal -e ssh illuminator@192.168.0.1 './Desktop/illuminatorclient/configuration/runshfile/runBattery.sh 192.168.0.1 5000 /home/illuminator/Desktop/Final_illuminator'&
lxterminal -e ssh illuminator@192.168.0.2 './Desktop/illuminatorclient/configuration/runshfile/runBattery.sh 192.168.0.2 5000 /home/illuminator/Desktop/Final_illuminator'&
lxterminal -e ssh illuminator@192.168.0.3 './Desktop/illuminatorclient/configuration/runshfile/runPV.sh 192.168.0.3 5123 /home/illuminator/Desktop/Final_illuminator'&
