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

import click

logging.basicConfig(level=logging.INFO)
logging.getLogger('iso8601').setLevel(
        logging.ERROR)  # Suppress iso8601 debug log.
logger = logging.getLogger("voeventdb-ingest")


@click.command()
@click.option('-d', '--dbname',
              default=str(dbconfig.testdb_corpus_url.database),
              help="Database to load to, default='{}'".format(
                  dbconfig.testdb_corpus_url.database
              ))
@click.option('--check/--no-check', default=False,
              help="Check for (and ignore) duplicate packets. Default behaviour "
                   "is to ingest in batches without checking first - this is "
                   "faster but may fail part-way through if it hits a duplicate "
                   "entry.")
@click.argument('tarballs', nargs=-1, type=click.Path())
def main(dbname, check, tarballs):
    dburl = dbconfig.make_db_url(dbconfig.default_admin_db_params, dbname)
    if not db_utils.check_database_exists(dburl):
        raise RuntimeError("Database not found")

    with click.progressbar(tarballs) as tarball_bar:
        for tbpath in tarball_bar:
            session = Session(bind=create_engine(dburl))
            n_parsed, n_loaded = ingest.load_from_tarfile(
                    session,
                    tarfile_path=tbpath,
                    check_for_duplicates=check)
            logger.info("Loaded {} packets into {} from {}".format(
                    n_loaded, dbname, tbpath))
            session.close()
    return 0


if __name__ == '__main__':
    main()
