import subprocess
from os import system, getcwd

USERNAME = 'Raspinator'

ips = ['192.168.27.19', '192.168.27.161']

print('updating master')
system('git pull')

for client_ip in ips:
    print('updating Client: ', client_ip)
    subprocess.run(f"ssh {USERNAME}@{client_ip} 'cd Illuminator & git pull'", shell=True)

print("\nDONE")
