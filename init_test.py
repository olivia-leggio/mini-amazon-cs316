from database import init_db
from database import db_session
from models import *
print("Initialize Test Database")

init_db()

toys = Category('Toys')
db_session.add(toys)

household = Category('Household')
db_session.add(household)

item = Item('Batman','DC','Black',2,'A toy',None)
assoc = InCat()
assoc.cat = toys
item.categories.append(assoc)
db_session.add(item)

item = Item('Cup','Solo','Red',1,'A cup',None)
assoc = InCat()
assoc.cat = household
item.categories.append(assoc)
db_session.add(item)

user = User('alice@gmail.com','pass','Alice',0,'User','1 University Dr','Durham',27708,'NC')
db_session.add(user)

house = Warehouse('23 University Dr','Durham',27708,'NC',100)
db_session.add(house)

db_session.commit()

print("DONE!")
