# voeventdb      [![Build Status](https://travis-ci.org/timstaley/voeventdb.svg?branch=master)](https://travis-ci.org/timstaley/voeventdb)

A database-store and accompanying RESTful query API for archiving and retrieving 
[VOEvent](http://voevent.readthedocs.org/) packets.

## Postgres Database Setup

Before the unit-tests or database setup will run, we need a 
[PostgreSQL](http://www.postgresql.org/) 
installation, and a database login with createdb rights. 
On a typical Debian system, install postgres with something like:

    sudo apt-get install libpq-dev postgresql-9.3 postgresql-server-dev-9.3
    
You can check if you have database login and creation rights by running e.g.

    createdb
    
Which will attempt to create a database named after your username. 
On a fresh Postgres installation you will get an access rights error - 
you need to login and create your user like so:

    user@machine: sudo su postgres
    postgres@machine: psql
    postgres=# create user userfoo with superuser;
    postgres=# alter user userfoo with password 'userfoo';

For full details, consult the 
[postgres docs](http://www.postgresql.org/docs/9.3/interactive/tutorial-createdb.html).

Note the unit-tests assume by default a database username/password which
are both the same as your login username, but this can be edited in
the [test config file](voeventdb/tests/config.py).
Alternatively, edit 
[pg_hba.conf](http://www.postgresql.org/docs/9.1/static/auth-pg-hba-conf.html)
appropriately, or consult a friendly sysadmin.

A final word on Postgres setup - I recommend setting 

    timezone = 'UTC'
    
in *postgresql.conf*, this ensures that all timestamps are displayed in UTC 
both when querying the database via the command line, and when returning 
`datetime` objects via the SQLAlchemy API 
(full docs [here](http://www.postgresql.org/docs/9.3/static/config-setting.html)).

## Package Installation
Once all that's out of the way, installation is trivial, simply run

    pip install .[all]


