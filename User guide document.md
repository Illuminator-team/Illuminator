# User Guide document 
## Configuration and simulation
1. The users can change the `config.xml` to change the configuration of the simulation study.
   Here is an example of the information in the config.xml file. 
   It means we would like to build only Wind and PV models in our simulation study. 
   The wind model is running and imported from a python file, and the PV model is running in another Raspi whose ip address is '192.168.0.1', 
   and the Master get the PV model information from port' 5123'.
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
   
2. The users can change the `connection.xml` to set how the message is transferred from one model to another. 
   Here is an example of the information in the connection file.  
   The model 'ctrl' sends the information 'flow2e' to Electrolyser to control its hydrogen-generating speed. 
   The Electrolyser sends the 'h2_gen' information to model h2storage 'h2_in' to control the hydrogen storing speed.
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
   The `connection.xml` file can be built through the hard draw in the web my script software by running the script `drawpptx.py`, draw what you want to connect in the simulation case study, 
   save what you drew as `example.pptx`, and finally, run the `readppt_connectionxml.py` to set the `connection.xml`.
3. The model parameters, how to show the results, and if we do the real-time simulation are set in the file `buildmodelse.py`.
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
	# #'Realtime_show':True/Flause, show the results in Dashboard
	# 'Finalresults_show':True/Flause, show the results after finish the simulation

	realtimefactor=0
	#0 as soon as possible. 1/60 using 1 second simulate 1 mintes
	```
5. Finally, run the `demo.py` to run the simulation. If the user wants to see the results in the Dashboard, you need internet and sign up in [wandb software](https://wandb.ai/site).


## Demos
We build a case study as a demo to show how to use Illuminator to demonstrate this system at
a general user level and verify the Illuminator's performance. The demo includes Households,
PV panels, Wind generators, Batteries and Hydrogen systems
to achieve electric power self-sufficiency. The controller's
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
use the Battery first. If Battery doesn't have enough capacity
to achieve power balance, then use Electrolyser or Fuel cell
to achieve power balance. All the input data are in the folder `Input profiles,` and all the output data are in the folder `Output profiles`.

<div align="center">
	<img align="center" src="docs/Figure/case study.jpg" width="500">
</div>
