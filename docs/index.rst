.. obci documentation master file, created by sphinx-quickstart.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to OpenBCI 2 documentation!
===================================

Welcome to the `OpenBCI`_ framework.

This documentation is written as a part of Alex Khrabrov's Google Summer of Code 2016 project.

This file contains documentation generated from whole OpenBCI project. Because most of OpenBCI's code is undocumented only following modules, written during GSoC, have proper documentation:

* :mod:`obci.core`
* :mod:`obci.peers`
* :mod:`obci.utils.zmq`
* :mod:`obci.utils.debug`
* :mod:`obci.utils.signal_generators`

.. _OpenBCI: https://github.com/BrainTech/openbci

OpenBCI 2 API
-------------

.. toctree::
   :maxdepth: 3
   :titlesonly:

   apidoc/modules

Glossary
--------

Useful terms for easy understanding of the documentation:

**peer**
    An OpenBCI module (most probably a Python program or module) which communicates with other running modules through the network. Typical examples: eeg signal amplifiers, filters, signal displays.

(helper) **module**
    A module which is not a peer. Helper modules are not explicitly mentioned in OpenBCI launch/configuration files because they are components of the peers.

**peer config file**, configuration file
    Text configuration file (of a peer). Stores necessary parameters and defines dependencies on other peers in the system.

**experiment**, OpenBCI instance, system instance
    A set of running OpenBCI peers. Each peer can be identified by its assigned peer_id, thus allowing for launching multiple instances of the same programs. Peer_ids, peer program paths and peer configurations are predefined in *launch files*.

**launch file**, experiment definition file/scenario
    Text file for defining an experiment. It contains paths to programs to be executed (peers),
    assignments of peer_id and paths to peer configurations.

Obsolete documentation
----------------------

Following tutorial is obsolete, but still can be useful for understanding OpenBCI 2 internals:

:doc:`Peer configuration tutorial<configuration/tutorial>`


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

