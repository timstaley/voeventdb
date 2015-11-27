#!/usr/bin/env python

import sys
import os
import argparse
import logging

from sqlalchemy.engine.url import make_url
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from voeventdb.server.database import ingest, db_utils
import voeventdb.server.database.config as dbconfig

logging.basicConfig(level=logging.INFO)
logging.getLogger('iso8601').setLevel(
    logging.ERROR)  # Suppress iso8601 debug log.
logger = logging.getLogger("voeventdb-ingest")



def filepath_arg(p):
    if not os.path.isfile(p):
        msg = "Cannot find file at {}".format(p)
        raise argparse.ArgumentTypeError(msg)
    return p


def handle_args():
    """
    Default values are defined here.
    """

    default_database_name = dbconfig.testdb_corpus_url.database
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, )
    parser.add_argument('tarfile',
                        nargs='?',
                        type=filepath_arg,
                        help='Tarball containing XML files.')

    parser.add_argument('-d', '--dbname', nargs='?',
                        default=str(default_database_name),
                        help='Database name')

    parser.add_argument('-c', '--check', action='store_true',
                        help="Check for (and ignore) duplicate packets.")
    return parser.parse_args()


def main():
    args = handle_args()
    dburl = dbconfig.make_db_url(dbconfig.default_admin_db_params, args.dbname)
    if not db_utils.check_database_exists(dburl):
        raise RuntimeError("Database not found")

    session = Session(bind=create_engine(dburl))
    n_parsed, n_loaded = ingest.load_from_tarfile(session,
                                                  tarfile_path=args.tarfile,
                                                  check_for_duplicates=args.check)
    session.close()
    logger.info("Loaded {} packets into {}".format(n_loaded, args.dbname))
    return 0


if __name__ == '__main__':
    sys.exit(main())
