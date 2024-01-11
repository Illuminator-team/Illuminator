# Illuminator
The Illuminator is an easy-to-use Energy System Integration 
Development kit to demystify energy system operation, illustrate challenges 
that arise due to the energy transition and test 
state-of-the-art energy management concepts. we utilise Raspberry Pis
as the individual components of the energy system emulator, 
and the simulation engine is based on [Mosaik](https://mosaik.offis.de/).

## Contact/Support
* This project is supported by [TU Delft PowerWeb](https://www.tudelft.nl/powerweb) and [Stichting 3E](https://www.stichting3e.nl/).
* For more comprehensive support, please contact us at illuminator@tudelft.nl. Additionally, you can reach out to the main contributors for specific inquiries:
	Aihui Fu: A.Fu@tudelft.nl
	Dr.ir. Milos Cvetkovic: M.Cvetkovic@tudelft.nl



## The Illuminator setup in short
The setup consists of one leader RasPi and several follower RasPis.
The leader RasPi has permission to access and control the
follower RasPis through Secure Shell Protocol (SSH). Once we
set the simulation configuration, the leader RasPi will engage
the follower RasPis to run the specified simulators. During the
simulation, the information will be exchanged between RasPis via socket connection.
The leader RasPi shows the results through Dashboard and saves the results
to a ’.csv’ file for later analysis. 
Since the Illuminator is Python based, this code can also run on regular machines(PC). If you run 
the Illuminator in one regular PC, then you don't need to do the Illuminator environment set up.
<div align="center">
	<img align="center" src="docs/Figure/Structure.jpg" width="500">
</div>

## Illuminator environment set up for a Raspberry Pi cluster
1. [Install Raspberry pi OS using raspberry pi imager.](https://www.raspberrypi.com/software/)
2. Set static IP address for the Raspberry Pi.
    Use the following command from in terminal to open the dhcpcd.conf file:
    ```
    sudo nano /etc/dhcpcd.conf
    ```
   In the dhcpcd.conf file, find the information to change the IP address as static as following:
   ```
   interface etho
   static ip_address=192.168.0.1/24#change the IP address as you want
   ```
   Finally reboot the Raspberry Pi through `sudo reboot` in the terminal.
3. [Set leader RasPi to connect followers without password.](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-2)
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
   itertools
   ```
5. Send the Illuminator package to all follower Raspberry Pis. Use the following command in the leader Raspberry Pi terminal to check the connection 
between leader and follower Raspberry Pis. 
   ```
   ssh illuminator@ip #ip represent your follower IP address
   ```
6. Run the ‘buildcilentremoterun.py’ file at each follower and give all users execute permission to all the documents in “runshfile” in order 
to make sure the leader can access the follower model.
   ```
   chmod -R a+X *dir*
   ```

More detialed instructions are given in the [user guide document](User%20guide.md) and [model build up document](Models.md).
## License & Contributing development
Illuminator is available under a GNU Lesser General Public License (LGPL) license.
The Illuminator team accepts contributions to the Illuminator source, test files, documentation, and other materials distributed with the program.
If you are interested in contributing, please start there, and feel free to reach out to the team using illuminator@tudelft.nl. The Illuminator team does not take any responsibility for the damage or loss that this code might provide. 

Reference for the Illuminator: A. Fu, R. Saini, R. Koornneef, A. van der Meer, P. Palensky and M. Cvetković, "The Illuminator: An Open Source Energy System Integration Development Kit," 2023 IEEE Belgrade PowerTech, Belgrade, Serbia, 2023, pp. 01-05, doi: 10.1109/PowerTech55446.2023.10202816.

The Illuminator V2 thanks the contribution of Raghav Saini and Niki Balassi
