.. _introduction:

Introduction
=============

*voeventdb* is a database-store and accompanying RESTful
query API for archiving and retrieving
`VOEvent <http://voevent.readthedocs.org/>`_ packets.

*A what?*
----------
(If you've never heard of a VOEvent,
`read this first <http://voevent.readthedocs.org/en/latest/intro.html>`_).

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
  in a particular region of sky, or mapping the distribution of detected events,
  etc.


Key Features
-------------
The key features of voeventdb, as far as the end-user is concerned, can
be summarised as follows:

 - Ready-made Python client-library
    If you've never used a 'REST' interface before, don't worry. Voeventdb comes
    with a ready-made Python client-library,
    `voeventdb.remote <https://github.com/timstaley/voeventdb.remote>`_,
    which simplifies
    querying the database to calling a few Python functions, as laid out in the
    accompanying `tutorial <http://voeventdbremote.readthedocs.org/en/latest/>`_.
 - Full XML storage
    You can always retrieve the original packet-data if you
    know the IVORN identifier (and assuming there's a copy in the database).
 - Spatial filtering
    You can limit your search query to a 'cone', i.e.
    only returning events near to a given location. This functionality is
    powered by Sergey Koposov's `q3c <https://github.com/segasai/q3c>`_.
 - Web of citations
    The database contains the information needed to determine
    reference / citation links between different VOEvent packets, so for example
    you can check if an exciting new transient announced in one packet has
    already been followed up by another VOEvent broadcasting observatory.
 - Various summary statistics at your fingertips
    View the number of VOEvents
    broken down by observatory, by month, by type, etc.
 - Extensive filters, applicable throughout
    Narrow your query to a particular
    type of alert, limit it to packets authored between certain dates, only return
    events which are cited by others, return all events citing one particular
    packet, etc etc. Queries and endpoints can be thought of as orthogonal_,
    i.e. the same filter-set can be applied to any endpoint.
 - Loading / dumping of XML packets in plain-old-tarballs
    The package contains routines for handling BZ2-compressed tarballs containing
    the original XML packets. This allows for version migration, or exporting the
    archive to another tool entirely. It also keeps the backups remarkably
    compact - all 750,000 or so packets for the past 12 months weigh in at just
    under 100MB in compressed form.

.. _orthogonal: https://en.wikipedia.org/wiki/Orthogonality#Computer_science

.. _getting_started:

Getting started
----------------
If you just want to query our copy of the database rather than running your
own, then you should probably head over to the Python-client-package,
`voeventdb.remote <https://github.com/timstaley/voeventdb.remote>`_,
or jump straight to the relevant
`documentation <http://voeventdbremote.readthedocs.org/en/latest/>`_.

If you would like to access the REST API directly, our copy of voeventdb
is hosted and documented at http://voeventdb.4pisky.org/. You can find
reference information on how to form your http-queries :ref:`here <apiv0_ref>`.

If you want to run a local copy of voeventdb, or contribute to voeventdb's
development, see :ref:`installation`.