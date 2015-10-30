from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (backref, deferred, relationship,
                            )
from sqlalchemy import Column, ForeignKey
import sqlalchemy as sql
import voeventparse as vp
from datetime import datetime
import iso8601
import pytz
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


def _grab_xpath(root, xpath, converter=lambda x: x):
    """
    XML convenience - grabs the first element at xpath if present, else returns None.
    """
    elements = root.xpath(xpath)
    if elements:
        return converter(str(elements[0]))
    else:
        return None


class OdictMixin(object):
    def to_odict(self):
        """
        Returns an OrderedDict representation of the SQLalchemy table row.
        """
        colnames = [c.name for c in self.__table__.columns]
        return OrderedDict(((col, getattr(self, col)) for col in colnames))


class Voevent(Base, OdictMixin):
    """
    Define the core VOEvent table.

    .. NOTE::
        On datetimes:
        We store datetimes 'with timezone' even though we'll use the convention
        of storing UTC throughout (and VOEvents are UTC too).
        This helps to make explicit what convention we're using and avoid
        any possible timezone-naive mixups down the line.

        However, if this ever gets used at (really large!) scale, then may
        need to be wary of issues with partitioning really large datasets, cf:
        http://justatheory.com/computers/databases/postgresql/use-timestamptz.html
        http://www.postgresql.org/docs/9.1/static/ddl-partitioning.html

    """
    __tablename__ = 'voevent'
    # Basics: Attributes or associated metadata present for almost every VOEvent:
    id = Column(sql.Integer, primary_key=True)
    received = Column(
        sql.DateTime(timezone=True), nullable=False,
        doc="Records when the packet was loaded into the database"
    )
    ivorn = Column(sql.String, nullable=False, unique=True, index=True)
    stream = Column(sql.String, index=True)
    role = Column(sql.Enum(vp.definitions.roles.observation,
                           vp.definitions.roles.prediction,
                           vp.definitions.roles.utility,
                           vp.definitions.roles.test,
                           name="roles_enum",
                           ),
                  index=True
                  )
    version = Column(sql.String)
    # Who
    author_ivorn = Column(sql.String)
    author_datetime = Column(sql.DateTime(timezone=True))
    # Finally, the raw XML. Mark this for lazy-loading, cf:
    # http://docs.sqlalchemy.org/en/latest/orm/loading_columns.html
    xml = deferred(Column(sql.String))

    cites = relationship("Cite", backref=backref('voevent', order_by=id),
                         cascade="all, delete, delete-orphan")

    coords = relationship('Coord', backref=backref('voevent', order_by=id),
                          cascade="all, delete, delete-orphan")

    @staticmethod
    def from_etree(root, received=pytz.UTC.localize(datetime.utcnow())):
        """
        Init a Voevent row from an LXML etree loaded with voevent-parse
        """
        ivorn = root.attrib['ivorn']
        # Stream- Everything except before the '#' separator,
        # with the prefix 'ivo://' removed:
        stream = ivorn.split('#')[0][6:]
        row = Voevent(ivorn=ivorn,
                      role=root.attrib['role'],
                      version=root.attrib['version'],
                      stream=stream,
                      xml=vp.dumps(root),
                      received=received,
                      )
        row.author_datetime = _grab_xpath(root, 'Who/Date',
                                          converter=iso8601.parse_date)
        row.author_ivorn = _grab_xpath(root, 'Who/AuthorIVORN')

        row.cites = Cite.from_etree(root)
        row.coords = Coord.from_etree(root)
        return row

    def _reformatted_prettydict(self, valformat=str):
        pd = self.prettydict()
        return '\n'.join(
            ("{}={}".format(k, valformat(v)) for k, v in pd.iteritems()))

    def __repr__(self):
        od = self.to_odict()
        content = ',\n'.join(
            ("{}={}".format(k, repr(v)) for k, v in od.iteritems()))
        return """<Voevent({})>""".format(content)

    def __str__(self):
        od = self.to_odict()
        od.pop('xml')
        content = ',\n    '.join(
            ("{}={}".format(k, str(v)) for k, v in od.iteritems()))
        return """<Voevent({})>""".format(content)


