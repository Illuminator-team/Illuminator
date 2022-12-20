# User Guide document 
## Configuration
There are three methods to configurate the cases.
1. Through provide `config.xml` and `connection.xml` files in the `Cases` folder. We provide an example in
the `Resisential Case` folder. Then run `interpreter.py` file in `configuration` folder to set the case configuration.

   The `config.xml` file is used to define the models in the case and where to 
   run the model. Here is an example of the information in the config.xml file. 
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
   The `connection.xml` file is to set how the message transferred from one model to others. 
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

2. The users can build case through run the scripts `build_configuration_xml`. Through running the scripts, the `config.xml` and `connection.xml`
file will be automatically built. If you want to change the configuration, the user need to change the parameter 'sim_config' and 'sim_config'.
3. The Illuminator also provide visualized method to do the configuration. The user can use smarter board, touch screen or mouse to configurate 
the case. Firstly, run `drawpptx.py`, the user can draw their configuration by hard draw and save as 'example.pptx' file, such as below.
<div align="center">
	<img align="center" src="docs/Figure/config.png" width="300">
</div>
Then run the script 'readppt_connectionxml' to build the configuration.
## Define models
The model parameters, results presentation and real-time simulation are all set in the file `buildmodelse.py`.
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
## Simulation
Run the `simulation creator.py` to create and run the simulation based on the provided case and scenario. 
If the user want to see the results shown in the dashboard, you need internet and sign up in [wandb software](https://wandb.ai/site).


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
to achieve power balance. All the input data are in file `Scenarios` and all the output data are in file `Result`.

<div align="center">
	<img align="center" src="docs/Figure/case study.jpg" width="500">
</div>

