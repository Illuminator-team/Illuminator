# Illuminator
The Illuminator is being developed as an easy-to-use Energy System Integration 
Development kit to demystify energy system operation, illustrate challenges 
that arise due to the energy transition to a broader community and test 
state-of-the-art energy management concepts. we utilise Raspberry Pis to work 
as the individual components of the power system emulator (or network), 
and the simulation is based on [Mosaik](https://mosaik.offis.de/).

## Contact/Support
* This project is supported by [TU Delft PowerWeb](https://www.tudelft.nl/powerweb) and [Stichting 3E](https://www.stichting3e.nl/).
* For more in-depth, developer-driven support, please contact with us through email: illuminator@tudelft.nl.

## The Illuminator structure
There is one master RasPi and several client RasPis, and
the master RasPi has permission to access and control the
client RasPis through Secure Shell Protocol (SSH). Once we
set the simulation configuration, the master RasPi will retain
the client RasPis to run the defined simulator. And during the
simulation, the information will be exchanged between master
RasPi and client RasPis through the socket. The Master RasPi
can show the results through Dashboard and save the results
to a ’.csv’ file for later analysis. 
<div align="center">
	<img align="center" src="docs/Figure/Structure.jpg" width="500">
</div>

## Illuminator Environment set up for Raspberry pi cluster
1. [Install Raspberry pi OS using raspberry pi imager.](https://www.raspberrypi.com/software/)
2. Set static ip address for the raspberry pi.
    Use the following command from in terminal to open the dhcpcd.conf file:
    ```
    sudo nano /etc/dhcpcd.conf
    ```
   In the dhcpcd.conf file, find the information to change the ip address as static as following:
   ```
   interface etho
   static ip_address=192.168.0.1/24#change the ip address as you want
   ```
   Finally reboot the Raspberry Pi through `sudo reboot` in the terminal.
3. [Set master to connect clients without password.](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-2)
4. Install the required packages in the python.
   ```
   pandas
   tk
   python-csv
   datetime
   python-math
   numpy
   scipy
   arrow
   mosaik
   mosaik_api
   mosaik.util
   wandb
   matplotlib
   ```
5. Send the illuminator package to all client Raspberry pis. Use the following command in the master Raspberry pi terminal to check the connection 
between master and client Raspberry pis. 
   ```
   ssh illuminator@ip #ip represent your client ip address
   ```
6. Run the ‘buildcilentremoterun.py’ file at each clients and give all users execute permission to all the documents in “runshfile” in order 
to make sure the master can access the client model.
   ```
   chmod -R a+X *dir*
   ```

More detials are in the [user guide document](User%20guide%20document.md) and [model build up document](Models.md).
## License & Contributing Development
Illuminator is available under a GNU Lesser General Public License (LGPL) license.
The Illuminator team accepts contributions to Illuminator source, test files, documentation, and other materials distributed with the program.
If you are interested in contributing, please start there, but feel free to reach out to the team.
