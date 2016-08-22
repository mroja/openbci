# OpenBCI 2 framework

This branch contains my final contribution for Google Summer of Code 2016.

This version of OpenBCI requires Python 3.5.1+ and PyZmq 15.4+. It will not work with older versions.

Following things were implemented during GSoC:
 
 * new OpenBCI 2 Core Communication Layer written using PyZmq
 * reduced OpenBCI 1 to minimal codeset:
 * removed a lot of unmaintained peers
  * removed lots of unused legacy code
  * removed dependency on `scipy`, `matplotlib` and `decorator` packages
  * removed dependency on `azouk` and `multiplexer` Python modules (replaced with `obci.mx_legacy`)
 * ported code from Python 2 to Python 3.5
 * automated testing by tidying up existing and introducing new unit tests:
  * total code coverage is now 37%
  * code coverage for new code, written during GSoC 2016, is about 90%
 * installation, testing and development can be done using standard `setup.py` instead of purely written custom scripts
 * OpenBCI 2 can now be installed and developed on Windows without MinGW environment
 * all OpenBCI 2 source code in pycodestyle (PEP-8) compliant now
 * new code is extensively documented - https://mroja.github.io/openbci-docs/

But as always there is still some work to be done:

 * port binary amplifiers to use the new ZMQ-based peer messaging layer
 * finish writing `obci.mx_legacy.clients` legacy wrapper
 * finish porting `obci_gui` to Windows (currently GUI start, but there are some errors left)
 * documentation of existing code

Packages for 64-bit Python for Ubuntu 16.04 and Windows can be downloaded from https://github.com/mroja/openbci/releases/tag/2.0.0.

### Documentation

https://mroja.github.io/openbci-docs/

### Original OpenBCI 1 framework description

OpenBCI is a platform for Brain Computer Interfaces. This software contains tools which allow you to build a complete Brain Computer Interface based on EEG, and perform some experiments collecting EEG and other biomedical data signals.

These tools are:

 * tools for communication with some EEG hardware (TMSi, Braintronics, and openEEG)
 * tools for displaying and storing the EEG (and other biomedical time series) signal
 * tools for creating "bindings" or "use scenarios" for some 3rd party software for performing psychological experiments (e-prime, psychopy, visionEGG). This means, that if you prepare an experiment in some of mentioned software, you will be able to perform this experiment, and store the EEG data, with necessary tags using OpenBCI.
 
# Running from source

Download OpenBCI source code and checkout `gsoc2016` branch:

```
$ cd ~
$ sudo apt-get -qq -y install git python3-pip
$ git clone https://github.com/mroja/openbci.git
$ cd openbci
$ git checkout gsoc2016
$ pip3 install --user -e .
```

After following programs should be available from command line:
 * <code>obci</code> - main OpenBCI script
 * <code>obci_gui</code> - OpenBCI scenario selector GUI

### Run tests

    $ sudo apt-get -qq -y install libbluetooth-dev python3-pip python3-pytest python3-setuptools python3-pyqt4 python3-twisted python3-numpy
    $ pip3 install pyzmq protobuf pybluez psutil
    $ python3 setup.py test

### Build packages
    
    $ git clean -xdf
    $ sudo apt-get -qq -y install git debhelper sed equivs chrpath python3-all python3-pip
    $ sudo apt-get -qq -y install python-dev
    $ pip3 install stdeb
    $ ./debbuildobci.sh

### Building documentation

To be able to generate documentation install (on Ubuntu):

    $ sudo apt-get -qq -y install python3-sphinx

To build the *.rst files, from the openbci directory run:

    $ sphinx-apidoc -o docs/apidoc obci

Then generate documentation:

    $ python3 setup.py build_sphinx

# License

OpenBCI is licensed under the terms of the GNU GPL version 3.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
