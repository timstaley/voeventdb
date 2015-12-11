.. _apiv1_endpoints:

Endpoints
---------
The ``apiv1`` endpoints are listed below.

Most endpoints return a JSON-encoded dictionary;
the 'Result' values documented below refer to the contents of the ``result``
entry in the JSON-dict. See :ref:`returned-content` for details.

.. _apiv1_query_endpoints:

Query endpoints
~~~~~~~~~~~~~~~~

.. autoflask:: voeventdb.server.restapi.app:app
    :blueprints: apiv1
    :undoc-endpoints: apiv1.packet_synopsis, apiv1.packet_xml


.. _apiv1_packet_endpoints:

Single-packet endpoints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Unlike the query-endpoints, these return data on a single packet.

The IVORN of the desired packet should be appended to the endpoint-URL
in :ref:`URL-encoded <url-encoding>` form.


.. autoflask:: voeventdb.server.restapi.app:app
    :blueprints: apiv1
    :endpoints: apiv1.packet_synopsis, apiv1.packet_xml


