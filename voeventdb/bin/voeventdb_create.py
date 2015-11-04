#!/usr/bin/env python

import sys
import os
import argparse
import logging

from sqlalchemy.engine.url import make_url
from sqlalchemy import create_engine

from voeventdb.database import db_utils
import voeventdb.database.config as dbconfig
from voeventdb.database.models import Base

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("create_db")


def database_url(s):
    return make_url(s)


def handle_args():
    """
    Default values are defined here.
    """
    default_database_name = dbconfig.testdb_corpus_url.database
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('dbname',
                        nargs='?',
                        default=str(default_database_name),
                        help='Database name',
                        )
    return parser.parse_args()


def main():

    args = handle_args()
    dburl = dbconfig.make_db_url(dbconfig.default_admin_db_params, args.dbname)
    if not db_utils.check_database_exists(dburl):
        db_utils.create_database(dbconfig.default_admin_db_url, args.dbname)
    engine = create_engine(dburl)
    Base.metadata.create_all(engine)
    logger.info('Database "{}" created.'.format(dburl.database))
    return 0


if __name__ == '__main__':
    sys.exit(main())
