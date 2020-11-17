from csv import DictReader
from database import db_session
from models import *

# open file in read mode
with open('users_add.csv', 'r') as read_obj:
    # pass the file object to reader() to get the reader object
    csv_reader = DictReader(read_obj)
    # Iterate over each row in the csv using reader object
    for row in csv_reader:
        user = User(row['email'],row['name'],row['password'],row['balance'],row['type'],row['street'],row['city'],row['zip'],row['state'])
        db_session.add(user)


    db_session.commit()
    print("done")
