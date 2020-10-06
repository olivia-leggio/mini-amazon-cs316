from database import init_db
from database import db_session
from models import *
print("Initialize Test Database")

init_db()

toys = Category('Toys')
db_session.add(toys)

household = Category('Household')
db_session.add(household)

item = Item('Batman','DC','Black','2')
assoc = InCat()
assoc.category = toys
item.categories.append(assoc)
db_session.add(item)

item = Item('Cup','Solo','Red','1')
assoc = InCat()
assoc.category = household
item.categories.append(assoc)
db_session.add(item)

db_session.commit()

print("DONE!")
