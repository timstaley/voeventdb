# voeventcache

A database-store and accompanying RESTful query API for archiving and retrieving 
[VOEvent](http://voevent.readthedocs.org/) packets.

## Setup

Before the unit-tests or database setup will run, we need a postgres 
installation, and a database login with createdb rights. 
On a typical Debian system, install postgres with something like:

    sudo apt-get install postgresql libpq-dev
    
You can check if you have database login and creation rights by running e.g.

    createdb
    
Which will attempt to create a database named after your username. 
On a fresh Postgres installation you will get an access rights error - 
you need to login and create your user like so:

    user@machine: sudo su postgres
    postgres@machine: psql
    postgres=# create user userfoo with superuser;
    postgres=# alter user userfoo with password 'userfoo';

Note the unit-tests assume by default a database username/password which
are both the same as your login username, but this can be edited in
the [test config file](voeventcache/tests/config.py).
Alternatively, edit 
[pg_hba.conf](http://www.postgresql.org/docs/9.1/static/auth-pg-hba-conf.html)
appropriately, or consult a friendly sysadmin.