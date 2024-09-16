import mosaik
import mosaik.util

# Simulation's config (global settings)
SIM_CONFIG: mosaik.SimConfig = {
    'ExampleSim': {
        'python': 'simulator_mosaik:ExampleSimulator',
    },
    'Collector': {
        'cmd': '%(python)s tutorial/collector.py %(addr)s', # %(addr)s will be replaced by host:port and %(python)s by the current python interpreter
    },
}
# Simulation's duration (global settings)
END = 10  # 10 seconds


# world object holds the simulation state

world = mosaik.World(SIM_CONFIG)

## A workflow to run a simulation

# Start simulators
examplesim = world.start('ExampleSim', eid_prefix='MyModel_') # returns model factory
collector = world.start('Collector')

# Instantiate models/ create entities
model = examplesim.ExampleModel(init_val=2)
monitor = collector.Monitor()

# Connection of entities
world.connect(model, monitor, 'val', 'delta') # connect model.val to monitor.val, and model.delta to monitor.delta

# Create more entities
more_models = examplesim.ExampleModel.create(2, init_val=3) # returns list of entities
mosaik.util.connect_many_to_one(world, more_models, monitor, 'val', 'delta')


# Run simulation
world.run(until=END)