class Cite(Base, OdictMixin):
    """
    Record the references cited from each VOEvent.

    Relationship is one Voevent -> Many Cites.


    .. note:: On store-by-value vs store-by-reference

        NB, we store the ref_ivorn string values in the Cite table rows. This is
        quite inefficient compared to referencing the ID of a Voevent that has
        been previously loaded (in the case that one IVORN is cited by many
        Voevents). However, it's necessary, since we may see an IVORN cited for
        which we don't have the primary entry. If this inefficiency ever becomes
        an issue, I can imagine various schemes where e.g. a Voevent is created
        with just a bare IVORN and no other data if it's cited but not ingested,
        with a flag-bit set accordingly. Or we could create a separate 'cited
        IVORNS' table. But probably you ain't gonna need it.


    .. note:: On naming

        `Reference` might be a more appropriate class name, but it's a reserved
        Postgres word, cf
        http://www.postgresql.org/docs/9.3/static/sql-keywords-appendix.html .
        Grammatically speaking, `cite` is a valid noun form, in addition to
        verb: http://www.grammarphobia.com/blog/2011/10/cite.html And it's much
        shorter than 'citation'.


    .. note:: On descriptions

        Note that technically there's a slight model mismatch here: What we're
        really modelling are the EventIVORN entries in the Citations section of
        the VOEvent, which typically share a description between them. This may
        result in duplicated descriptions (but most packets only have a single
        reference anyway).

    """
    __tablename__ = 'cite'
    id = Column(sql.Integer, primary_key=True)
    voevent_id = Column(sql.Integer, ForeignKey(Voevent.id))
    ref_ivorn = Column(sql.String, nullable=False, index=True)
    cite_type = Column(sql.Enum(vp.definitions.cite_types.followup,
                                vp.definitions.cite_types.retraction,
                                vp.definitions.cite_types.supersedes,
                                name="cite_types_enum",
                                ),
                       nullable=False
                       )
    description = Column(sql.String)

    @staticmethod
    def from_etree(root):
        """
        Load up the citations, if present, for initializing with the Voevent.
        """
        cite_list = []
        citations = root.xpath('Citations/EventIVORN')
        if citations:
            description = root.xpath('Citations/Description')
            if description:
                description_text = description[0].text
            else:
                description_text = None
            for entry in root.Citations.EventIVORN:
                if entry.text:
                    cite_list.append(
                        Cite(ref_ivorn=entry.text,
                             cite_type=entry.attrib['cite'],
                             description=description_text)
                    )
                else:
                    logger.info(
                        'Ignoring empty citation in {}'.format(
                            root.attrib['ivorn']))
        return cite_list

    def __repr__(self):
        od = self.to_odict()
        content = ',\n'.join(
            ("{}={}".format(k, repr(v)) for k, v in od.iteritems()))
        return """<Cite({})>""".format(content)


class Coord(Base, OdictMixin):
    """
    Represents a co-ordinate position.

    I.e. an entry in the WhereWhen section of a VOEvent.

    For these entries to be of any use, we must choose a single standard format
    from the wide array of possible VOEvent / STC recommended co-ordinate
    systems and representations. See
    http://www.ivoa.net/documents/REC/DM/STC-20071030.html
    for reference.

    Nominally, we will adopt UTC as the time-system, ICRS decimal degrees as the
    celestial system / representation, and GEO as the reference position.

    In practice, we take a relaxed attitude where GEO / TOPO are assumed
    approximately equal, as are FK5/ICRS, and hence any matching substitutes are
    loaded into the database without further co-ordinate transformation.

    Additional transformation code may be implemented in future as requirements
    and developer time dictate. As a fallback, the client can always request the
    XML packet and inspect the native VOEvent representation for themselves,
    assuming that other fields / naively parsed co-ordinates can be used to
    restrict the number of plausibly relevant packets.
    """
    __tablename__ = 'coord'
    id = Column(sql.Integer, primary_key=True)
    voevent_id = Column(sql.Integer, ForeignKey(Voevent.id))
    ra = Column(sql.Float, nullable=False, index=True)
    decl = Column(sql.Float, nullable=False, index=True)
    error = Column(
        sql.Float,
        doc="Error-circle radius associated with coordinate-position (degrees)"
    )
    time = Column(
        sql.DateTime(timezone=True), nullable=False,
        doc="Records timestamp associated with co-ordinate position of event"
    )

    @staticmethod
    def from_etree(root):
        """
        Load up the coords, if present, for initializing with the Voevent.
        """
        position_list = []
        astrocoords = root.xpath(
            'WhereWhen/ObsDataLocation/ObservationLocation/AstroCoords'
        )
        if astrocoords:
            for idx, entry in enumerate(astrocoords):
                posn = vp.pull_astro_coords(root,idx)
                isotime = vp.pull_isotime(root,idx)
                position_list.append(
                    Coord(ra = posn.ra,
                          decl = posn.dec,
                          error = posn.err,
                          time = isotime)
                )
        return position_list