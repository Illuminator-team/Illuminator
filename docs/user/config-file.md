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
| **scenario:** | a set of global values for a simulation. |  |  |
|`name` | A name for the simulation, internally this name will be asssigned to what the Mosaik World created during runtime. |  |  |
| `start_time` | start time for the simulation. Must be a timestamp in ISO 8601 format |  |  |
| `end_time` | end time for the simulation. Must be a timestamp in ISO 8601 format.  |  |  |
| `time_resolution` | number of seconds between simulation steps | &#9745; | 900 (15 min)
| **models:** | a list of models for the simulation | |  |
|  `name` | a name for the model. Must be unique for each simulation |  |   |
| `type`  | type of model. This must correspond with the name of the model registered in the Illuminator. | |  |
| `inputs`  | a set of input-names and initial values for the model. The model type determines which names and values are applicable to each model, and they must be declared accordingly. Inputs are optional | | If the value is set to `null`, the default value will be used. See the respective model type for details.|
| `outputs` | a set of output-names and initial values for the model. Similar to *inputs* valid names and values for each model are determined by the model *type*. See the respective model type for details. | | If the value is set to `null`, the default value will be used. |
| `parameters`  | a set of name-value pairs for the model. Parameters declared constants for a model during runtime. | &#9745; | If ommited, the default values will be used. See the respective model type for details. |
| `states` | a set of name-value pairs considered as states for the model. The values modify the internal initial values of a state. | &#9745; | If ommited, the default values will be used. See the respective model type for details. |
| `triggers` | names of inputs, output or states that are use as triggers for a particular model. Triggers can only be declared by models that implement the *event-based paradigm*. See the respective model type to know if it accepts triggers. |  &#9745; | |
| `connect` | to declare in which client a model runs when using a Raspberry Pi cluster. | &#9745;  | |
| `ip` | Ip of the client manchine that will run the model. Only IP version 4 format. |  |   |
| `port` | TCP port to use to connect to the client machine| &#9745;   |   |
| **connections:** |  how models connect to each other. |  |  |
| `from`  | origin of the connection declared as `<model-name>.<output-name>`. Input names use here must also appear as *inputs* in the models section.   |   |  |
| `to` | destination of the connection declared as `<model-name>.<input-name>`. Output names use here must also appear as *outputs* in the models section. |   | 
| **monitor:**  | 
| `file` | path to a CSV file to store results of the simulation. File will be created if necessary. |  &#9745; | a `out.csv` file saved to the current directory |
|`items` | a list of which inputs, outputs or states of models that most be monitored during runtime. Items must be declared as `<model-name>.<name>`, where *name* is an input, output or stated clared in the *models* section. No duplicated values are allowed  |  |   |

