"""
Define a singleton database session.

Used to be in __init__.py, but that could result in circular imports if
we need it in another database module.
"""
from __future__ import absolute_import
from sqlalchemy.orm import sessionmaker, scoped_session

# Create a shared reference to the thread-local session-proxy. cf
# http://docs.sqlalchemy.org/en/rel_1_0/orm/contextual.html#thread-local-scope
# Configure this with an engine of choice before instantiating
db_session = scoped_session(sessionmaker())