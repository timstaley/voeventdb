# Defines a plugin for the Comet broker.
# If top-level directory 'comet_plugin' is added to $PYTHONPATH then comet
# will detect this module at import-time.


from zope.interface import implementer
from twisted.plugin import IPlugin
from comet.icomet import IHandler
import comet.log as log
import os
import voeventparse
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import voeventdb.server.database.config as dbconfig
from voeventdb.server.database import db_utils
import voeventdb.server.database.convenience as dbconv

voeventdb_dbname = os.environ.get("VOEVENTDB_DBNAME",
                                  dbconfig.testdb_corpus_url.database)

dburl = dbconfig.make_db_url(dbconfig.default_admin_db_params, voeventdb_dbname)
if not db_utils.check_database_exists(dburl):
    log.warn("voeventdb database not found: {}".format(
        voeventdb_dbname))
dbengine = create_engine(dburl)


@implementer(IPlugin, IHandler)
class VoeventdbInserter(object):
    name = "voeventdb-insert"

    # When the handler is called, it is passed an instance of
    # comet.utility.xml.xml_document.
    def __call__(self, event):
        """
        Add an event to the celery processing queue
        """
        v = None
        try:
            session = Session(bind=dbengine)
            v = voeventparse.loads(event.raw_bytes)
            dbconv.safe_insert_voevent(session, v)
            session.commit()
        except Exception as e:
            if v is None:
                log.warn("Could not parse event-bytes as voevent")
            else:
                log.warn(
                    "Could not insert packet with ivorn {} into database {}".format(
                        v.attrib['ivorn'], voeventdb_dbname))
            self.deferred.errback(e)

        log.info("Loaded {} into database {}".format(
            v.attrib['ivorn'], voeventdb_dbname))


# This instance of the handler is what actually constitutes our plugin.
ingest_event = VoeventdbInserter()
