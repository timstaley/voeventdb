#!/usr/bin/env python

import sys
import os
import argparse
import logging

from sqlalchemy.engine.url import make_url
from sqlalchemy import create_engine

from voeventcache.database import db_utils
from voeventcache.tests.config import testdb_corpus_url, admin_db_url
from voeventcache.database.models import Base

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("create_db")


def database_url(s):
    return make_url(s)

def handle_args():
    """
    Default values are defined here.
    """
    default_database_url = testdb_corpus_url
    parser = argparse.ArgumentParser(prog=os.path.basename(__file__))

    parser.add_argument('database_url',
                    nargs='?',
                    type=database_url,
                    default=str(default_database_url),
                    help='Database url \n (default="{}"'.format(default_database_url)
                    )
    return parser.parse_args()

def main():
    args = handle_args()
    dburl = args.database_url
    if not db_utils.check_database_exists(dburl):
        db_utils.create_database(admin_db_url, dburl.database)
    engine = create_engine(dburl)
    Base.metadata.create_all(engine)
    logger.info('Database "{}" created.'.format(dburl.database))
    



if __name__ == '__main__':
    sys.exit(main())
