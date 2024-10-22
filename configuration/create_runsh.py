import pandas as pd

sim_config_ddf=pd.read_xml('config.xml')

sim_config={row[1]:{row[2]:row[3]}for row in sim_config_ddf.values}

print (sim_config)

tosh=sim_config_ddf[sim_config_ddf['method']=='connect']

run_path='./Desktop/illuminatorclient/configuration/runshfile/'
run_model='/home/illuminator/Desktop/Final_illuminator'

if not tosh.empty:
    with open ('run.sh', 'w') as rsh:
        rsh.write("#! /bin/bash")
        for row in tosh.values:
            ip_port=row[3].split(":")
            rsh.write("\n"+"lxterminal -e ssh illuminator@"+ip_port[0]+" '"+run_path+"run"+row[1]+".sh "+ip_port[0]+" "+ip_port[1]+" "+run_model+"'&")





