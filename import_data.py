from database import db_session, init_db
from models import *
from csv import DictReader
from random import randrange
from datetime import datetime
from sqlalchemy.sql import func

init_db()

user = User('admin@gmail.com','ADMIN','admin',0,'ADMIN','440 Chapel Dr','Durham',27708,'NC')
db_session.add(user)
db_session.commit()

with open('init_data/users_add.csv', 'r') as read_obj:
    # pass the file object to reader() to get the reader object
    csv_reader = DictReader(read_obj)
    # Iterate over each row in the csv using reader object
    for row in csv_reader:
        user = User(row['email'],row['password'],row['name'],row['balance'],row['type'],row['street'],row['city'],row['zip'],row['state'])
        db_session.add(user)


    db_session.commit()
    print("imported users")

with open('init_data/cats_add.csv', 'r') as read_obj:
    # pass the file object to reader() to get the reader object
    csv_reader = DictReader(read_obj)
    # Iterate over each row in the csv using reader object
    for row in csv_reader:
        cat = Category(row['categories'])
        db_session.add(cat)


    db_session.commit()
    print("imported categories")

with open('init_data/items_add.csv', 'r') as read_obj:
    # pass the file object to reader() to get the reader object
    csv_reader = DictReader(read_obj)
    # Iterate over each row in the csv using reader object
    for row in csv_reader:
        catname = row['categories']
        cat = Category.query.filter_by(name=catname).first()
        item = Item(row['name'],row['brand'],row['desc'],row['imgurl'])
        assoc = InCat()
        assoc.cat = cat
        assoc.item = item
        item.categories.append(assoc)
        cat.items.append(assoc)
        db_session.add(item)

    db_session.commit()
    print("imported items")

managers = User.query.filter_by(type="Manager")

for m in managers:
    whouse = Warehouse(m.street,m.city,m.zip,m.state,randrange(6000,15000,1000))
    ml = ManagerLocation()
    ml.manager = m
    ml.warehouse = whouse
    whouse.manager.append(ml)
    m.warehouse = ml
    db_session.add(whouse)
    db_session.add(ml)

db_session.commit()
print("imported warehouses")

with open('init_data/listings_add.csv', 'r') as read_obj:
    # pass the file object to reader() to get the reader object
    csv_reader = DictReader(read_obj)
    # Iterate over each row in the csv using reader object
    for row in csv_reader:
        item_id = row['item_id']
        item = Item.query.filter_by(id=item_id).first()
        seller_id = row['seller_id']
        seller = User.query.filter_by(id=seller_id).first()
        whouse_id = randrange(1,21)
        whouse = Warehouse.query.filter_by(id=whouse_id).first()
        price = row['price']
        amount = row['amount']

        lst = Listing(price,amount)
        lst.item = item
        lst.seller = seller
        lst.warehouse = whouse
        db_session.add(lst)

    db_session.commit()
    print("imported listings")

with open('init_data/reviews_add.csv', 'r') as read_obj:
    # pass the file object to reader() to get the reader object
    csv_reader = DictReader(read_obj)
    # Iterate over each row in the csv using reader object
    for row in csv_reader:
        product_name = row['product_name']
        item = Item.query.filter_by(name=product_name).first()

        if item is None:
            continue

        text = row['text']
        rating = row['rating']

        user_id = randrange(125,500)
        user = User.query.filter_by(id=user_id).first()

        seller_id = randrange(22,121)
        seller = User.query.filter_by(id=seller_id).first()

        review = Review(text,datetime.now(),rating,randrange(1,6))
        review.item = item
        review.user = user
        review.seller = seller
        user.reviews_buy.append(review)
        seller.reviews_sell.append(review)
        item.reviews.append(review)
        db_session.add(review)

    db_session.commit()
    print("imported reviews")

buyers = User.query.filter_by(type="User")

for b in buyers:
    lst = Listing.query.order_by(func.random()).first()
    amount = randrange(1,5)
    cart = Cart(amount)
    cart.user = b
    cart.listing = lst
    db_session.add(cart)

db_session.commit()
print("generated carts")

warehouses = Warehouse.query.all()

for w in warehouses:
    for n in range(1,25):
        lst = Listing.query.order_by(func.random()).first()
        amount = randrange(1,6)

        o1 = Order(datetime.now(),True,lst.price,amount)
        o1.user = User.query.order_by(func.random()).first()
        o1.seller = lst.seller
        o1.item = lst.item
        o1.warehouse = lst.warehouse
        db_session.add(o1)

    for k in range(1,25):
        lst = Listing.query.order_by(func.random()).first()
        amount = randrange(1,6)

        o1 = Order(datetime.now(),False,lst.price,amount)
        o1.user = User.query.order_by(func.random()).first()
        o1.seller = lst.seller
        o1.item = lst.item
        o1.warehouse = lst.warehouse
        db_session.add(o1)

db_session.commit()
print("generated orders")
