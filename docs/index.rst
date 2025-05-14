.. Illuminator documentation master file, created by
   sphinx-quickstart on Wed Jul 31 14:38:44 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Illuminator documentation
=========================


TThe Illuminator is a user-friendly development kit for simulating integrated energy systems.
It supports the design of energy systems, the testing of advanced energy management concepts, and the demonstration of challenges posed by the energy transition.
Illuminator builts on `Mosaik. <https://mosaik.offis.de/>`_ and supports both stand-alone simulations and distributed computing.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   quick-start
   .. cluster-setup
   .. user/models

.. toctree::
   :maxdepth: 2
   :caption: Educational tutorials

   tutorials/tutorials-overview.md
   tutorials/tutorial1.md
   tutorials/tutorial2.md
   tutorials/tutorial3.md
   

.. toctree::
   :maxdepth: 3
   :caption: User's Documentation

   user/config-file.md
   user/simulations.md
   references/models.rst

.. toctree::
   :maxdepth: 2
   :caption: Developer's Documentation

   developer/set-up.md
   developer/software-architecture.md
   developer/developer-docstrings.md
   developer/testing-explained.md
   developer/writing-tests.md
   
.. toctree::
   :maxdepth: 2
   :caption: Future Work

   developer/dev-cluster-setup.md
   developer/dev-dashboard.md

.. toctree::
   :maxdepth: 2
   :caption: References

   references/scenario-api.rst
   


Indices and tables
==================

* :ref:`genindex`

.. * :ref:`modindex`
.. * :ref:`search`
