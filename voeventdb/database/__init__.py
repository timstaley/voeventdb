from __future__ import absolute_import
from sqlalchemy.orm import sessionmaker, scoped_session
from flask import _app_ctx_stack

# Create a shared reference to the thread-local session-proxy. cf
# http://docs.sqlalchemy.org/en/rel_1_0/orm/contextual.html#thread-local-scope
# Configure this with an engine of choice before instantiating
session_factory = sessionmaker()
session_registry = scoped_session(session_factory,
                                  scopefunc=_app_ctx_stack.__ident_func__)




