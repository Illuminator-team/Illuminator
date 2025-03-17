# Cluster Set Up

We are currently working on automating some of the steps to deploy the **Illuminator** on a Raspberry Pi cluster. 
The main idea of this line of development is to simplify the number of steps required to install and enable simulations, after the networking of the cluster is completed. The following are some of the goals we will like to achieve:

1. **Installation:** it shall be possible to install the 'Illuminator' on each *client* and *server* with a single command on the terminal. For example: `pip install illuminator`. This  will remove the burden of copying the source code to to each client and server imposed by the current implementation. Achieving this will make goal (2) more feasible.   
2. **Model accessibility:** it shall be possible for the *server* to run models in any *client* by using the `lxterminal` command, with a command such as:
     `lxterminal -e ssh illuminator@192.168.0.1 'illuminator cluster run <model-name> --remote'`. Where the `--remote` flag must tell *Mosaik* that the simulation will run in a distributed environment (cluster). In the current implementation, one has to specified the path to the Python file containing the model (usually a directoy on the client). However, that is harder to maintain because new versions of the Illuminator rely on the source code and not on Python wheels or TARs. Therefore, the focus here should be on making sure that once the Illuminator is installed to the Python path, then all models are accessible at the OS level and they can be run in *remote* model. 
3. **Business logic for cluster scenarios:** shall develop the business logic to use the information in (`connect`) in the [scenario configuration file](../user/config-file.md) to start simulators on the clienst; such that, for example, calling `illuminator cluster <scenario.yaml>` reads on which client a model should be started, and start the relevant simulators on that client and runs the simulation.

:::{note}
The ideas above can be used by contributors to participate in the development of the *Illuminator*. Feedback and solutions are always welcome. Please contact the [Illuminator Development Team](mailto:illuminator@tudelft.nl) if you would like to contribute.
:::