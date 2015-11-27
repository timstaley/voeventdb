
.. _querying:

Querying the REST API
=====================

The voeventdb web-interface is designed around widely used RESTful_ concepts,
which means (simplifying grossly) that all the details of your data query are
encoded in an HTTP URL. By making requests at that URL, you get back the data
matching your query. You can try this out by following links and editing the URL
in your browser, but typically you'll want to grab data using a scripting
library such as Python's requests_. [#client]_

.. _RESTful: https://en.wikipedia.org/wiki/Representational_state_transfer
.. _JSON: https://en.wikipedia.org/wiki/JSON
.. _requests: http://docs.python-requests.org/

Finding and using endpoints
----------------------------

The base URLs which represent different queries are known as 'endpoints' -
full listings for voeventdb can be found on the :ref:`endpoints` page.
Some useful places to start are the
`root <endpoints.html#get--apiv0->`_ endpoint, which provides a concise listing
of the endpoints available, and the
`stream count <endpoints.html#get--apiv0-stream_count>`_ endpoint, which
serves as a sort of 'contents' page for the database.

.. [#client] A ready-made Python-client library which wraps requests_ in a
    convenient fashion may be made available in future
    (contributions / expressions of interest welcomed).


.. _narrowing:

Narrowing your query
--------------------

Most endpoints return data pertaining to all VOEvents
currently stored in the database. [#notalldata]_
To narrow down your query to a specific subset of the VOEvents,
you can apply a selection of the available filters listed on the
:ref:`filters` page.
Filters are be applied by providing key-value pairs as part of the
`query-string`_ in your HTTP request - see the filters page for details.


.. [#notalldata] The exceptions are the
    `packet-detail <endpoints.html#get--apiv0-full->`_
    and
    `XML <endpoints.html#get--apiv0-xml->`_
    endpoints, which are intended to retrieve data about a particular
    VOEvent.


.. _query-string: https://en.wikipedia.org/wiki/Query_string

.. _url-encoding:

URL-Encoding
-------------

Note that if you are accessing the
`packet-detail <endpoints.html#get--apiv0-full->`_
or
`XML <endpoints.html#get--apiv0-xml->`_
endpoints, or specifying a query-filter value which contains the ``#``
character, then you will need to use `URL-encoding <URL-encode_>`_ (because otherwise the
query-value is indistinguishable from an incorrectly-formed URL). It's simple to
manually URL-encode the value using a `web-based tool`_, or e.g. in
python::

    import urllib
    s = urllib.quote_plus("ivo://foo.bar/baz#quux")
    print(s)


.. _URL-encode: https://en.wikipedia.org/wiki/Query_string#URL_encoding
.. _web-based tool: http://meyerweb.com/eric/tools/dencoder/


.. _pagination:

List-pagination controls
----------------------------
The database can easily handle millions of entries, so it makes sense to
break up the return-data for queries which return (possibly large) lists
of data. You can use pagination-keys in the same manner as
query-keys (i.e. in the query-string) to control this:


.. autoclass:: voeventdb.server.restapi.v0.definitions.PaginationKeys
    :members:
    :undoc-members:

.. autoclass:: voeventdb.server.restapi.v0.definitions.OrderValues
    :members:
    :undoc-members:

.. _returned-content:

Returned content
----------------
.. autoclass:: voeventdb.server.restapi.v0.viewbase.ResultKeys
    :members:
    :undoc-members: