.. Illuminator documentation master file, created by
   sphinx-quickstart on Wed Jul 31 14:38:44 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Illuminator documentation
=========================


The Illuminator is an easy-to-use Energy System Integration 
Development kit to demystify energy system operation, illustrate challenges 
that arise due to the energy transition and test 
state-of-the-art energy management concepts. we utilise Raspberry Pis
as the individual components of the energy system emulator, 
and the simulation engine is based on `Mosaik. <https://mosaik.offis.de/>`_

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   quick-start
   .. cluster-setup
   .. user/models

.. toctree::
   :maxdepth: 2
   :caption: User's Documentation

   user/config-file.md
   user/simulations.md
   references/models.rst

.. toctree::
   :maxdepth: 2
   :caption: Tutorials

   tutorials/tutorials-overview.md
   tutorials/tutorial1.md
   tutorials/tutorial2.md
   tutorials/tutorial3.md

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
