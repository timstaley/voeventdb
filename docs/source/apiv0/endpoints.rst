.. _apiv0_endpoints:

Endpoints
---------
The ``apiv0`` endpoints are listed below.

Most endpoints return a JSON-encoded dictionary;
the 'Result' values documented below refer to the contents of the ``result``
entry in the JSON-dict. See :ref:`returned-content` for details.


.. autoflask:: voeventdb.server.restapi.app:app
    :blueprints: apiv0

