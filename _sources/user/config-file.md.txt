# Simulation Configuration File

Simulation scenarios for the *Illuminator* are define using configuration files written in YAML. The structure of a configuration must be as in the example below. 

A *simulation file* has four main sections:

- `scenario`: defines metadata and global variable for the simulation.
- `models`: defines which models are included in the simulation.
- `connections`: defines how the models in the `models` section must be connected for a particular simulation.
- `monitor`: defines which inputs, outputs, and states of a particular model must be monitored and logged during simulation. 

## Example 

The following is an example to explain the basic format of a configuration file. 
See the table below a description of each keyword and their default values. Optinal keywords can be ommitted, in those case the defaults will be used. 


```yaml
# An example of a configuration file for a simuation. Won't run successfully.
scenario:
  name: "ScenarioTest" # name for the similation
  start_time: '2012-01-01 00:00:00' # ISO 8601 start time 
  end_time: '2012-01-01 01:00:00'  
  time_resolution: 900 # time step in seconds (optional).
models: # list of models for the energy system
- name: CSVB # name for the model (must be unique)
  type: CSV # name the model type in the Illuminator
  parameters:  # vary per model type
    start: '2012-01-01 00:00:00' 
    datafile: './tests/data/solar-sample.csv' 
- name: PV
  type: PvAdapter 
  inputs:  # vary per model type (optional)
    G_Gh: null 
    G_Dh: null
  outputs:
    G_Gh: null
  states:
    state1: null
    state2: null
  triggers:
    - D_Dh
    - state2
  connect: # necessary for running a simulation in a Raspberry Pi cluster
    ip: 168.192.0.3  # IP of client machine
    port: 5000 
connections:
- from: CSVB.G_Gh # origin model, format: model_name.output_name
  to: PV.G_Gh # destinatioin model, format: model_name.input_name
- from: CSVB.G_Dh
  to: PV.G_Dh
- from: CSVB.G_Bn
  to: PV.G_Bn
- from: CSVB.Ta
  to: PV.Ta
- from: CSVB.hs
  to: PV.hs
- from: CSVB.FF
  to: PV.FF
- from: CSVB.Az
  to: PV.Az
monitor:
  file: './out.csv' # file where items are saved during simualation (optional)
  items:
  - PV.pv_gen  # List of inputs, outputs or states to monitor
```


| Keyword | Description | Optional | Default |
|---------|-------------|----------|---------|
| **scenario:** | a set of global values <br>for a simulation. |  |  |
|`name` | A name for the simulation, internally <br>this name will be asssigned to what <br>the Mosaik World created during runtime. |  |  |
| `start_time` | start time for the simulation.<br>Must be a timestamp in ISO 8601 format |  |  |
| `end_time` | end time for the simulation. <br>Must be a timestamp in ISO 8601 format.  |  |  |
| `time_resolution` | number of seconds between <br>simulation steps | &#9745; | 900 (15 min)
| **models:** | a list of models for <br>the simulation | |  |
|  `name` | a name for the model. Must <br>be unique for each simulation |  |   |
| `type`  | type of model. This must correspond <br>with the name of the model <br>registered in the Illuminator. | |  |
| `inputs`  | a set of input-names and initial <br>values for the model. The model <br>type determines which names and <br>values are applicable to each model, <br>and they must be declared accordingly. <br>Inputs are optional | | If the value is set to `null`, <br>the default value will be <br>used. See the respective model <br>type for details.|
| `outputs` | a set of output-names and initial <br>values for the model. Similar to <br>*inputs* valid names and values <br>for each model are determined by <br>the model *type*. See the respective <br>model type for details. | | If the value is set to `null`, <br>the default value will be used. |
| `parameters`  | a set of name-value pairs for <br>the model. Parameters declared constants <br>for a model during runtime. | &#9745; | If ommited, the default values <br>will be used. See the <br>respective model type for details. |
| `states` | a set of name-value pairs considered <br>as states for the model. The values modify <br>the internal initial values of a state. | &#9745; | If ommited, the default <br>values will be used. See the <br>respective model type for details. |
| `triggers` | names of inputs, output or states <br>that are use as triggers for a particular model. <br>Triggers can only be declared by models <br>that implement the *event-based paradigm*. <br>See the respective model type to know if <br>it accepts triggers. |  &#9745; | |
| `connect` | to declare in which client a model runs <br>when using a Raspberry Pi cluster. | &#9745;  | |
| `ip` | Ip of the client manchine that will run <br>the model. Only IP version 4 format. |  |   |
| `port` | TCP port to use to connect to the <br>client machine| &#9745;   |   |
| **connections:** |  how models connect to each other. |  |  |
| `from`  | origin of the connection declared as <br>`<model-name>.<output-name>`. Input names <br>use here must also appear as *inputs* in<br>the models section.   |   |  |
| `to` | destination of the connection declared as <br>`<model-name>.<input-name>`. Output names <br>use here must also appear as *outputs* in <br>the models section. |   | 
| **monitor:**  | 
| `file` | path to a CSV file to store results of <br>the simulation. File will be created if <br>necessary. |  &#9745; | a `out.csv` file saved to <br>the current directory |
|`items` | a list of which inputs, outputs or states <br>of models that most be monitored during <br>runtime. Items must be declared as <br>`<model-name>.<name>`, where *name* is an <br>input, output or stated clared in the <br>*models* section. No duplicated values <br>are allowed  |  |   |

