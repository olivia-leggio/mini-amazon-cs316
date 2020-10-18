from flask import Flask, request, redirect, url_for, render_template
from models import *
from database import db_session, engine
from datetime import datetime

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/browse')
def browse():
  cat = request.args.get('cat','ALL')
  incats = InCat.query.join(Category).filter_by(name=cat)

  sql_item_in_cat = '''SELECT *
                    FROM items I
                    WHERE EXISTS (SELECT * FROM categories C, inCategory A
                                  WHERE I.id=A.item_id and C.id=A.cat_id
                                  and C.name = :1)'''

  items = engine.execute(sql_item_in_cat,cat)
  if cat == 'ALL':
      incats = InCat.query.all()
      items = Item.query.all()

  return render_template(
    'browse.html',
    cats = Category.query.all(),
    incats = incats,
    items = items
  )

@app.route('/add_item')
def add_item():
  name = request.args.get("name")
  brand = request.args.get("brand")
  color = request.args.get("color")
  size = request.args.get("size")
  desc = request.args.get("desc")
  cat = request.args.get("cat")

  item = Item(name, brand, color, size,desc,None)
  category = Category.query.filter_by(name=cat).first()
  assoc = InCat()
  assoc.cat = category
  item.categories.append(assoc)
  db_session.add(item)
  db_session.commit()

  return redirect(url_for('browse'))

@app.route('/test')
def test():
    return render_template(
        'test.html',
        users = User.query.all(),
        sellers = User.query.filter_by(type="Seller"),
        warehouses = Warehouse.query.all(),
        cats = Category.query.all(),
        incats = InCat.query.all(),
        items = Item.query.all(),
        reviews = Review.query.all(),
        listings = Listing.query.all(),
        carts = Cart.query.all(),
        orders = Order.query.all()
    )

@app.route('/delete_item')
def delete_item():
    item_id = request.args.get("item_id")
    item = Item.query.filter_by(id=item_id).first()
    db_session.delete(item)
    db_session.commit()

    return redirect(url_for('test'))

@app.route('/new_cat')
def new_cat():
    name = request.args.get("name")
    cat = Category(name)
    db_session.add(cat)
    db_session.commit()

    return redirect(url_for('test'))

@app.route('/delete_cat')
def delete_cat():
    cat_id = request.args.get("cat_id")
    cat = Category.query.filter_by(id=cat_id).first()
    db_session.delete(cat)
    db_session.commit()

    return redirect(url_for('test'))

@app.route('/add_user')
def add_user():
  name = request.args.get("name")
  email = request.args.get("email")
  password = request.args.get("password")
  type = request.args.get("type")
  street = request.args.get("street")
  city = request.args.get("city")
  zip = request.args.get("zip")
  state = request.args.get("state")

  user = User(email,password,name,0,type,street,city,zip,state)
  db_session.add(user)
  db_session.commit()

  return redirect(url_for('test'))

@app.route('/new_house')
def new_house():
  capacity = request.args.get("capacity")
  street = request.args.get("street")
  city = request.args.get("city")
  zip = request.args.get("zip")
  state = request.args.get("state")

  house = Warehouse(street,city,zip,state,capacity)
  db_session.add(house)
  db_session.commit()

  return redirect(url_for('test'))

@app.route('/add_review')
def add_review():
    user_id = request.args.get("user_id")
    item_id = request.args.get("item_id")
    seller_id = request.args.get("seller_id")
    text = request.args.get("text")
    item_rating = request.args.get("item_rating")

    review = Review(text,datetime.now(),item_rating,None)

    if seller_id != 'NONE':
        seller_rating = request.args.get("seller_rating")
        review = Review(text,datetime.now(),item_rating,seller_rating)
        review.seller = User.query.filter_by(id=seller_id).first()

    review.item = Item.query.filter_by(id=item_id).first()
    review.user = User.query.filter_by(id=user_id).first()

    db_session.add(review)
    db_session.commit()

    return redirect(url_for('test'))

@app.route('/add_listing')
def add_listing():
    seller_id = request.args.get("seller_id")
    item_id = request.args.get("item_id")
    wh_id = request.args.get("warehouse_id")
    price = request.args.get("price")
    amount = request.args.get("amount")

    listing = Listing(price,amount)
    listing.item = Item.query.filter_by(id=item_id).first()
    listing.seller = User.query.filter_by(type="Seller").filter_by(id=seller_id).first()
    listing.warehouse = Warehouse.query.filter_by(id=wh_id).first()

    db_session.add(listing)
    db_session.commit()

    return redirect(url_for('test'))

@app.route('/add_cart')
def add_cart():
    user_id = request.args.get("user_id")
    listing_id = request.args.get("listing_id")
    amount = request.args.get("amount")

    cart = Cart(amount)
    cart.listing = Listing.query.filter_by(id=listing_id).first()
    cart.user = User.query.filter_by(id=user_id).first()

    db_session.add(cart)
    db_session.commit()

    return redirect(url_for('test'))

@app.route('/process_checkout')
def process_checkout():
    cart_id = request.args.get("cart_id")
    cart = Cart.query.filter_by(id=cart_id).first()
    order = Order(datetime.now(),False,cart.listing.price,cart.amount)
    order.user = cart.user
    order.seller = cart.listing.seller
    order.item = cart.listing.item
    order.warehouse = cart.listing.warehouse

    cart.listing.amount = cart.listing.amount - cart.amount
    cart.listing.seller.balance = cart.listing.seller.balance + cart.listing.price*cart.amount
    cart.user.balance = cart.user.balance - cart.listing.price*cart.amount

    db_session.add(order)
    db_session.delete(cart)
    db_session.commit()
    return redirect(url_for('test'))


@app.route('/account')
def account():
    return render_template('account.html')

@app.route('/wallet')
def wallet():
    return render_template('wallet.html')

@app.route('/history')
def orderHistory():
    return render_template('order-history.html')

@app.route('/cart')
def cart():
    logged_in_id = id
    sql_get_cart = '''SELECT I.imgurl AS img, I.name AS name, L.price AS price, C.amount AS amount
                      FROM carts C, listings L, items I
                      WHERE C.user_id = {} AND C.listing_id = L.id
                      AND L.item_id = I.id'''.format(logged_in_id)

    cart_items = engine.execute(sql_get_cart)
    
    return render_template('cart.html', items = cart_items)

@app.route('/search-results')
def results():
    query = request.args.get("searchtext")
    
    return render_template(
        'results.html',
        results = Item.query.filter(Item.name.like(query))       
    )

@app.route('/item')
def items():
    
    return render_template('item.html')

if __name__ == "__main__":
    app.run()
