import subprocess
from os import system, getcwd

USERNAME = 'Raspinator'

ips = ['192.168.1.193', '192.168.1.111', '192.168.1.182', '192.168.1.149', '192.168.1.192']

print('updating master')
system('git pull')

for client_ip in ips:
    print('updating Client: ', client_ip)
    subprocess.run(f"ssh {USERNAME}@{client_ip} 'cd Illuminator && git pull'", shell=True)

print("\nDONE")
