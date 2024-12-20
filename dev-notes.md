# Dev Notes


## Source code

Most of the source code is `configuration/` directory.

## Configuration of simulation case

* The `config.xml` file serves as a reference matrix, providing Mosaik with essential information about each simulator
involved in the study case. This includes details such as the simulator’s name, programming language, and specific
location. By leveraging this file, the platform can accurately identify and incorporate the necessary simulators into
the study case.

* The `connection.xml` file defines the interconnections between the different instances of the models whithin the study case. It presents a matrix format that specifies the sender and receiver names, as well as the attributes being
sent and received. This connection matrix, utilized in the Main file, assists in determining the number of entities for
each simulator and it is used to correctly call the Mosaik Scenario function `connect()`, which informs the engine of
the topology of the studycase.

* The `buildmodelset.py` file holds the parameters for each simulator. It is imported into the Main file and used to
instantiate the models with the appropriate setup. This file allows for the specification of various parameters related
to physical energy assets, like the initial SoC of batteries or the rated power of wind turbines. Additionally, economic
parameters, such as the marginal cost or benefit of each asset in agents’ portfolios, can also be defined among the
available parameters.

## Power Point as GUI

While the configuration and connection matrix can be directly written in Python files, the platform goes a step further by incorporating a
user-friendly approach inherited from The Illuminator. This approach allows users to define their simulation cases by
visually drawing them in an online workspace or using tools like PowerPoint.
The translation of these visual representations into the necessary XML format is achieved through the `readppt.py`

The `configuration/readppt_connectionxml.py` is an example of how `.pptx` files are converted to XML configuration files.


## Mosaik

Modeling or composing a scenario in mosaik comprises three steps:

1. starting simulators,
2. instantiating models within the simulators, and
3. connecting the model instances of different simulators to establish the data flow between them.


### 1. Starting simulators

`sim config` is a dict that contains every simulator we want to use together with some information on how to start it.

### 2.  Instantiating modesl within simulators

Creates model instaces

### 3. Connecting models instances