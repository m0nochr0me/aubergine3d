Aubergine3D
===========

Simple control software for DLP/DUP 3Dprinter.

Reuirements
-----------
 - python3
 - python3-tk
 - pipenv

Installation
------------

Install ``pipenv``:

Ubuntu 17.10::

    $ sudo apt install software-properties-common python-software-properties
    $ sudo add-apt-repository ppa:pypa/ppa
    $ sudo apt update
    $ sudo apt install pipenv

Archlinux::

    $ sudo pacman -Sy python-pipenv

Distribution independent::

    $ sudo pip install pipenv

You probably need to add your user to the following groups: ``uucp``, ``dialout``, ``tty``::

    $ sudo usermod -a -G uucp *username*
    $ sudo usermod -a -G tty *username*
    $ sudo usermod -a -G dialout *username*

Install::

    $ git clone https://bitbucket.org/m0nochr0me/aubergine3d.git
    $ cd aubergine3d
    $ pipenv --python 3
    $ pipenv install ewmh pyserial natsort screeninfo

Usage
-----

Run::

    $ chmod +x aubergine3d.sh
    $ aubergine3d.sh

Connect, load job and start print::

    > connect
    > load <filename>.txz
    > start

Job files can be prepared with `stlslice <https://bitbucket.org/m0nochr0me/stlslice>`_

Notice
------
| This software is poorly written, so it may cause severe mental pain or make your eyes bleed if you look at its code.
| You've been warned.
