from database import db_session
from models import *

user = User('admin@gmail.com','ADMIN','admin',0,'ADMIN','440 Chapel Dr','Durham',27708,'NC')
db_session.add(user)
db_session.commit()
