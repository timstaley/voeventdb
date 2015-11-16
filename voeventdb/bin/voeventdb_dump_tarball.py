#!/usr/bin/env python

import sys
import os
import argparse
import logging
import glob

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from voeventdb.database import db_utils
import voeventdb.database.config as dbconfig
from voeventdb.database.models import Voevent
from voeventdb.utils.filestore import write_tarball

logging.basicConfig(level=logging.INFO)
logging.getLogger('iso8601').setLevel(
    logging.ERROR)  # Suppress iso8601 debug log.
logger = logging.getLogger("voeventdb-dump")


def handle_args():
    """
    Default values are defined here.
    """

    default_database_name = dbconfig.testdb_corpus_url.database
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, )
    parser.add_argument('tarfile_pathstem',
                        help='Path to tarball to create. '
                             'Suffix ``.tar.bz2`` will be appended.'
                        )

    parser.add_argument('-d', '--dbname', nargs='?',
                        default=str(default_database_name),
                        help='Database name')

    parser.add_argument('-s', '--split',
                        type=int,
                        help="Output multiple files, `SPLIT` packets per tarball."
                             "Naming convention is `<stem>.01.tar.bz2, <stem>.02.tar.bz2, ...`")
    return parser.parse_args()


def main():
    args = handle_args()
    dburl = dbconfig.make_db_url(dbconfig.default_admin_db_params, args.dbname)
    if not db_utils.check_database_exists(dburl):
        raise RuntimeError("Database not found")

    filecount = 1
    n_packets_written = 0

    def get_tarfile_path():
        if args.split:
            suffix = '.{0:02d}.tar.bz2'.format(filecount)
        else:
            suffix = '.tar.bz2'
        return args.tarfile_pathstem + suffix

    session = Session(bind=create_engine(dburl))
    qry = session.query(Voevent).order_by(Voevent.id)
    n_matching = qry.count()
    logger.info("Dumping {} packets".format(n_matching))

    while n_packets_written < n_matching:
        voevents = qry.limit(args.split).offset(n_packets_written).all()
        ivorn_xml_tuples_gen = ((v.ivorn, v.xml) for v in voevents)
        n_packets_written +=  write_tarball(ivorn_xml_tuples_gen, get_tarfile_path())
        filecount += 1

    session.close()
    logger.info("Wrote {} packets".format(n_packets_written))
    return 0


if __name__ == '__main__':
    sys.exit(main())
