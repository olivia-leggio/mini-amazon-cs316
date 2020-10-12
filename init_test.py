from database import init_db
from database import db_session
from models import *
from datetime import datetime
print("Initialize Test Database")

init_db()

toys = Category('Toys')
db_session.add(toys)

household = Category('Household')
db_session.add(household)

bat = Item('Batman','DC','Black',2,'A toy',None)
assoc = InCat()
assoc.cat = toys
bat.categories.append(assoc)
db_session.add(bat)

item = Item('Cup','Solo','Red',1,'A cup',None)
assoc = InCat()
assoc.cat = household
item.categories.append(assoc)
db_session.add(item)

alice = User('alice@gmail.com','pass','Alice',0,'User','1 University Dr','Durham',27708,'NC')
db_session.add(alice)

bob = User('bob@gmail.com','12345','Bob',0,'Seller','440 Chapel Dr','Durham',27708,'NC')
db_session.add(bob)

review = Review('I love Batman!!!',datetime.now(),5)
review.item = bat
review.user = alice
db_session.add(review)

house = Warehouse('23 University Dr','Durham',27708,'NC',100)
db_session.add(house)

l1 = Listing(19.99,20)
l1.item = bat
l1.seller = bob
l1.warehouse = house
db_session.add(l1)

db_session.commit()

print("DONE!")
