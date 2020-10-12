from sqlalchemy import Column, Integer, String, Table, ForeignKey, CheckConstraint, Text, Float, DateTime
from sqlalchemy.orm import relationship, backref
from database import Base

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=False)
    brand = Column(String(20), unique=False)
    color = Column(String(20), unique=False)
    size = Column(Integer, unique=False)
    desc = Column(Text, unique=False)
    imgurl = Column(Text, unique=False,nullable=True)
    categories = relationship("InCat",back_populates="item",cascade="all, delete-orphan")
    reviews = relationship("Review",back_populates="item",cascade="all, delete-orphan")
    listings = relationship("Listing",back_populates="item",cascade="all, delete-orphan")

    def __init__(self, name=None, brand=None, color=None, size=None,desc=None,img=None):
        self.name = name
        self.brand = brand
        self.color = color
        self.size = size
        self.desc = desc
        self.imgurl = img

    def __repr__(self):
        return '<Item %r>' % (self.model)

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True)
    items = relationship("InCat",back_populates="cat",cascade="all, delete-orphan")

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % (self.model)

class InCat(Base):
    __tablename__ = 'inCategory'
    item_id = Column(Integer,ForeignKey('items.id'),primary_key=True)
    cat_id = Column(Integer,ForeignKey('categories.id'),primary_key=True)
    item = relationship("Item",back_populates="categories")
    cat = relationship("Category",back_populates="items")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(20), unique=True)
    name = Column(String(30), unique=False)
    password = Column(String(20), unique=False)
    balance = Column(Float, unique = False)
    type = Column(String(20), unique=False)
    street = Column(String(20), unique=False)
    city = Column(String(20), unique=False)
    zip = Column(Integer, unique=False)
    state = Column(String(2), unique=False)
    reviews = relationship("Review",back_populates="user",cascade="all, delete-orphan")
    listings = relationship("Listing",back_populates="seller",cascade="all, delete-orphan")
    __table_args__ = (
        CheckConstraint('type="User" OR type="Seller" OR type="Manager"'),{}
        )

    def __init__(self, email=None,password=None,name=None,balance=None,type="User",street=None,city=None,zip=None,state=None):
        self.email = email
        self.password = password
        self.name = name
        self.balance = balance
        self.type = type
        self.street = street
        self.city = city
        self.zip = zip
        self.state = state

class Warehouse(Base):
    __tablename__ = 'warehouses'
    id = Column(Integer, primary_key=True)
    street = Column(String(20), unique=False)
    city = Column(String(20), unique=False)
    zip = Column(Integer, unique=False)
    state = Column(String(2), unique=False)
    capacity = Column(Integer, unique=False)
    listings = relationship("Listing",back_populates="warehouse",cascade="all, delete-orphan")

    def __init__(self,street=None,city=None,zip=None,state=None,capacity=None):
        self.street = street
        self.city = city
        self.zip = zip
        self.state = state
        self.capacity = capacity

class Review(Base):
    __tablename__ = 'reviews'
    user_id = Column(Integer,ForeignKey('users.id'),primary_key=True)
    item_id = Column(Integer,ForeignKey('items.id'),primary_key=True)
    text = Column(Text, unique=False)
    date = Column(DateTime, unique=False)
    item_rating = Column(Integer, unique=False)
    user = relationship("User",back_populates="reviews",uselist=False)
    item = relationship("Item",back_populates="reviews",uselist=False)

    def __init__(self,text=None,date=None,item_rating=None):
        self.text = text
        self.date = date
        self.item_rating = item_rating

class Listing(Base):
    __tablename__ = 'listings'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer,ForeignKey('items.id'))
    seller_id = Column(Integer,ForeignKey('users.id'))
    warehouse_id = Column(Integer,ForeignKey('warehouses.id'))
    price = Column(Float, unique = False)
    amount = Column(Integer, unique = False)
    seller = relationship("User",back_populates="listings",uselist=False)
    item = relationship("Item",back_populates="listings",uselist=False)
    warehouse = relationship("Warehouse",back_populates="listings",uselist=False)

    def __init__(self,price=None,amount=None):
        self.price = price
        self.amount = amount
