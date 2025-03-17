# Running Simulations

Simulations can be directly run in a python script or using the *command line interface* (CLI).

## Python Script

To run a simulation from Python, you need to provide a [configuration file](./config-file.md). Then you can start the simulation as follows:

```python
from illuminator.engine import Simulation

simulation = Simulation('<path/to/config.yaml>')
simulation.run()

```

## Command Line

You can use the command `scenario run` to start a simulation from the terminal:

```shell
illuminator scenario run <path/to/config.yaml>
```
