from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship, backref
from database import Base

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=False)
    brand = Column(String(20), unique=False)
    color = Column(String(20), unique=False)
    size = Column(Integer, unique=False)
    categories = relationship("InCat", back_populates="item")

    def __init__(self, name=None, brand=None, color=None, size=None):
        self.name = name
        self.brand = brand
        self.color = color
        self.size = size

    def __repr__(self):
        return '<Item %r>' % (self.model)

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True)
    items = relationship("InCat", back_populates="category")

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % (self.model)

class InCat(Base):
    __tablename__ = 'inCategory'
    item_id = Column(Integer,ForeignKey('items.id'),primary_key=True)
    cat_id = Column(Integer,ForeignKey('categories.id'),primary_key=True)
    item = relationship("Item",back_populates="categories")
    category = relationship("Category",back_populates="items")
