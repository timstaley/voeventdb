import voeventparse as vp
with open('voeventcache/tests/resources/SWIFT_bat_position_v2.0_example.xml') as f:
                v = vp.load(f)
import voeventcache
from voeventcache.database.models import Voevent
row = Voevent.from_etree(v)
from voeventcache.tests.config import testdb_empty_url
import sqlalchemy
engine = sqlalchemy.engine.create_engine(testdb_empty_url)
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
s = Session()
print s.query(Voevent).all()
s.add(row)
s.commit()
# engine.url
# engine.dispose()
