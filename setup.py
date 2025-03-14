from os import system

USERNAME = 'Raspinator'

# setting static ip
print('making ip adres static')
system('python cluster_setup/static_ip.py')

# give executive permission to all files in runshfile/
print('making runshfiles executable')
system('chmod +x configuration/runshfile/*.sh')

# generate ssh keys and send them to the master
print('generating ssh keys and sending it to the master')
master_ip = input('please provide the ip of the master pi: ')
system(f"cluster_setup/generate_ssh_key.py {USERNAME} {master_ip}")

print('FINISHED')

