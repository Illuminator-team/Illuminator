## What does the illuminator do? 

The Illuminator is a user-friendly development kit for simulating integrated energy systems. It supports the design of energy systems, the testing of advanced energy management concepts, and the demonstration of challenges posed by the energy transition. Illuminator builts on [Mosaik](https://mosaik.offis.de/). and supports both stand-alone simulations and distributed computing.

### Practical Examples
To simplify the multiple possible functionalities, there are three go-to applications for the Illuminator that might help the user to have a clearer overview: 
- Power Balancing (Selecting a viable portfolio of renewable generation to match an electricity demand)
- Simulation of electricity markets (Obtaining clearing prices, demand and supply bid functions)
- Simulation of electricity grids

Three {doc}`tutorials <tutorials/tutorials-overview>` are available to get acquainted with these examples.  

## How does it work ?
To better visualize the illuminator as a virtual instrument, some typical inputs and outputs examples can be generalized as follows:

```mermaid
flowchart LR

id1>Illuminator]

A@{ shape: lean-r, label: "load data per hour" }
B@{ shape: lean-r, label: "Solar and wind meteorological data" }
C@{ shape: lean-r, label: "portfolio of companies in market" }
D@{ shape: lean-r, label: "grid connection data" }

E@{ shape: doc, label: "load plots" }
F@{ shape: doc, label: "generation plots" }
G@{ shape: doc, label: "simulation plots" }
H@{ shape: doc, label: "market clearing plots" }

A e1@==>id1 e5@==> E
B e2@==>id1 e6@==> F
C e3@==>id1 e7@==> G
D e4@==>id1 e8@==> H

e1@{ animate: true }
e2@{ animate: true }
e3@{ animate: true }
e4@{ animate: true }
e5@{ animate: true }
e6@{ animate: true }
e7@{ animate: true }
e8@{ animate: true }
```

To simulate the different components of the applications a number of elements are simulated through {doc}`models <references/models>`, namely: batteries, PV panels, wind turbines,  controllers, company portfolios, loads etc. A series of connections between these models create different simulations depending on the interactions between said models, and can be modified to create more complex simulations.

## Prior Knowledge 
Designed for versatility, the Illuminator adapts to diverse applications; therefore, the prior knowledge required depends on the intended use (for a wide range of users). To {doc}`get started <quick-start>` as a basic end user the following will suffice:  
- basic understanding of energy systems relevant parameters and interactions (ex. rated power of wind turbines, concept of a load, dynamics of an energy market)
- basic understanding of the Illuminator's commands from the tutorials
