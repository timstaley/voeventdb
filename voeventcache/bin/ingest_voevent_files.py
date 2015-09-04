#!/usr/bin/env python

import sys
import os
import argparse
import logging

from sqlalchemy.engine.url import make_url
from sqlalchemy import create_engine

from sqlalchemy.orm import Session

from voeventcache.database import ingest, db_utils
from voeventcache.tests.config import voecache_corpusdb_url

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vo-ingest")

def directory_arg(p):
    if not os.path.isdir(p):
        msg = "Cannot find directory at {}".format(p)
        raise argparse.ArgumentTypeError(msg)
    return p

def database_url(s):
    return make_url(s)

def handle_args():
    """
    Default values are defined here.
    """


    default_database_url = voecache_corpusdb_url
    parser = argparse.ArgumentParser(prog=os.path.basename(__file__))
    parser.add_argument('folder_to_process',
                        nargs='?',
                        type=directory_arg,
                        help='Top level folder to scan for XML files')
    parser.add_argument('-d', '--database_url', nargs='?',
                    type=database_url,
                    default=str(default_database_url),
                    help='Database url \n'
                    ' (default="{}"'.format(default_database_url))
    return parser.parse_args()

def main():
    args = handle_args()
    topdir = args.folder_to_process
    dburl = args.database_url
    if not db_utils.check_database_exists(dburl):
        raise RuntimeError("Database not found")

    session = Session(bind=create_engine(dburl))
    ingest.ingest_dir(topdir, session)
    session.commit()
    session.close()



if __name__ == '__main__':
    sys.exit(main())
