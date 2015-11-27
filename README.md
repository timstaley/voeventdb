# voeventdb      [![Build Status](https://travis-ci.org/timstaley/voeventdb.svg?branch=master)](https://travis-ci.org/timstaley/voeventdb)

A database-store and accompanying RESTful query API for archiving and retrieving 
[VOEvent](http://voevent.readthedocs.org/) packets.

### A what?
(If you've never heard of a VOEvent, start 
[here](http://voevent.readthedocs.org/en/latest/intro.html)).

This package contains code for building a database of
transient astronomical events, for which alerts or follow-up data 
have been sent via the VOEvent network. It also provides a RESTful API,
which means you can query the database remotely via the internet, either 
using your web-browser or your programming language of choice. 

This serves two main purposes:

 - It allows people distributing or monitoring VOEvent packets to 'catch up' 
   with any missed data, in the event of a network or systems outage.
 - It allows astronomers to search through the archive of VOEvents. This can 
   be useful for planning future observations, or looking for related events
   in a particular region of sky.

If you just want to query our copy of the database rather than running your
own, then you should probably head over to the python-client-package, 
[voeventdb.remote](https://github.com/timstaley/voeventdb.remote).

If you would like to access the REST API directly, our copy of voeventdb
is hosted and documented at http://voeventdb.4pisky.org/.
 

## Key Features:

 - Full XML storage - you can always retrieve the original packet-data if you
   know the IVORN identifier (and assuming there's a copy in the database).
 - Spatial filtering: you can limit your search query to a 'cone', i.e.
   only returning events near to a given location. This functionality is
   powered by Sergey Koposov's [q3c](https://github.com/segasai/q3c).
 - Web of citations: the database contains the information needed to determine
   reference / citation links between different VOEvent packets, so for example
   you can check if an exciting new transient announced in one packet has 
   already been followed up by another VOEvent broadcasting observatory.
 - Various summary statistics at your fingertips: view the number of VOEvents
   broken down by observatory, by month, by type. 
 - Extensive filters: narrow your query to a particular type of alert, limit
   it to packets authored between certain dates, only return events which 
   are cited by others, return all events citing one particular packet, etc etc.
 - Tools for loading from / dumping to BZ2-compressed tarballs containing the 
   original XML packets. This allows for version migration, or exporting the 
   archive to another tool entirely.


## All-in-one installation scripts for the [DevOps][] enthusiast 
If you'd like to install your own copy of voeventdb, you may be interested
in the accompanying [Ansible][] [role][] that provides a pre-configured 
installation of the voeventdb database and REST API, optionally served via 
Apache, available here: 
https://github.com/timstaley/ansible-voeventdb.

The voeventdb role is demonstrated in conjunction with another role installing the
[Comet](http://comet.readthedocs.org/) broker (to pull in the latest VOEvent
packets) here:
https://github.com/4pisky/voeventdb-deploy - in fact, those are the scripts which build 
http://voeventdb.4pisky.org/.
    
Note that, at time of writing, I've not had time to document these packages
much - if you'd be interested in making use of them please
drop me a line and I may be able to provide help / improve the associated docs.

[DevOps]: https://en.wikipedia.org/wiki/DevOps


[Ansible]: http://www.ansible.com/configuration-management
[role]: http://docs.ansible.com/ansible/playbooks_roles.html

## Development installation
Alternately, if you want a local installation for development and testing 
purposes (or you just prefer the hands-on approach) then read on for 
some tips regarding manual installation.
### Postgres Database Setup

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

    userfoo@machine: sudo su postgres
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

### Checking out and building q3c
We pull in [q3c](https://github.com/segasai/q3c) as a submodule, so unless you used a 
recursive ``git clone`` you will need to:

    git submodule init
    git submodule update
    
Then, to build q3c and install it into the PostgreSQL *contrib* folder:

    cd external/q3c
    make
    sudo make install


### Package Installation
Once all that's out of the way, installation is trivial, simply run

    pip install .[all]

from the repository root.

## License
GPL v2 (see [licence file](COPYING.txt)). This package is GPL by necessity due
to use of q3c. If circumstances warrant it, another spatial query engine could
perhaps be swapped in and a re-licensing arranged, but I don't see that being
likely anytime soon.

## Acknowledgement
If you'd like to use voeventdb (or the REST API provided at 
http://voeventdb.4pisky.org/) for work leading to a publication then I would 
appreciate you getting in touch so that I can arrange a suitable 
[ASCL](http://ascl.net/) entry or other DOI for citing.


