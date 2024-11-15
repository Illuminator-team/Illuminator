# Simulations

Simulations can be directly from Python or suing the *command line interface* (CLI).

## Python Interface

To run a simulation from Python, you need to provide a [configuration file](./config-file.md). Then you can start the simulation as follows:

```python
from illuminator.engine import Simulation

simulation = Simulation('<path/to/config.yaml>')
simulation.run()

```

## CLI

You can use the commands `scenario run` to start a simulation from the terminal:


```shell
illuminator scenario run <path/to/config.yaml>
```
