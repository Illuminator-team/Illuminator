"""
A CLI for running simulations in the Illuminator
By: M. Rom & M. Garcia Alvarez
"""

import typer
from typing_extensions import Annotated
import illuminator.engine as engine
from pathlib import Path
# from illuminator.cluster import build_runshfile 
from illuminator.schema.simulation import load_config_file
from illuminator.engine import Simulation

from illuminator.cli import parallel_scenarios
from ruamel.yaml import YAML
from mpi4py import MPI
import os
import psutil # Used for debugging! Remove before PR



APP_NAME = "illuminator"
DEFAULT_PORT = 5123
RUN_PATH = './Desktop/illuminatorclient/configuration/runshfile/'
RUN_MODEL = '/home/illuminator/Desktop/Final_illuminator'
RUN_FILE = 'run.sh'

app = typer.Typer()
scenario_app = typer.Typer()
app.add_typer(scenario_app, name="scenario", help="Run simulation scenarios.")
cluster_app = typer.Typer()
app.add_typer(cluster_app, name="cluster", help="Utilities for a RaspberryPi cluster.")

@scenario_app.command("run")
def scenario_run(config_file: Annotated[str, typer.Argument(help="Path to scenario configuration file.")] = "config.yaml"):
    "Runs a simulation scenario using a YAML file."

    simulation = Simulation(config_file)
    simulation.run()

@scenario_app.command("run_parallel")
def scenario_run_parallel(config_file: Annotated[str, typer.Argument(help="Path to base scenario configuration file.")] = "config.yaml"):
    "Runs a simulation scenario using a YAML file."

    rank = MPI.COMM_WORLD.Get_rank()        # id of the MPI process executing this function
    comm_size = MPI.COMM_WORLD.Get_size()   # number of MPI processes
    print("Hello from rank ", rank)
    print("Rank ", rank, " running on CPU core ", psutil.Process(os.getpid()))
    if rank == 0:
        print("Rank Zero: comm_size is ", comm_size)

    # Load base configuration and remove parallel items
    base_config, removed_items = parallel_scenarios.remove_scenario_parallel_items(config_file)
    
    # Check which type of combination
    align_parameters = base_config.get("scenario", {}).get("align_parameters")
    if align_parameters is None:
        align_parameters = False
        if rank == 0:
            print("Warning: 'align_parameters' is missing in 'scenario'. Setting it to False.")

    # Get list of parallel-item combinations:
    combinations = parallel_scenarios.generate_combinations_from_removed_items(removed_items, align_parameters)
    if rank == 0:
        print("Running ", len(combinations), "different scenarios across ", comm_size, " processes." )

    # Get the rank's subset of the list
    subset = parallel_scenarios.get_list_subset(combinations, rank, comm_size)

    # Split the filename and extension
    cf_base, cf_ext = os.path.splitext(config_file)

    # For each item in the subset:
    # 1. generate scenario
    # 3. overwrite monitor output file (temporary)
    # 2. write scenario to file
    # 3. run simulation
    for s in subset:
        scenario = parallel_scenarios.generate_scenario(base_config, s)
        sim_number = s.get("simulationID")

        # Serialize scenario into yaml file
        scenariofile =  f"{cf_base}_{sim_number}{cf_ext}"
        yaml = YAML()  
        with open(scenariofile, 'w') as f:
            yaml.dump(scenario, f)
        print(f"[Rank {rank}] Wrote scenario {sim_number} to {scenariofile}")

        # Run simulation
        simulation = Simulation(scenariofile)
        simulation.run()
    

@cluster_app.command("build")
def cluster_build(config_file: Annotated[str, typer.Argument(help="Path to scenario configuration file.")] = "config.yaml"):
    """Builds the run.sh files for a cluster of Raspberry Pi's."""
    app_dir = typer.get_app_dir(APP_NAME)
    runsh_path: Path = Path(app_dir) / "runshfile"

    runsh_path.mkdir(parents=True, exist_ok=True)

    output_file = RUN_FILE
    data = load_config_file(config_file)
    
    if data:
        build_runshfile.process_models(data, output_file)
        print(f"Commands have been written to {output_file}")


if __name__ == "__main__":

    # import importlib.util

    # package_spec = importlib.util.find_spec("illuminator.models.Battery")
    # print(package_spec.origin)


    app()