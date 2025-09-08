# Quick Start

The *Illuminator* is written in Python and its dependencies are also Python.

## Installation

**Requirements** 
- Python >= 3.11 < 3.12
- (optional) A Rasberry Pi cluster, for cluster deployment ( see [cluster set up](cluster-setup.md) for specific instructions)

## Installing the Package Release (Recommended for End-Users)

The simplest way to install *Illuminator* is from PYPI, using `pip`:

```shell
pip install illuminator
```
## Installing from Source (for Developers)

### 1. Create an environment
Create a new environment called *illuminator_env*:
```shell
Python -m venv illuminator_env
```

### 2. Activate the environment
- For linux/macOS:
```shell
Source illuminator_env/bin/activate
```
- For Windows (Command Prompt):
```shell
Illuminator_env\Scripts\activate
```
### 3. Clone the repository
```shell
git clone https://github.com/Illuminator-team/Illuminator.git
```
Navigate to the repository root and install with pip:

```shell
cd Illuminator/
pip install -e .
```
This creates an editable install, essential if you wish to modify the source code and allow edits without reinstalling.

## Usage

In version 3.0.0 and above, simulation scenarios are configured using `YAML` files. 

### Simulation file

Simulations are set up using a configuration file that must have the structure below. See [simulation file](./user/config-file.md) for a full explanation. 

```yaml
# config.yaml
scenario:
  name: "AddingNumbers" # a name for the simulation scenario
  start_time: '2012-01-02 00:00:00' # ISO 8601 start time for simulation
  end_time: '2012-01-02 00:00:10' 
  time_resolution: 900 # time step in seconds. Defaults to 15 minutes (900 s)
models: # list of models for the simulation
- name: Model1 # name for the model in the simulation (must be unique)
  type: MyModel # name of the type of model (must match the name of an existing model)
  inputs:  # list of initial values for the inputs of the model type
    # input names are defined by the model type
    in1: 10  # input-name: initial value, default values will be used if not set. 
    in2: 20
  outputs: 
    out1: 0 
  parameters: 
    param1: "adding tens"
- name: Model2
  type: MyModel # models can reuse the same type
  inputs: 
    in1: 100  
    in2: 200
  parameters: 
    param1: "adding hundreds"
connections:
- from: Adder1.out1 # origin model, format: <model_name>.<output>
  to: Adder2.in1 # destination model, format: <model_name>.<input>
monitor:  # a list of models, its inputs, output and states to be monitored and logged
- Adder2.out2 # format: <model_name>.<input>/<output>/<states>
```

### Running Simulations

The illuminator has two interfaces for a user, one for the command line (CLI) and one for Python:

1. To run a simulation **scenario* using the CLI, use the following:

  ```shell
  # to run a simulation scenario:
  illuminator scenario run <path/to/scenario-config.yaml>

  # to get help, use:
  illuminator scenario --help
  ```

2. Using a Python script:

  ```python

  from illuminator.engine import Simulation

  sim = Simulation('<path/to/scenario-config.yaml>')
  sim.run()
  ```

## Contact and Support

For more comprehensive support, please contact us at [illuminator@tudelft.nl](mailto:illuminator@tudelft.nl). Additionally, you can reach out to the main contributors for specific inquiries:
* [Dr.ir. Milos Cvetkovic](mailto:M.Cvetkovic@tudelft.nl)
* [Despoina Geordiadi](https://github.com/Eutardigrada)
* [Jort Groen](https://github.com/JortGroen)
