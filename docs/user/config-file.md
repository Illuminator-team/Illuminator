# Simulation Configuration File

Simulation scenarios for the *Illuminator* are define using configuration files written in YAML. The structure of a configuration must be as in the example below. 

A *simulation file* has four main sections:

- `scenario`: defines metadata and global variable for the simulation.
- `models`: defines which models are included in the simulation.
- `connections`: defines how the models in the `models` section must be connected for a particular simulation.
- `monitor`: defines which inputs, outputs, and states of a particular model must be monitored and logged during simulation. These are consider the simulation results and they will be saved to the file in `results`.

## Example 

See the table below a description of each keyword and their default values. Optinal keywords can be ommitted, in those case the defaults will be used.


```yaml
scenario:
  name: "ExampleScenario" # a name for the simulation
  start_time: '2012-01-02 00:00:00' # start and end times of the simulation
  end_time: '2012-01-02 00:00:10' 
  time_resolution: 900 # duration of each step in second
  results: './out.csv' #  a file to store the results (optional)
models: # list of models for the energy network
- name: Battery1 # name for the model (must be unique)
  type: Battery # name of the model registered in the Illuminator
  inputs: 
    input1: 0  # input-name: initial value, default value will be used if not declaredd
  outputs: 
    output1: 0 
    output2: null
  parameters: 
    charge_power_max: 100
    discharge_power_max: 200
    soc_min: 0.1 
    soc_max: 0.9 
    capacity: 1000
  states: 
    initial_soc: 0.5
  triggers:   # list of triggers for the of another model??. It must be an input, output or state of the model
    - capacity
    - soc_min
  scenario_data: './src/illuminator/schemas/scenario_data.csv' #path to the scenario data file for the model. This should be optional
  connect: # this is optional. If not defined, the model will be assumed to be local
    ip: 127.0.0.1 # Ip version 4
    port: 5000 # optional, if not defined, the default port will be used
- name: Battery2
  type: Battery # models can reuse the same type
  inputs: 
    input1: 0  # input-name: initial value, default value will be used if not defined
  outputs: 
    output1: 0 
    output2: null
  parameters: 
    charge_power_max: 100
  states: 
    soc: 0.5  # initial value for the state, optional
- name: PV1
  type: PVModel
  inputs: 
    input1: 0  # input-name: initial value, default value will be used if not defined
    input2: 0
  outputs: 
    output1: 0 
  parameters: 
    power_max: 100
  states: 
    initial_soc: 0.5
connections:
- from: Battery1.output2 # start model, pattern: model_name.output_name/input_name
  to: PV1.input1 # end model
- from: Battery2.output
  to: PV1.input2
monitor:  # a list of models, its inputs, output and states to be monitored and logged
- Battery1.input1 # pattern model_name.state_name
- Battery2.output1  # no duplicates allowed
- PV1.soc # pattern model_name.state_name
- PV1.output1
```


| Keyword | Description | Optional | Default |
|---------|-------------|----------|---------|
| **scenario:** | a set of global values for a simulation. |  |  |
|`name` | A name for the simulation, internally this name will be asssigned to what the Mosaik World created during runtime. |  |  |
| `start_time` | start time for the simulation. Must be a timestamp in ISO 8601 format |  |  |
| `end_time` | end time for the simulation. Must be a timestamp in ISO 8601 format.  |  |  |
| `time_resolution` | number of seconds between simulation steps | &#9745; | 900 (15 min)
| `results` | path to a CSV file to store the results of the simulation. The values in the `monitor` section determine which values are saved as results.|  &#9745; | a `out.csv` file saved to the current directory |
| **models:** | a list of models for the simulation | |  |
|  `name` | a name for the model. Must be unique in each simulation |  |   |
| `type`  | type of model. This must correspond with the name of the model registered in the Illuminator. | |  |
| `inputs`  | a set of input-names and initial values for the model. The model types determine which names and values are applicable to each model, and they must be declared accordingly. At least one input per model must be declared | | If the value is set to `null`, the default value will be used. See the respective model type for details.|
| `outputs` | a set of output-names and initial values for the model. Similar to *inputs* valid names and values for each model are determined by the model *type*. See the respective model type for details. | | If the value is set to `null`, the default value will be used. |
| `parameters`  | a set of name-value pairs for the model. Parameters declared constants for a model during runtime. | &#9745; | If ommited, the default values will be used. See the respective model type for details. |
| `states` | a set of name-value pairs considered as states for the model. Values allow to modify the internal initial values of a state. | &#9745; | If ommited, the default values will be used. See the respective model type for details. |
| `triggers` | names of inputs, output or states that are use as triggers for a particular model. Triggers can only be declaredd by models that implement the *event-based paradigm*. See the respective model type to know if it accepts triggers. |  &#9745; | |
| **connections:** |  how models connect to each other. |  |  |
| `from`  | origin of the connection declared as `<model-name>.<output-name>`. Input names use here must also appear as *inputs* in the models section.   |   |  |
| `to` | destination of the connection declared as `<model-name>.<input-name>`. Output names use here must also appear as *outputs* in the models section. |   | 
| **monitor:**  | a list of which inputs, outputs or states of the modles must be monitored and logged during runtime. These are consired *results* of the simulation and they will be saved to the file in `results`. Items must be declared as `<model-name>.<name>`, where *name* is an input, output or stated clared int the *models* section. No duplicated values are allowed  |  |   |
