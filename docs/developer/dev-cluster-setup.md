# Illuminator Cluster Set Up

The Illuminator cluster setup is an optional execution of Illuminator scenarios in different Raspberry Pis. This offers a more hands-on approach to running Illuminator cases with the option to have one or multiple models of a scenario running on different Raspberry Pi devices. The Illuminator Cluster is also used for the [Illuminator Demonstator Kit](https://github.com/Illuminator-team/Illuminator-Demonstrator), a physical setup in which flows and interactions between components of a specific scenario are visualised for educational purposes. 

## Master-Worker Raspberry Pis
For the cluster setup the Raspberry Pis need to be connected to the same network. The master Raspberry pi holds the yaml file of the scenario to be run. It connects to the worker Raspberry Pis through ssh and "tasks" them with running specific models of the scenario. 

![alt text](https://raw.githubusercontent.com/Illuminator-team/Illuminator-Demonstrator/refs/heads/main/figs/image-1.png?token=GHSAT0AAAAAAC4762D6BQXODDXAGXTGH4AY2BDHTVQ)
*Example setup of a Raspberry Pi cluster running the Illuminator*


All Raspberry Pis can run multiple models, specifically they can run one model per available port. 

## Raspberry Pi Setup

The following 2 steps need to be done to all Raspberry Pis, in the future the Install Illuminator step will also be done through the master to make deployment smoother.

### Flash SD card

Install a Raspberry Pi imager and flash the SD card with Raspberry Pi OS.
In the config file of the imager add the following configurations:

| **Parameter** | value |
|:------------:|:-------------:|
| **Username** | your_username |
| **Password** | your_password |
|    **ssh**   |    Enabled    |

Your defined username and password will be needed to connect to the worker Raspberry Pis through your master. Note that the username field is case sensitive.

### Install Illuminator

Clone the github repository by running `git clone https://github.com/Illuminator-team/Illuminator.git`. Enter the Illuminator directory and switch to the cluster branch by running `git checkout cluster`. 

Note that the Illuminator directory needs to have a capital I.

## Master Pi Setup
The following steps are all conducted through the Master Raspberry Pi. First we need to ensure our connection to the worker Raspberry Pis for remote execution of our scripts.

### IP Address Setup

The IPs of all Raspberry Pis need to be static for us to know where to connect. Navigate to the `Illuminator/cluster_setup` directory and run `static_ip.py`. The script will automatically make the device's IP static.

To make the worker Raspberry Pis'IPs static navigate to `Illuminator` dir and edit and run `setup.py`. This script generates keys for ssh connections without needing a password. Make sure your username, password and IPs reflect those of the worker Pis you wish to set up.

### Simulation Preparation

Normally the Illuminator scenarios are defined as yaml files. Similarly, those very same files are used in the cluster setup with some additional steps which allow us to run specific models in the worker Raspberry Pis.

Within your yaml file define the additional fields
```yml
  connect:
    ip: 145.94.213.75 # IP of the worker Pi we want to run this model
    port: 5123 # port of the worker Pi that will run this model
```
To prepare the scenario you wish to run in the cluster run `Illuminator cluster your_scenario.yaml`.

### Simulation Preparation

Execute `run.sh` and run `Illuminator scenario run your_scenario.yaml`.

## Warnings

- Slaves might need to be updated after adding a model.
- Slaves run .sh files to actually start the host (available in Illuminator/configuration/runshfile), if changed/added they need to be made executable through chmod +x <file.sh>.

This section of the documentation is a work in progress, please consult the related guide of the Illuminator Demonstrator Kit repository found [here](https://github.com/Illuminator-team/Illuminator-Demonstrator).

<!-- We are currently working on automating some of the steps to deploy the **Illuminator** on a Raspberry Pi cluster. 
The main idea of this line of development is to simplify the number of steps required to install and enable simulations, after the networking of the cluster is completed. The following are some of the goals we will like to achieve:

1. **Installation:** it shall be possible to install the 'Illuminator' on each *client* and *server* with a single command on the terminal. For example: `pip install illuminator`. This  will remove the burden of copying the source code to to each client and server imposed by the current implementation. Achieving this will make goal (2) more feasible.   
2. **Model accessibility:** it shall be possible for the *server* to run models in any *client* by using the `lxterminal` command, with a command such as:
     `lxterminal -e ssh illuminator@192.168.0.1 'illuminator cluster run <model-name> --remote'`. Where the `--remote` flag must tell *Mosaik* that the simulation will run in a distributed environment (cluster). In the current implementation, one has to specified the path to the Python file containing the model (usually a directoy on the client). However, that is harder to maintain because new versions of the Illuminator rely on the source code and not on Python wheels or TARs. Therefore, the focus here should be on making sure that once the Illuminator is installed to the Python path, then all models are accessible at the OS level and they can be run in *remote* model. 
3. **Business logic for cluster scenarios:** shall develop the business logic to use the information in (`connect`) in the [scenario configuration file](../user/config-file.md) to start simulators on the clienst; such that, for example, calling `illuminator cluster <scenario.yaml>` reads on which client a model should be started, and start the relevant simulators on that client and runs the simulation. -->

:::{note}
The ideas above can be used by contributors to participate in the development of the *Illuminator*. Feedback and solutions are always welcome. Please contact the [Illuminator Development Team](mailto:illuminator@tudelft.nl) if you would like to contribute.
:::