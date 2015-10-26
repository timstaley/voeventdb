#!/usr/bin/env python

import sys
import os
import argparse
import logging

from sqlalchemy.engine.url import make_url
from sqlalchemy import create_engine

from sqlalchemy.orm import Session

from voeventdb.database import ingest, db_utils
from voeventdb.tests.config import testdb_corpus_url

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('iso8601').setLevel(
    logging.ERROR)  # Suppress iso8601 debug log.
logger = logging.getLogger("vo-ingest")


def directory_arg(p):
    if not os.path.isdir(p):
        msg = "Cannot find directory at {}".format(p)
        raise argparse.ArgumentTypeError(msg)
    return p


def filepath_arg(p):
    if not os.path.isfile(p):
        msg = "Cannot find file at {}".format(p)
        raise argparse.ArgumentTypeError(msg)
    return p


def handle_args():
    """
    Default values are defined here.
    """

    default_database_url = testdb_corpus_url
    parser = argparse.ArgumentParser(prog=os.path.basename(__file__))
    parser.add_argument('tarfile',
                        nargs='?',
                        type=filepath_arg,
                        help='Top level folder to scan for XML files')

    parser.add_argument('-d', '--database_url', nargs='?',
                        type=make_url,
                        default=str(default_database_url),
                        help='Database url \n'
                             ' (default="{}"'.format(default_database_url))

    parser.add_argument('-c', '--check', action='store_true',
                        help="Check for (and ignore) duplicate packets.")
    return parser.parse_args()


def main():
    args = handle_args()
    if not db_utils.check_database_exists(args.database_url):
        raise RuntimeError("Database not found")

    session = Session(bind=create_engine(args.database_url))
    n_parsed, n_loaded = ingest.load_from_tarfile(session,
                                                  tarfile_path=args.tarfile,
                                                  check_for_duplicates=args.check)
    session.close()
    logger.info("Loaded {} packets into {}".format(n_loaded, args.database_url))
    return 0


if __name__ == '__main__':
    sys.exit(main())
