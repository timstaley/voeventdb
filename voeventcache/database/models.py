from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, Column, String, DateTime
import voeventparse as vp
from datetime import datetime
import iso8601
import pytz

Base = declarative_base()


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
    id = Column(Integer, primary_key=True)
    ivorn = Column(String, nullable=False, unique=True, index=True)
    received = Column(
        DateTime(timezone=True), nullable=False,
        doc="Records when the packet was loaded into the database"
    )

    # Who section:
    # We expect these to be present in most if not all packets, but
    # technically they can be absent and still VOE2-schema-valid.
    author_ivorn = Column(String)
    author_datetime = Column(DateTime(timezone=True))

    #Define the XML last - makes some command-line queries easier to view!
    xml = Column(String)

    def __repr__(self):
        return """
        <Voevent(ivorn={ivorn},
                 received={recv},
                 author_date={adate}
                 )
        >""".format(ivorn=self.ivorn,
                    recv=repr(self.received),
                    adate=repr(self.author_datetime))

    def __str__(self):
        return """
        <Voevent(ivorn={ivorn},
                 received={recv},
                 author_date={adate}
                 )
        >""".format(ivorn=self.ivorn,
                    recv=(self.received),
                    adate=(self.author_datetime))

    @staticmethod
    def from_etree(root, received=pytz.UTC.localize(datetime.utcnow())):
        """
        Init a Voevent row from an LXML etree loaded with voevent-parse
        """
        if root.xpath('Who/Date'):
            author_datetime = iso8601.parse_date(root.Who.Date.text)
        else:
            author_datetime = None

        row = Voevent(ivorn=root.attrib['ivorn'],
                      xml=vp.dumps(root),
                      received=received,
                      author_datetime=author_datetime,
                      )
        return row
