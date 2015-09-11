from sqlalchemy.orm import sessionmaker, scoped_session

# Create a shared reference to the thread-local session-proxy. cf
# http://docs.sqlalchemy.org/en/rel_1_0/orm/contextual.html#thread-local-scope
# Configure this with an engine of choice before instantiating
db_session = scoped_session(sessionmaker())