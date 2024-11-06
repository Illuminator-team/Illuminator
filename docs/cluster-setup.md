# Cluster Pi Setup

The setup for the Illuminator requires one Raspberry Pi acting as a **server** and several **clients** Raspberry Pi's.
Raspberry Pi's must be connected and configured as a local network, and the
*server* must be configured to have permissions to access and control the *clients* through the Secure Shell Protocol (SSH).

During simulation, the *server* engage with the *clients* to run the simulations defined in the *simulation configuration*, and
information is exchanged between Rasberry Pi's using network sockets.
The **server** provides a Dashboard to viazulize the results, and saves them to a `.csv` files for later analysis. 

<div align="center">
	<img align="center" src="_static/img/Structure.jpg" width="500">
</div>


## Set up

On every raspberrry Pi: 

1. [Install Raspberry pi OS using Raspberry Pi imager.](https://www.raspberrypi.com/software/).
2. Set an static IP address for each Raspberry Pi. Use the following command on the terminal to open the `dhcpcd.conf` file:

   ```shell
   sudo nano /etc/dhcpcd.conf
   ```

   In the `dhcpcd.conf` file, find the information to change the IP address to static as following:

   ```shell
   interface etho
   static ip_address=192.168.0.1/24 # change the IP address as you want
   ```

   Give all users execute permission to all the documents in `runshfile/` in order to make sure the *server* can access the *client* model.
   
   ```shell
   chmod -R a+X *dir*
   ```

   Finally, reboot the Raspberry Pi suing `sudo reboot` on the terminal.
3. [Configure SSH connections so that the *master* can connect to the *clients* without a password.](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-2)

4. Install the Illuminator Python package, and the addional dependencies:

   ```shell
   # if connected to the internet
   pip install illuminator

   # or, if from source code
   pip install Illuminator/
   ```

   ```shell
   # aditional dependencies
   pip install tk python-csv python-math scipy wandb itertools
   ```
5. Use the following command on the *master's* terminal to check the connection  between *master* and the *clients*

   ```shell
   # notice that the followng assumes that each client has a 
   # user named 'illuminator'
   ssh illuminator@ip #ip represent your follower IP address
   ```
6. Run the `build_runshfile.py` file in the configuration directory on *server*, this will generate a  to generate a `run.sh` script. Give the appropiate `config.yaml` file containing the simulation scenario definition:
   
   ```shell
   python3 build_runshfile.py <config.yaml>
   ```


## Contact and Support

For more comprehensive support, please contact us at [illuminator@tudelft.nl](mailto:illuminator@tudelft.nl). Additionally, you can reach out to the main contributors for specific inquiries:
* [Dr.ir. Milos Cvetkovic](mailto:M.Cvetkovic@tudelft.nl)
