# Simulation Configuration File

Simulation scenarios for the *Illuminator* are defined using configuration files written in YAML. The structure of a configuration must be as in the example below. 

A *simulation file* has four main sections:

- `scenario`: defines metadata and global variable for the simulation.
- `models`: defines which models are included in the simulation.
- `connections`: defines how the models in the `models` section must be connected for a particular simulation.
- `monitor`: defines which inputs, outputs, and states of a particular model must be monitored and logged during simulation. 

## Example 

The following is an example to explain the basic format of a configuration file. 
A description of each keyword and their default values can be found in the table below. 

Optinal keywords can be ommitted, in those cases the defaults will be used. 


```yaml
scenario:
  name: "WindTest" # in mosaik so called world
  start_time: '2012-01-01 00:00:00' # ISO 8601 start time of the simulation
  end_time: '2012-01-01 01:00:00' # ISO 8601 end time of the simulation 
  time_resolution: 900 # time step in seconds (optional). Defaults to 15 minutes (900 s)
models: # list of models for the energy network
- name: CSVB # name for the model (must be unique)
  type: CSV # type of the model registered in the Illuminator
  parameters: # a CSV model must have a start time and a file as its parameters
    start: '2012-01-01 00:00:00' # ISO 8601 start time of the simulation
    file_path: './examples/wind_test.csv' # path to the file with the data
    delimiter: ','
    date_format: 'YYYY-MM-DD HH:mm:ss'

- name: Wind1
  type: Wind # models can reuse the same type
  parameters:
    p_rated: 73548  # Rated power output (kW) of the wind turbine at the rated wind speed and above.
    u_rated: 100  # Rated wind speed (m/s) where the wind turbine reaches its maximum power output.
    u_cutin: 1  # Cut-in wind speed (m/s) below which the wind turbine does not generate power.
    u_cutout: 1000  # Cut-out wind speed (m/s) above which the wind turbine stops generating power to prevent damage.
    cp: 0.40  # Coefficient of performance of the wind turbine, typically around 0.40 and never more than 0.59.
    diameter: 30  # Diameter of the wind turbine rotor (m), used in calculating the swept area for wind power production.
    output_type: 'power'  # Output type of the wind generation, either 'power' (kW) or 'energy' (kWh).
  inputs:
    u: 0  # Wind speed (m/s) at a specific height used to calculate the wind power generation.
  outputs:
    wind_gen: 0  # Generated wind power output (kW) or energy (kWh) based on the chosen output type (power or energy).
    u: 0  # Adjusted wind speed (m/s) at 25m height after converting from the original height (e.g., 100m or 60m).

connections:
- from: CSVB.u
  to: Wind1.u

monitor:
  file: './out_Wind.csv'
  items:
  - Wind1.wind_gen
  - Wind1.u
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

