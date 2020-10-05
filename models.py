from sqlalchemy import Column, Integer, String
from database import Base

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=False)
    brand = Column(String(20), unique=False)
    color = Column(String(20), unique=False)
    size = Column(Integer, unique=False)

    def __init__(self, name=None, brand=None, color=None, size=None):
        self.name = name
        self.brand = brand
        self.color = color
        self.size = size

    def __repr__(self):
        return '<Item %r>' % (self.model)
