#!/usr/bin/env python

import argparse
import datetime
import logging
import os
import sys
import textwrap

import iso8601
import pytz
import voeventdb.server.database.config as dbconfig
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from voeventdb.server.database import db_utils
from voeventdb.server.database.models import Voevent
from voeventdb.server.utils.filestore import (
    write_tarball,
)

logging.basicConfig(level=logging.INFO)
logging.getLogger('iso8601').setLevel(
    logging.ERROR)  # Suppress iso8601 debug log.
logger = logging.getLogger("voeventdb-dump")


class MyFormatter(argparse.ArgumentDefaultsHelpFormatter,
                  argparse.RawDescriptionHelpFormatter):
    pass


def handle_args():
    """
    Default values are defined here.
    """

    default_database_name = dbconfig.testdb_corpus_url.database
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        # formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        formatter_class=MyFormatter,
        description=textwrap.dedent("""\
        Dump the raw VOEvents as XML files, collected into bzip2'd tarballs.

        If start or end times are specified, then the range is start-inclusive
        end-exclusive, i.e.

            start <= author_datetime < end

        NB when writing compressed tarballs in Python, the entire file is
        composed in memory before writing to file. This means that setting
        `nsplit` too large will result in very high memory usage! The default
        value of 5000 seems to peak at <250MB of RAM (though this varies
        according to the size of the VOEvent packets, and assumes
        `prefetch=False`). Some quick tests suggest typical RAM usage
            ~= 40MB + 30MB*(nsplit/1000) .
        """),

    )
    parser.add_argument('tarfile_pathstem',
                        help='Path to tarball to create, e.g. `foobar`. '
                             'Suffix ``.tar.bz2`` will be appended.'
                        )

    parser.add_argument('-d', '--dbname', nargs='?',
                        default=str(default_database_name),
                        help='Database name')

    parser.add_argument('-n', '--nsplit',
                        type=int,
                        default=5000,
                        help=
                        "Output multiple files, `NSPLIT` packets per tarball."
                        "Naming convention is `<stem>.001.tar.bz2, <stem>.002.tar.bz2, ...`"
                        )
    parser.add_argument('-s', '--start',
                        type=iso8601.parse_date,
                        default=None,
                        help="Filter events by author_date>=`START`")
    parser.add_argument('-e', '--end',
                        type=iso8601.parse_date,
                        default=datetime.datetime.now(tz=pytz.UTC),
                        help=
                        "Filter events by author_date<`END`")
    parser.add_argument('-p', '--prefetch', action='store_true', default=False,
                        help=
                        "Bulk-fetch XML packets from DB (~3x faster, but "
                        "uses considerably more RAM, depending on value of "
                        "`nsplit`.)"
                        )
    parser.add_argument('-a', '--all', action='store_true', default=False,
                        help=
                        "Ignore any datetime filters, dump **all** VOEvents."
                        "(This option is provided to allow dumping of VOEvents"
                        "with author_datetime=Null, which are otherwise ignored.)"
                        )
    return parser.parse_args()


def main():
    args = handle_args()
    dburl = dbconfig.make_db_url(dbconfig.default_admin_db_params, args.dbname)
    if not db_utils.check_database_exists(dburl):
        raise RuntimeError("Database not found")

    filecount = 1
    n_packets_written = 0

    def get_tarfile_path():
        if args.nsplit:
            suffix = '.{0:03d}.tar.bz2'.format(filecount)
        else:
            suffix = '.tar.bz2'
        return args.tarfile_pathstem + suffix

    session = Session(bind=create_engine(dburl))
    if args.prefetch:
        qry = session.query(Voevent.ivorn, Voevent.xml)
    else:
        qry = session.query(Voevent)

    if args.all:
        logger.info("Dumping **all** packets currently in database")
    else:
        qry = qry.filter(Voevent.author_datetime < args.end)
        if args.start is not None:
            qry = qry.filter(Voevent.author_datetime >= args.start)
            logger.info("Fetching packets from {}".format(args.start))
        else:
            logger.info("Fetching packets from beginning of time")
        logger.info("...until: {}".format(args.end))
    qry = qry.order_by(Voevent.id)

    n_matching = qry.count()
    logger.info("Dumping {} packets".format(n_matching))
    start_time = datetime.datetime.now()
    while n_packets_written < n_matching:
        logger.debug("Fetching batch of up to {} packets".format(args.nsplit))
        voevents = qry.limit(args.nsplit).offset(n_packets_written).all()

        n_packets_written += write_tarball(voevents,
                                           get_tarfile_path())
        elapsed = (datetime.datetime.now() - start_time).total_seconds()
        logger.info(
            "{} packets dumped so far, in {} ({:.0f} kilopacket/s)".format(
                n_packets_written,
                elapsed,
                n_packets_written / elapsed
            ))
        filecount += 1
    session.close()
    logger.info("Wrote {} packets".format(n_packets_written))
    return 0


if __name__ == '__main__':
    sys.exit(main())
