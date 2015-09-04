from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, Column, String, DateTime
import voeventparse as vp

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
    xml = Column(String)
    received = Column(
        DateTime(timezone=True), nullable=False,
        doc="Records when the packet was loaded into the database"
    )

    # Who section:
    # We expect these to be present in most if not all packets, but
    # technically they can be absent and still VOE2-schema-valid.
    author_ivorn = Column(String)
    author_datetime = Column(DateTime(timezone=True))

    def __repr__(self):
        return "<Voevent(ivorn='{}')>".format(self.ivorn)

    @staticmethod
    def from_etree(root):
        """
        Init a Voevent row from an LXML etree loaded with voevent-parse
        """
        row = Voevent(ivorn=root.attrib['ivorn'],
                              xml=vp.dumps(root),
                              received=root.Who.Date.text)
        return row
