from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
import sqlalchemy as sql
import voeventparse as vp
from datetime import datetime
import iso8601
import pytz
from collections import OrderedDict

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


class Voevent(Base):
    """
    Define the core VOEvent table.

    .. NOTE::
        On datetimes:
        We store datetimes 'with timezone' even though we'll use the convention
        of storing UTC throughout (and VOEvents are UTC too).
        This helps to make explicit what convention we're using and avoid
        any possible timezone-naive mixups down the line.

        However, if this ever gets used at scale may need to be wary of issues
        with partitioning really large datasets, cf:
        http://justatheory.com/computers/databases/postgresql/use-timestamptz.html
        http://www.postgresql.org/docs/9.1/static/ddl-partitioning.html

    """
    __tablename__ = 'voevent'
    # Basics: Attributes or associated metadata present for **every** VOEvent:
    id = Column(sql.Integer, primary_key=True)
    received = Column(
        sql.DateTime(timezone=True), nullable=False,
        doc="Records when the packet was loaded into the database"
    )
    ivorn = Column(sql.String, nullable=False, unique=True, index=True)
    role = Column(sql.Enum(vp.definitions.roles.observation,
                           vp.definitions.roles.prediction,
                           vp.definitions.roles.utility,
                           vp.definitions.roles.test,
                           name="roles_enum"
                           ))
    # Who
    author_ivorn = Column(sql.String)
    author_datetime = Column(sql.DateTime(timezone=True))
    # Finally, the raw XML
    xml = Column(sql.String)

    @staticmethod
    def from_etree(root, received=pytz.UTC.localize(datetime.utcnow())):
        """
        Init a Voevent row from an LXML etree loaded with voevent-parse
        """
        row = Voevent(ivorn=root.attrib['ivorn'],
                      role=root.attrib['role'],
                      xml=vp.dumps(root),
                      received=received,
                      )
        row.author_datetime = _grab_xpath(root, 'Who/Date',
                                          converter=iso8601.parse_date)
        row.author_ivorn = _grab_xpath(root, 'Who/AuthorIVORN')
        return row

    def to_odict(self):
        """
        Returns an OrderedDict representation of the Voevent row.
        """
        colnames = [c.name for c in self.__table__.columns]
        return OrderedDict( ((col , getattr(self, col)) for col in colnames))


    def _reformatted_prettydict(self, valformat=str):
        pd = self.prettydict()
        return '\n'.join(("{}={}".format(k,valformat(v)) for k,v in pd.iteritems()))

    def __repr__(self):
        od = self.to_odict()
        content = ',\n'.join(("{}={}".format(k,repr(v)) for k,v in od.iteritems()))
        return """<Voevent({})>""".format(content)

    def __str__(self):
        od = self.to_odict()
        od.pop('xml')
        content = ',\n    '.join(("{}={}".format(k,str(v)) for k,v in od.iteritems()))
        return """<Voevent({})>""".format(content)
