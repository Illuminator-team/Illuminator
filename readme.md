[![License: GPL v2](https://img.shields.io/badge/License-GPL_v2.1-blue.svg)](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html)
[![documentation](https://github.com/Illuminator-team/Illuminator/actions/workflows/deploy-docs.yml/badge.svg)](https://github.com/Illuminator-team/Illuminator/actions/workflows/deploy-docs.yml)

# Illuminator
The Illuminator is an easy-to-use Energy System Integration 
Development kit to demystify energy system's operation, illustrate challenges 
that arise due to the energy transition and test 
state-of-the-art energy management concepts. 
The kit utilises Raspberry Pi's as individual components of an energy system emulator, 
and the simulation engine is based on [Mosaik](https://mosaik.offis.de/).

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

The `environment.yml` provides all dependecies to create a conda environment called **illuminator**.

```shell
conda env create -f environment.yml

conda activate illuminator
```

> Refer to the [documenation](https://illuminator-team.github.io/Illuminator/quick-start.html#usage) for an explanation on how to set up and run a simulation.


## Raspberry Pi Setup

The setup for the Illuminator requires one **server** Raspberry Pi and several **clients** Raspberry Pi's.
Raspberry Pi's must be connected and configured as a local network, and the
*server* must be configured to have permissions to access and control the *clients* through Secure Shell Protocol (SSH).

During simulation, the *server* engage with the *clients* to run the simulations defined in the *simulation configuration*, and
information is exchanged between Rasberry Pi's using network sockets.
The **server** provides a Dashboard to viazulize the results, and saves them to a `.csv` files for later analysis. 

<div align="center">
	<img align="center" src="docs/_static/img/Structure.jpg" width="500">
</div>


### Set up 

Consult the [Cluster Pi Setup](docs/cluster-setup.md) document for instructions on how to set up a cluster.

## Contributing Guidelines

The Illuminator team accepts contributions to the Illuminator source, test files, documentation, and other materials distributed with the program. To contribute read our [guidelines](CONTRIBUTING.md)

## License 
Illuminator is available under a GNU Lesser General Public License (LGPL).
The Illuminator team does not take responsibility for any damage or loss derive from using this sourcecode.

## Citation
Please cite this software as follows:

*A. Fu, R. Saini, R. Koornneef, A. van der Meer, P. Palensky and M. Cvetković, "The Illuminator: An Open Source Energy System Integration Development Kit," 2023 IEEE Belgrade PowerTech, Belgrade, Serbia, 2023, pp. 01-05, doi: 10.1109/PowerTech55446.2023.10202816.*

### Contributors

Many people have contributed to the development of *Illuminator*, we list their names and contributions below:

| [Role](https://credit.niso.org/contributor-roles-defined/) | Contributor |
|------|--------|
| Conceptualization | A. Fu, A. Neagu, M. Cvetkovic, M. Garcia Alvarez, M. Rom |
| Funding acquisition | A. Fu, M. Cvetkovic,  P. Palensky |
| Project management | A. Neagu, M. Cvetkovic  |
| Research |A. Fu, M. Cvetkovic,  N. Balassi, R. Saini, S.K. Trichy Siva Raman |
| Resources | R. Koornneef |
| Software | A. Fu, J. Grguric, J. Pijpker, M. Garcia Alvarez,  M. Rom., D. Georgiadi,  J. Groen |
| Supervision |  A. Neagu, M. Cvetkovic |

## Acknowledgements

The Illuminator team extends its sincere gratitude for the invaluable support and contributions from our dedicated members:

- **Aihui Fu**, who played a pivotal role as the main developer for both Versions 1.0 and 2.0.
- **Remko Koornneef**, whose expertise in hardware development has been instrumental.
- **Siva Kaviya**, for her significant contributions to the development of the initial version.
- **Raghav Saini**, for his substantial involvement in developing the models for Version 1.0.
- **Niki Balassi**, for his crucial role in advancing the multi-energy system models in Version 2.0.

Each of these individuals has been essential in shaping the success and evolution of our project. We are profoundly thankful for their dedication and expertise.

* The Illuminator project is supported by [TU Delft PowerWeb](https://www.tudelft.nl/powerweb) and [Stichting 3E](https://www.stichting3e.nl/).
* The development of the *Illuminator* was supported by the [Digital Competence Centre](https://dcc.tudelft.nl), Delft University of Technology.


## Contact and Support

For more comprehensive support, please contact us at [illuminator@tudelft.nl](mailto:illuminator@tudelft.nl). Additionally, you can reach out to the main contributors for specific inquiries:
* [Dr.ir. Milos Cvetkovic](mailto:M.Cvetkovic@tudelft.nl)
