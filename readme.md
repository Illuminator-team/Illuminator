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

## User guide document 
1. The users can change the `config.xml` to change the configuration of the simulation study.
   Here is an example of the information in the config.xml file. 
   It means we would like build only Wind and PV models in our simulation study. 
   The wind model is running and import from python file, and the PV model is running in another Raspi which ip address is ‘192.168.0.1’, 
   and the master get the pv model information from the port ’5123’.
   ```
    #'Wind' ,'python','Models.Wind.wind_mosaik:WindSim'
    #'PV','connect', '192.168.0.1:5123'
    
    <?xml version='1.0' encoding='utf-8'?>
    <data>
      <row>
        <index>0</index>
        <model>Wind</model>
        <method>python</method>
        <location>Models.Wind.wind_mosaik:WindSim</location>
      </row>
      <row>
        <index>1</index>
        <model>PV</model>
        <method>connect</method>
        <location>192.168.0.1:5123</location>
      </row>
   ```
   
2. The users can change the `connection.xml` to set how the message transferred from one model to others. 
   Here is an example of the information in the connection file.  
   The model ctrl send the information ‘flow2e’ to electrolyser to control its hydrogen generating speed. 
   The electrolyser send the ‘h2_gen’ information to model h2storage ‘h2_in’ to control the hydrogen storing speed.
   ```
    #['ctrl', 'electrolyser', 'flow2e'],
    #['electrolyser', 'h2storage', 'h2_gen', 'h2_in'],
    
    <row>
        <index>13</index>
        <send>ctrl</send>
        <receive>electrolyser</receive>
        <message>flow2e</message>
        <more/>
      </row>
      <row>
        <index>14</index>
        <send>electrolyser</send>
        <receive>h2storage</receive>
        <message>h2_gen</message>
        <more>h2_in</more>
   ```
   The `connection.xml` file can be build through hard draw in the web my script software through run the script `drawpptx.py`, draw what you want to connect in the simulation case study, 
   save what you drawed as `example.pptx`, and finally run the `readppt_connectionxml.py` to set the `connection.xml`.
3. The model parameters, how to show the results and if we do the real time simulation are set in the file `buildmodelse.py`.
	```
	Battery_initialset = {'initial_soc': 20}
	Battery_set = {'max_p': 500, 'min_p': -500, 'max_energy': 500,
		    'charge_efficiency': 0.9, 'discharge_efficiency': 0.9,
		    'soc_min': 10, 'soc_max': 90, 'flag': 0, 'resolution': 15}  #p in kW
	#Set flag as 1 to show fully discharged state; -1 show fully charged,0 show ready to charge and discharge

	h2storage_initial = {'initial_soc': 20}
	h2_set = {'h2storage_soc_min': 10, 'h2storage_soc_max': 90, 'max_h2': 200, 'min_h2': -200, 'flag': -1}
	#max_h2 in kWh; flag as 1 to show fully discharged state; -1 show fully charged,0 show ready to charge and discharge

	pv_panel_set ={'Module_area': 1.26, 'NOCT': 44, 'Module_Efficiency': 0.198, 'Irradiance_at_NOCT': 800,
		  'Power_output_at_STC': 250}
	pv_set={'m_tilt':14,'m_az':180,'cap':500000,'output_type':'power'}
	# 'NOCT':degree celsius; 'Irradiance_at_NOCT':W/m2 This is the irradiance that falls on the panel under NOCT conditions
	# Watts. Available in spec sheet of a module
	load_set={'houses':200, 'output_type':'power'}

	Wind_set={'p_rated':110, 'u_rated':10.3, 'u_cutin':2.8, 'u_cutout':25, 'cp':0.40, 'diameter':22, 'output_type':'power'}
	#  p_rated  # kW power it generates at rated wind speed and above
	# u_rated  # m/s #windspeed it generates most power at
	#  u_cutin  # m/s #below this wind speed no power generation
	# u_cutout  # m/s #above this wind speed no power generation. Blades are pitched
	# cp  # coefficient of performance of a turbine. Usually around0.40. Never more than 0.59
	# powerout = 0  # output power at wind speed u
	fuelcell_set={'eff':0.45}

	electrolyser_set={'eff':0.60,'fc_eff':0.45,'resolution':15}

	RESULTS_SHOW_TYPE={'write2csv':True, 'dashboard_show':True, 'Finalresults_show':True}
	#'write2csv':True/Flause   Write the results to csv file
	# #'Realtime_show':True/Flause, show the results in dashboard
	# 'Finalresults_show':True/Flause, show the results after finish the simulation

	realtimefactor=0
	#0 as soon as possible. 1/60 using 1 second simulate 1 mintes
	```
5. Finally run the `demo.py` to run the simulation. If the user want to see the results shown in the dashboard, you need internet and sign up in [wandb software](https://wandb.ai/site).

## Provided models and document explanation
### `Input Profiles`
This file include all the input profiles, which include wind data, pv data and load data.Wind data chosen is from an on-shore site situated in The Netherlands at a height of 100m at 5 minutes interval. PV data is from the Meteonorm software, solar radiation and positioning values were obtained for the region of Rotterdam. With the new updates, it was possible to extract 15 minute interval data from within meteonorm. 15 minute interval data option from meteonorm does not provide the values for azimuth angle of the sun which are essential to the calculation. To do this, the pvlib for python from sandia was used which takes the location coordinates as the inputs. The Load profile is typical residential load profile in the Netherlands.
### `Output Profiles`
This simulation results is saved as an `.csv` document in this file.
### `Models`
All the simulation models are located in this file, which include PV, Wind, Battery, Electrolyser, Fuel cell and hydrogen tank models. 
#### PV model
The PV model set is shown as below.
```

```


## Demos
We build a case study as a demo to show how to use Illuminator to demonstrate this system at
a general user level and verify the Illuminator’s performance. The demo include Households,
PV panels, Wind generators, Battery and Hydrogen system
to achieve electric power self-sufficiency. The controller’s
algorithm in the case study runs in the Master RasPi, and
the rest simulators are separately deployed in different Client
RasPis.The data flow between the simulators is also shown in
the figure. Based on the inputs, including the generated power
from PV and Wind, the consuming power of households, and
the state of charge (Soc) of the Battery and Hydrogen, the
controller decides the power from the Battery and Fuel cell
and the power to the Electrolyser. In the case study, we use
simple logic to achieve self-sufficiency. If Battery has enough
capacity for charging or discharging to achieve power balance,
use the Battery first. If Battery doesn’t have enough capacity
to achieve power balance, then use Electrolyser or Fuel cell
to achieve power balance. All the input data are in file `Input profiles` and all the output data are in file `Output profiles`.

<div align="center">
	<img align="center" src="docs/Figure/case study.jpg" width="300">
</div>


## License & Contributing Development
Illuminator is available under a GNU Lesser General Public License (LGPL) license.
The Illuminator team accepts contributions to Illuminator source, test files, documentation, and other materials distributed with the program.
If you are interested in contributing, please start there, but feel free to reach out to the team.
