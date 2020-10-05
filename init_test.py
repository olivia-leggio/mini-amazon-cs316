from database import init_db
from database import db_session
from models import Item
print("Initialize Test Database")

init_db()

item = Item('Batman','DC','Black','2')
db_session.add(item)

item = Item('Cup','Solo','Red','1')
db_session.add(item)

db_session.commit()

print("DONE!")
