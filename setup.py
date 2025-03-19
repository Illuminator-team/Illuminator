import subprocess
from os import system, getcwd

USERNAME = 'Raspinator'

client_ip = input('please provide the ip of the Client pi: ')
# password = input('please provide the password of the Client pi: ')

# def remote_command(command: str):
#     # Run SSH with interactive input for the password
#     proc = subprocess.Popen(
#         ["ssh", f"{USERNAME}@{client_ip}", command],
#         stdin=subprocess.PIPE,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True
#     )

#     # Send the password when prompted
#     proc.stdin.write(password + "\n")
#     proc.stdin.flush()

#     # Capture and print output
#     stdout, stderr = proc.communicate()
#     print("stdout::\n", stdout)
#     print("\nstderr:\n", stderr)

# generate ssh keys and send them to the slave
print('generating ssh keys and sending it to the new Client')
# print('current directory: ', getcwd())
system(f"python cluster_setup/generate_ssh_key.py {USERNAME} {client_ip}")

# setting static ip
print('\n\n##########################################')
print('making ip address static')
subprocess.run(f"ssh {USERNAME}@{client_ip} 'sudo python Illuminator/cluster_setup/static_ip.py'", shell=True)
# system('python cluster_setup/static_ip.py')

# give executive permission to all files in runshfile/
print('\n\n##########################################')
print('making runshfiles executable')
subprocess.run(f"ssh {USERNAME}@{client_ip} 'chmod +x Illuminator/configuration/runshfile/*.sh'", shell=True)


print('\n\n##########################################')
print('setup finished, rebooting new Client')
subprocess.run(f"ssh {USERNAME}@{client_ip} 'sudo reboot'", shell=True)

print("\nDONE")
