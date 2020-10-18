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

bat = Item('Batman','DC','Black',2,'Batmtan Action Figure',None)
assoc = InCat()
assoc.cat = toys
bat.categories.append(assoc)
db_session.add(bat)

drums = Item('MiniDrums','Hasbro','Red',5,'Mini drum set',None)
assoc = InCat()
assoc.cat = toys
drums.categories.append(assoc)
db_session.add(drums)

cup = Item('Cup','Solo','Red',1,'A cup',None)
assoc = InCat()
assoc.cat = household
cup.categories.append(assoc)
db_session.add(cup)

alice = User('alice@gmail.com','pass','Alice',100,'User','1 University Dr','Durham',27708,'NC')
db_session.add(alice)

bob = User('bob@gmail.com','12345','Bob',100,'Seller','440 Chapel Dr','Durham',27708,'NC')
db_session.add(bob)

carol = User('carol@gmail.com','superman','Carol',100,'Manager','440 Chapel Dr','Durham',27708,'NC')
db_session.add(carol)

dan = User('dan@gmail.com','joker','Dan',100,'Seller','1 University Dr','Durham',27708,'NC')
db_session.add(dan)

eve = User('eve@gmail.com','ice20','Eve',100,'User','127 University Dr','Durham',27708,'NC')
db_session.add(eve)

frank = User('frank@gmail.com','hello','Frank',100,'User','200 University Dr','Durham',27708,'NC')
db_session.add(frank)

gary = User('gary@gmail.com','goodbye','Gary',100,'Manager','200 University Dr','Durham',27708,'NC')
db_session.add(gary)

review = Review('I love Batman!!!',datetime.now(),5,None)
review.item = bat
review.user = alice
db_session.add(review)

review = Review('This cup leaks',datetime.now(),1,1)
review.item = cup
review.user = alice
review.seller = bob
db_session.add(review)

house1 = Warehouse('23 University Dr','Durham',27708,'NC',100)
db_session.add(house1)

house2 = Warehouse('300 Franklin St','Chapel Hill',27514,'NC',50)
db_session.add(house2)

l1 = Listing(19.99,20)
l1.item = bat
l1.seller = bob
l1.warehouse = house1
db_session.add(l1)

l2 = Listing(39.99,5)
l2.item = drums
l2.seller = dan
l2.warehouse = house2
db_session.add(l2)

c1 = Cart(2)
c1.listing = l1
c1.user = alice
db_session.add(c1)

c2 = Cart(1)
c2.listing = l2
c2.user = dan
db_session.add(c2)

o1 = Order(datetime.now(),True,7.50,20)
o1.user = bob
o1.seller = bob
o1.item = bat
o1.warehouse = house1
db_session.add(o1)

o2 = Order(datetime.now(),False,14.99,1)
o2.user = dan
o2.seller = bob
o2.item = bat
o2.warehouse = house1
db_session.add(o2)

ml = ManagerLocation()
ml.manager = carol
ml.warehouse = house1
db_session.add(ml)

ml = ManagerLocation()
ml.manager = gary
ml.warehouse = house2
db_session.add(ml)

db_session.commit()

print("DONE!")
