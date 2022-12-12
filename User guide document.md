# User Guide document 
## Configuration and simulation
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
The PV model set and explanation is shown as below.
```
pv_panel_set ={'Module_area': 1.26, 'NOCT': 44, 'Module_Efficiency': 0.198, 'Irradiance_at_NOCT': 800,
          'Power_output_at_STC': 250}
pv_set={'m_tilt':14,'m_az':180,'cap':50,'output_type':'power'}

#'Module_area' # module area. available in the spec sheet of a pv module
#'NOCT'  #module temperature under the standard test conditions (STC) and stands for Nominal Operating Cell Temperature
#'Module_Efficiency'
#'Irradiance_at_NOCT'# W/m2 This is the irradiance that falls on the panel under NOCT conditions
#'Power_output_at_STC'# Watts. Available in spec sheet of a module
# m_tilt #module tilt angle
# m_az #azimuth of the module
# cap #capacity
#output_type #power or energy
#azimuth of the module is set to 90
```
Calculation the irradiance on the PV module

Calculating the irradiance on a module at a specific location is essential to calculate the output of
a PV system, and is governed by multiple factors. Irradiance is defined as the incoming power of
the solar radiation over a unit area and is measured in W/m2. Due to rotation and revolution of the
earth, the positioning of the sun is not constant, and hence the amount of irradiation received changes continuously with time of the day, month, and year. Location on the earth also factors in for the amount of irradiance received. Due to the changing elevation and azimuth angle of the sun throughout the day, the incoming solar radiations are not normal to the surface. The angle between the normal of the surface and the solar radiation is called Angle of Incidence (AOI) and it affects the amount of irradiance of the module surface.
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
	<img align="center" src="docs/Figure/case study.jpg" width="500">
</div>

