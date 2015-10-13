REST API v0 (``apiv0``)
===============================


Endpoints
---------
The ``apiv0`` endpoints are listed below.

Most endpoints return a JSON-encoded dictionary;
the 'Result' values documented below refer to the contents of the ``result``
entry in the JSON-dict. See `returned content`_ for details.

.. note::

    Clicking the 'Result' headers below will direct you to the relevant
    endpoint.

.. autoflask:: voeventcache.restapi.app:app
    :blueprints: apiv0


Returned content
----------------
.. autoclass:: voeventcache.restapi.v0.ResultKeys
    :members:
    :undoc-members:


List-pagination controls
------------------------
The following query-keys can be used to alter the ordering and slicing of
results when querying a list-endpoint and returning a large number of entries:


.. autoclass:: voeventcache.restapi.v0.PaginationKeys
    :members:
    :undoc-members:



Query filters
---------------------------
These filters can be applied by providing key-value pairs as part of the
`query string`_ in your HTTP request, where the key is equal to the
``querystring_key`` entry below, and the value is formatted like one of the
``example_values``.

The same query filters can be applied to all endpoints except for the
XML-endpoint (`/apiv0/xml/ <apiv0.html#get--apiv0-xml-(path-ivorn)>`_),
which only ever returns a single XML packet matching an exact IVORN.


.. _query string: https://en.wikipedia.org/wiki/Query_string

.. automodule:: voeventcache.restapi.v0.filters
    :members:
    :undoc-members:
    :member-order: bysource

