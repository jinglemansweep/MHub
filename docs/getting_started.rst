Getting Started
===============

Download
--------

Clone (or fork) the `MHub repository over at GitHub <http://github.com/jingleman/MHub>`_::

  $ git clone git://github.com/jingleman/MHub.git

Developers
----------

For development, it is advisable to install MHub within a `virtualenv <http://pypi.python.org/pypi/virtualenv>`_.
Also, `virtualenvwrapper <http://www.doughellmann.com/projects/virtualenvwrapper/>`_ is recommended for managing Python
virtual environments.

Once installed, create a Python (2.x) virtual environment::

  $ mkvirtualenv --no-site-packages mhub
  $ workon mhub

Navigate to your project checkout destination::

  $ cd MHub

Now, install the requirements. If you intend to try out all the included plugins, we recommend using the full
requirements file.

Install core dependencies only::

  $ pip install -r requirements.txt

Install all dependencies (for plugin support)::

  $ pip install -r requirements-full.txt

Testing The Installation
------------------------

Launch MHub using the ``twistd`` daemon command::

  $ cd mhub
  $ twistd -y run.py -n

You should see output similar to::

  $ twistd -n -y run.py
  2011-11-07 22:28:41,616 INFO [app.app] Registering plugins
  2011-11-07 22:28:41+0000 [-] Log opened.
  2011-11-07 22:28:41+0000 [-] twistd 11.0.0 (/home/louis/.virtualenvs/mhub/bin/python2.7 2.7.2) starting up.
  2011-11-07 22:28:41+0000 [-] reactor class: twisted.internet.selectreactor.SelectReactor.

To exit, simply press CTRL + C to end the process.

Configuration
-------------

On first startup, MHub creates default configuration files in the standard XDG home locations. This will be
``~/.config/mhub`` on Linux. There are two main configuration files, one for general settings (``app.yml``) and one
for enabling/configuring the available plugins (``plugins.yml``).
