#!/usr/bin/env python

import argparse
import logging
import logging.handlers
import os
import sys

import six
import voeventparse
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import voeventdb.server.database.config as dbconfig
import voeventdb.server.database.convenience as conv
from voeventdb.server.database import db_utils


def handle_args():
    """
    Default values are defined here.
    """

    default_database_name = os.environ.get(
        'VOEVENTDB_DBNAME',
        dbconfig.testdb_corpus_url.database)
    default_logfile_path = os.path.expanduser("~/voeventdb_packet_ingest.log")

    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, )

    parser.description = """
    Ingest a packet from stdin and attempt to ingest into a voeventdb database.

    Usage:

      cat test.xml | voeventdb_ingest_packet.py -d mydb -l /tmp/my.log

    """

    parser.add_argument('-d', '--dbname', nargs='?',
                        default=str(default_database_name),
                        help='Database name')

    parser.add_argument('-l', '--logfile_path', nargs='?',
                        default=default_logfile_path,
                        )
    return parser.parse_args()


def setup_logging(logfile_path):
    """
    Set up basic (INFO level) and debug logfiles
    """
    date_fmt = "%y-%m-%d (%a) %H:%M:%S"

    std_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s',
                                      date_fmt)

    # Get to the following size before splitting log into multiple files:
    log_chunk_bytesize = 5e6

    info_logfile = logging.handlers.RotatingFileHandler(logfile_path,
                                                        maxBytes=log_chunk_bytesize,
                                                        backupCount=10)
    info_logfile.setFormatter(std_formatter)
    info_logfile.setLevel(logging.DEBUG)

    stdout_log = logging.StreamHandler()
    stdout_log.setLevel(logging.DEBUG)
    stdout_log.setFormatter(std_formatter)

    # Set up root logger
    logger = logging.getLogger()
    logger.handlers = []
    logger.setLevel(logging.DEBUG)
    logger.addHandler(info_logfile)
    logger.addHandler(stdout_log)
    logging.getLogger('iso8601').setLevel(
        logging.ERROR)  # Suppress iso8601 debug log.
    return logger


def main():
    args = handle_args()
    logger = setup_logging(args.logfile_path)
    dburl = dbconfig.make_db_url(dbconfig.default_admin_db_params, args.dbname)
    if not db_utils.check_database_exists(dburl):
        raise RuntimeError("Database not found")
    if six.PY3:
        stdin = sys.stdin.buffer.read()
    else:
        stdin = sys.stdin.read()  # Py2

    v = voeventparse.loads(stdin)

    session = Session(bind=create_engine(dburl))
    try:
        conv.safe_insert_voevent(session, v)
        session.commit()
    except:
        logger.exception("Could not insert packet with ivorn {} into {}".format(
            v.attrib['ivorn'], args.dbname))

    logger.info("Loaded packet with ivorn {} into {}".format(
        v.attrib['ivorn'], args.dbname))
    return 0


if __name__ == '__main__':
    sys.exit(main())
