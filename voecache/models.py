from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, Column, String

Base = declarative_base()

class Voevent(Base):
    __tablename__ = 'voevent'
    id = Column(Integer, primary_key=True)
    ivorn = Column(String, nullable=False)
    packet = Column(String)
    
    def __repr__(self):
        return "<Voevent(ivorn='{}')>".format(self.ivorn)
