#! /bin/bash
lxterminal -e ssh illuminator@192.168.0.1 './Desktop/illuminatorclient/configuration/runshfile/runWind.sh'&
lxterminal -e ssh illuminator@192.168.0.2 './Desktop/illuminatorclient/configuration/runshfile/runPV.sh'&
lxterminal -e ssh illuminator@192.168.0.3 './Desktop/illuminatorclient/configuration/runshfile/runLoad.sh'&
lxterminal -e ssh illuminator@192.168.0.4 './Desktop/illuminatorclient/configuration/runshfile/runBattery.sh'&