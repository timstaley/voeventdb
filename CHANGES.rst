Change history
==============

1.3.2 (2016/11/28) - Mirror upstream changes in voevent-parse
-------------------------------------------------------------
Minor update to mirror API changes in voevent-parse 1.0.

1.3.1 (2016/11/14) - Fix issue with UTF-8 encoded unicode chars in VOEvents
---------------------------------------------------------------------------
Fix an issue where non-ascii characters in XML packets broke tarball-dumping,
because Postgres returns the data as unicode, and we need to explicitly encode
that to a UTF-8 bytestring before the tarball code will accept it.

1.3.0 (2016/11/09) - Add parsing of barycentric event co-ords
-------------------------------------------------------------
Make use of voevent-parse 0.9.8 (and hence astropy 1.2.x) to apply TDB->UTC time
conversion where relevant (e.g. GAIA event timestamps).

Also relaxes list of allowed position formats.

 .. note::

    VOEventDB does not currently apply any conversion to co-ordinates as read
    in from the packets**, this may produce small inaccuracies for close
    objects. Those needing high-precision ICRS co-ordinates should use coarse
    spatial queries and perform their own position parsing / transformation from
    packet-XML directly. See docstring and source under
    `voeventdb.server.database.models.Coord.from_etree` for more details and
    justification.

1.2.1  (2016/09/19) - Minor bugfix
----------------------------------
Authored_month_count could bin entries incorrectly if postgres
timezone was not configured to UTC.

If Postgres is configured correctly, then all was fine.
But, if default timezone was configured to say, timezone=GB, (UTC+1 in summer),
then datetime is fetched *and truncated in the default (UTC+1) timezone*.
Therefore the month endpoints were off by the timezone offset compared to the
regular 'author_datetime' queries which always enforce timezone evaluation,
and so the 'authored_month_count' endpoint produced conflicting results to
'count' with relevant datetime filters applied.


1.2.0  (2016/09/15) - Tarball-dump-script enhancements
------------------------------------------------------
Add datetime-range filtering options to tarball-dump script.
Also change default tarball size to avoid unreasonable RAM requirements,
document typical RAM usage.
