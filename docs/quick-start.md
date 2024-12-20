# Quick Start

The *Illuminator* is written in Python and its dependencies are also Python.

## Installation

**Requirements** 
- Python >= 3.8
- Miniconda (optional)
- A Rasberry Pi cluster, for cluster deplyment ( [cluster set up](cluster-setup.md) for specific instructions)

### Using Pip

The simpliest way to install *Illuminator* is from PYPI, using `pip`:

```shell
pip install illuminator
```

### Using Conda

If you prefer to use conda the `environment.yml` provides all dependecies to create a conda environment called **illuminator**.

1. Clone the repository or download the [environment.yml](https://github.com/Illuminator-team/Illuminator/blob/main/environment.yml) file.

2. Use Miniconda to create a new invironment:

```shell
conda env create -f environment.yml

conda activate illuminator
```

## From Source

To install the *Illuminator* from source: 

1. Clone the repository. 

```shell
git clone https://github.com/Illuminator-team/Illuminator.git
```

2. Go to the root of the repository and install it using `pip`:

```shell
cd Illuminator/

pip install .
```

## Usage

In version 3.0.0 and above, simulation scenarios are configure using `YAML` files. 

### Simulation file

Simulations are declared using a configulation file that must have the structure below. Refer to  [simulation file](./user/config-file.md) for a full explanation. 

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

The illuminator has two interfaces for user, one for the command line (CLI) and one for Python:


1. To run a simulation **scenario* using the CLI, use the following:

  ```shell
  # to run a simulation scenario:
  illuminator scenario <path/to/scenario-config.yaml>

  # to get help, use:
  illuminator scenario --help
  ```

2. If using Python:

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
