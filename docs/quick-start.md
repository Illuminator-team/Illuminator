# Quick Start

The *Illuminator* is written in Python and all its dependencies are also based on Python.

## Installation

**Requirements** 
- Python >= 3.8
- Miniconda (optional)
- A Rasberry Pi cluster (See [cluster set up](cluster-setup.md) for specific instructions)

### Using Pip

You can install the *Illuminator* directly from PYPI:

```shell
pip install illuminator
```

### Using Conda

If you prefer to use conda the `environment.yml` provides all dependecies to create a conda environment called **Ecosystem**.

1. Clone the repository or download the [environment.yml](https://github.com/Illuminator-team/Illuminator/blob/main/environment.yml) file.

2. Use Miniconda to create a new invironment:

```shell
conda env create -f environment.yml

conda activate Ecosystem
```


## From Source

To install the *Illuminator* in from source: 

1. Clone this repository. 

```shell
git clone https://github.com/Illuminator-team/Illuminator.git
```

2. Go to the root of the repository and nstall using `pip`:

```shell
cd Illuminator/

pip install .
```

## Usage

In version 3.0.0 and above, simulation scenarios are configure using `YAML` files with the following structure:

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

To run a simulation scenario, you can use the CLI. On the terminal:

```shell
illuminator <path/to/scenario-config.yaml>
```


## Contact and Support

For more comprehensive support, please contact us at [illuminator@tudelft.nl](mailto:illuminator@tudelft.nl). Additionally, you can reach out to the main contributors for specific inquiries:
* [Dr.ir. Milos Cvetkovic](mailto:M.Cvetkovic@tudelft.nl)
