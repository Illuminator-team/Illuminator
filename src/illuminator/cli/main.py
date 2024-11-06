"""
A CLI for running simulations in the Illuminator
By: M. Rom & M. Garcia Alvarez
"""

import typer
from typing_extensions import Annotated
import illuminator.engine as engine


app = typer.Typer()
scenario_app = typer.Typer()
app.add_typer(scenario_app, name="scenario", help="Run simulation scenarios.")
cluster_app = typer.Typer()
app.add_typer(cluster_app, name="cluster", help="Utilities for a RaspberryPi cluster.")


@scenario_app.command("run")
def scenario_run(config: Annotated[str, typer.Argument(help="Path to scenario configuration file.")] = "config.yaml"):
    "Runs a simulation scenario using a YAML file."

    file_path = config

    # load and validate configuration file
    config = engine.validate_config_data(file_path)
    config = engine.apply_default_values(config)

    print("config:  ", config['models'])
    
    # Define the Mosaik simulation configuration
    sim_config = engine.generate_mosaik_configuration(config)
    
    print("mosaik conf:  ", sim_config)

    # simulation time
    _start_time = config['scenario']['start_time']
    _end_time = config['scenario']['end_time']
    _time_resolution = config['scenario']['time_resolution']
    # output file with forecast results
    _results_file = config['scenario']['results']

    # Initialize the Mosaik worlds
    world = engine.create_world(sim_config, time_resolution=_time_resolution)
    # TODO: collectors are also customisable simulators, define in the same way as models.
    # A way to define custom collectors should be provided by the Illuminator.
    collector = world.start('Collector', 
                            time_resolution=_time_resolution, 
                            start_date=_start_time,  
                            results_show={'write2csv':True, 'dashboard_show':False, 
                                          'Finalresults_show':False,'database':False, 'mqtt':False}, 
                            output_file=_results_file)
    
    # initialize monitor
    monitor = collector.Monitor()

    # Dictionary to keep track of created model entities
    model_entities = engine.start_simulators(world, config['models'])

    # Connect the models based on the connections specified in the configuration
    world = engine.build_connections(world, model_entities, config['connections'])

    # Connect monitor
    world = engine.connect_monitor(world, model_entities, monitor, config['monitor'])
    
    # Run the simulation until the specified end time
    mosaik_end_time =  engine.compute_mosaik_end_time(_start_time,
                                            _end_time,
                                            _time_resolution
                                        )

    print(f"Running simulation from")
    world.run(until=mosaik_end_time)


@cluster_app.command("build")
def cluster_build(config: Annotated[str, typer.Argument(help="Path to scenario configuration file.")] = "config.yaml"):
    """Builds the run.sh files for a cluster of Raspberry Pi's."""
    print('building sh')


if __name__ == "__main__":
    app()