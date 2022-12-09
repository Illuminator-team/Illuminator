import socket, subprocess,re
p=subprocess.Popen(["ifconfig"],stdout=subprocess.PIPE)
ifc_resp=p.communicate()
patt=re.compile(r'inet \d{3}\.\d{3}.\d{1,3}.\d{1,3}')
resp=patt.findall(str(ifc_resp[0]))
print(resp[0].replace('inet ',''))
IPAddr=resp[0].replace('inet ','')


# import socket
# hostname=socket.gethostname()
# IPAddr=socket.gethostbyname(hostname)
# print("Your Computer Name is:"+hostname)
# print("Your Computer IP Address is:"+IPAddr)
models=['Battery','Controller','Electrolyser','H2storage','Load','PV','Wind','Fuelcell']
#models=['Battery']
for model in models:
    with open('./configuration/runshfile/run'+model+'.sh', 'w') as rsh:
        rsh.write("#! /bin/bash")
        rsh.write("\n" + "cd /home/illuminator/Desktop/Final_illuminator/Models/"+model)
        rsh.write("\npython "+model.lower()+'_mosaik.py '+IPAddr+':5123 --remote')

# import socket
# import fcntl
# import struct
# def get_ip_address(ifname):
#     s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#     return socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,
#                             struct.pack('256s',ifname[:15]))[20:24])
# get_ip_address('eth0')


