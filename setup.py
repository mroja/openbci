"""
A setuptools based setup module for OpenBCI 2.

To develop this package execute 'pip install -e .' command inside this
directory.

See: https://packaging.python.org/en/latest/distributing.html
"""

from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path
import os
import sys
import subprocess


here = path.abspath(path.dirname(__file__))
needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

try:
    version = subprocess.check_output(['git', 'describe', '--tags'], universal_newlines=True).strip()
except Exception:
    version = '0.0.0a0'

setup(
    name='obci',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=version,

    description='OpenBCI 2 EEG acquisition and BCI framework',

    # A boolean (True or False) flag specifying whether the project can be
    # safely installed and run from a zip file. If this argument is not
    # supplied, the bdist_egg command will have to analyze all of your
    # project’s contents for possible problems each time it builds an egg.
    zip_safe=False,

    author='Alex Khrabrov',
    author_email='alex@mroja.net',

    license='GNU General Public License v3 or later (GPLv3+)',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: Qt',
    ],

    # What does your project relate to?
    keywords='bci eeg openbci',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['docs', 'cpp_amplifiers']),

    include_package_data=True,
    exclude_package_data={'': ['.gitignore', '.gitlab-ci.yml'], },

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'pyzmq>=15.4.0',
        'numpy>=1.10.1',
        'protobuf>=3.0.0',
        'twisted>=16.0',  # used in obci/control/launcher/twisted_tcp_handling.py
        'psutil>=3.4.2',  # used in obci/utils/filesystem.py
        'pybluez>=0.22',  # used in obci/drivers/eeg/driver_discovery/amplifier_tmsi_bt_discovery.py
        # python3-pyqt4 Ubuntu deb package doesn't have a .egg-info metadata
        # file so it's impossible for pip to know that it is installed.
        # 'PyQt4',
        # 'sip',
    ],

    # If your project’s tests need one or more additional packages besides
    # those needed to install it, you can use this option to specify them. It
    # should be a string or list of strings specifying what other distributions
    # need to be present for the package’s tests to run. When you run the test
    # command, setuptools will attempt to obtain these (even going so far as to
    # download them using EasyInstall). Note that these required projects will
    # not be installed on the system where the tests are run, but only
    # downloaded to the project’s setup directory if they’re not already
    # installed locally.
    tests_require=[
        'pytest',
        'pytest-cov',
        'pytest-timeout',
        'nose',
    ],

    # A string or list of strings specifying what other distributions need to
    # be present in order for the setup script to run. setuptools will attempt
    # to obtain these (even going so far as to download them using EasyInstall)
    # before processing the rest of the setup script or commands. This argument
    # is needed if you are using distutils extensions as part of your build
    # process; for example, extensions that process setup() arguments and turn
    # them into EGG-INFO metadata files.
    #
    # (Note: projects listed in setup_requires will NOT be automatically
    # installed on the system where the setup script is being run. They
    # are simply downloaded to the ./.eggs directory if they’re not locally
    # available already. If you want them to be installed, as well as being
    # available when the setup script is run, you should add them to
    # install_requires and setup_requires.)
    setup_requires=[] + pytest_runner,

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        # TODO: build_sphinx? make sure these tools are installed properly
        'docs': ['sphinx',
                 'sphinx-autodoc-annotation'],
        # 'dev': ['check-manifest'],
        # 'test': ['coverage'],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={
    #    'obci': ['version.txt'],
    # },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('', [])],

    entry_points={
          'console_scripts': [
              'obci = obci.cmd.obci:run',
              'obci_experiment = obci.cmd.obci_experiment:run',
              'obci_process_supervisor = obci.cmd.obci_process_supervisor:run',
              'obci_server = obci.cmd.obci_server:run',
              'obci_broker = obci.cmd.obci_broker:run',
              'obci_run_peer = obci.cmd.obci_run_peer:run',
          ],
          'gui_scripts': [
              'obci_gui = obci.cmd.obci_gui:run',
          ],
    },
)
