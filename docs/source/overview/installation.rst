.. _installation:

Installation
=============

.. note::

    This page is intended for those who wish to install their own local copy
    of voeventdb. If you just want to query our copy of the database, things
    are much simpler - see :ref:`getting_started`.

All-in-one installation scripts for the DevOps_ enthusiast
----------------------------------------------------------------------------------------------------

.. _DevOps: https://en.wikipedia.org/wiki/DevOps

If you'd like to install your own copy of voeventdb, you may be
interested in the accompanying
`Ansible <http://www.ansible.com/configuration-management>`_
`role <http://docs.ansible.com/ansible/playbooks_roles.html>`_ that
provides a pre-configured installation of the voeventdb database and
REST API, optionally served via Apache, available here:
https://github.com/timstaley/ansible-voeventdb.

The voeventdb role is demonstrated in conjunction with another role
installing the `Comet <http://comet.readthedocs.org/>`_ broker (to pull
in the latest VOEvent packets) here:
https://github.com/4pisky/voeventdb-deploy - in fact, those are the
scripts which build http://voeventdb.4pisky.org/.

Note that, at time of writing, I've not had time to document these
packages much - if you'd be interested in making use of them please drop
me a line and I may be able to provide help / improve the associated
docs.

Development installation
------------------------

Alternately, if you want a local installation for development and
testing purposes (or you just prefer the hands-on approach) then read on
for some tips regarding manual installation.

Postgres Database Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Before the unit-tests or database setup will run, we need a
`PostgreSQL <http://www.postgresql.org/>`_ installation, and a database
login with createdb rights. On a typical Debian system, install postgres
with something like:

::

    sudo apt-get install libpq-dev postgresql-9.3 postgresql-server-dev-9.3

You can check if you have database login and creation rights by running
e.g.

::

    createdb

Which will attempt to create a database named after your username. On a
fresh Postgres installation you will get an access rights error - you
need to login and create your user like so:

::

    userfoo@machine: sudo su postgres
    postgres@machine: psql
    postgres=# create user userfoo with superuser;
    postgres=# alter user userfoo with password 'userfoo';

For full details, consult the `postgres
docs <http://www.postgresql.org/docs/9.3/interactive/tutorial-createdb.html>`_.

Note the unit-tests assume by default a database username/password which
are both the same as your login username, but this can be easily changed, see the
module
`voeventdb.server.database.config <https://github.com/timstaley/voeventdb/blob/master/voeventdb/server/database/config.py#L11>`_.

A final word on Postgres setup - I recommend setting

::

    timezone = 'UTC'

in *postgresql.conf*, this ensures that all timestamps are displayed in
UTC both when querying the database via the command line, and when
returning ``datetime`` objects via the SQLAlchemy API (full docs
`here <http://www.postgresql.org/docs/9.3/static/config-setting.html>`__).

Checking out and building q3c
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We pull in `q3c <https://github.com/segasai/q3c>`__ as a submodule, so
unless you used a recursive ``git clone`` you will need to:

::

    git submodule init
    git submodule update

Then, to build q3c and install it into the PostgreSQL *contrib* folder:

::

    cd external/q3c
    make
    sudo make install

Package Installation
~~~~~~~~~~~~~~~~~~~~
Once all that's out of the way, installation is trivial, simply run::

    pip install .[all]

from the repository root, or (if you plan on development work)::

    pip install -e .[all]

.. _testing:

Testing
=========
voeventdb is accompanied by an extensive test-suite, powered by pytest_.

To run the tests, you can run::

    py.test -sv

From the repository root (see ``py.test -h`` for details),
or you can use::

    ./runtests.py -sv

Which is a wrapper arount pytest which sets up some sensible logging defaults.

The tests can be run via tox_, which additionally confirms a correct
build-and-install process.
Commits uploaded to github are automatically tested via Travis_.

.. _pytest: http://pytest.org/
.. _tox: https://tox.readthedocs.org/
.. _Travis: https://travis-ci.org/timstaley/voeventdb
