from flask import Flask, request, redirect, url_for, render_template, session
from models import *
from database import db_session, engine
from datetime import datetime
import secrets

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = secrets.token_urlsafe(15)

def Name():
    return session.get('NAME')

def Type():
    return session.get('TYPE')


@app.route('/')
def index():
    return render_template('index.html', categories = Category.query.all(), name = Name(), type = Type())

@app.route('/databaseview')
def databaseview():
    return render_template('databaseview.html', values=User.query.all())


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        input_email = request.form['username']
        input_pw = request.form['password']
        user = User.query.filter_by(email = input_email).first()
        if user is None or user.password != input_pw:
            error = 'Invalid Credentials. Please try again.'
            return render_template('login.html', error=error)
        else:
            session["USERID"] = user.id
            session["NAME"] = user.name
            session["TYPE"] = user.type
            return redirect(url_for('index'))

    # If you get here from a get request, render the page unless already logged in
    if session.get('USERID') is None: 
        return render_template('login.html')
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('NAME',None)
    session.pop('TYPE',None)
    session.pop('USERID',None)
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        # Get information from form if you reach here from a POST request
        req = request.form
        email = req['email']
        name = req['name']
        password = req['password']
        street = req['street']
        city = req['city']
        state = req['state']
        zipcode = int(req['zip'])
        balance = float(0)
        type_ = 'User'

        confirm_email = req['confirm_email']
        confirm_password = req['confirm_password']
        
        if email != confirm_email:
            error = 'Emails do not match'
            return render_template('signup.html', error=error)

        exists = User.query.filter_by(email=email).first()
        if exists:
            error = 'An account with this email already exists. Login with your existing email or use a different one.'
            return render_template('signup.html', error=error)
            
        if password != confirm_password:
            error = 'Passwords do not match'
            return render_template('signup.html', error=error)

        if len(str(zipcode)) != 5:
            error = 'Please enter a valid zipcode'
            return render_template('signup.html', error=error)

        new_user = User(email, password, name, balance, type_, street, city, zipcode, state)
        db_session.add(new_user)
        db_session.commit()

        session["USERID"] = new_user.id
        session["NAME"] = new_user.name
        session["TYPE"] = new_user.type

        return redirect(url_for('index'))

    # If you get here from a get request, render the page unless already logged in
    if session.get('USERID') is None: 
        return render_template('signup.html')
    else:
        return redirect(url_for('index'))

@app.route('/forgotpassword')
def forgotpassword():
    return render_template('forgotpassword.html')

@app.route('/browse')
def browse():
  me_id = session.get("USERID")
  print(me_id)
  if me_id is None:
      return redirect(url_for('login'))

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
    items = items,
    me = User.query.filter_by(id=me_id).first(),
    name = Name(), type = Type())

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

@app.route('/denied')
def denied():
     return render_template('denied.html')

@app.route('/warehouse')
def warehouse():
    me_id = session.get("USERID")
    if me_id is None:
        return redirect(url_for('login'))

    me = User.query.filter_by(id=me_id).first()

    if me.type != 'Manager':
        return redirect(url_for('denied'))

    past_orders = Order.query.filter_by(warehouse_id=me.warehouse.warehouse_id).filter_by(delivered=True)
    new_orders = Order.query.filter_by(warehouse_id=me.warehouse.warehouse_id).filter_by(delivered=False)

    return render_template(
      'warehouse.html',
      past_orders = past_orders,
      new_orders = new_orders,
      me = me,
      warehouse = Warehouse.query.filter_by(id=me.warehouse.warehouse_id).first(),
      name = Name(), type = Type()
    )

@app.route('/markdelivered')
def markdelivered():
    order_id = request.args.get('order_id')
    order = Order.query.filter_by(id=order_id).first()
    order.delivered = True

    db_session.commit()

    return redirect(url_for('warehouse'))

@app.route('/return_order')
def return_order():
    order_id = request.args.get('order_id')
    order = Order.query.filter_by(id=order_id).first()
    admin = User.query.filter_by(type="ADMIN").first()
    money = order.price * order.amount

    order.user.balance = order.user.balance + money
    order.seller.balance = order.seller.balance - (0.9 * money)
    admin.balance = admin.balance - (0.1 * money)

    db_session.delete(order)
    db_session.commit()
    return redirect(url_for('warehouse'))

@app.route('/account')
def account():
    me_id = session.get('USERID')
    if me_id is None:
        return redirect(url_for('login'))

    user = User.query.filter_by(id = me_id).first()

    return render_template('account.html', user = user, name = Name(), type = Type())

@app.route('/update-account')
def update_account():
    me_id = session.get("USERID")
    if me_id is None:
        return redirect(url_for('login'))

    newEmail = request.args.get("updatedEmail")
    newPassword = request.args.get("updatedPassword")
    newStreet = request.args.get("updatedStreet")
    newCity = request.args.get("updatedCity")
    newState = request.args.get("updatedState")
    newZip = request.args.get("updatedZip")

    user = User.query.filter_by(id = me_id).first()
    currState = user.state

    if (len(newEmail) != 0):
        user.email = newEmail

    if (len(newPassword) != 0):
        user.password = newPassword

    if (len(newStreet) != 0):
        user.street = newStreet

    if (len(newCity) != 0):
        user.city = newCity

    if (newState == None):
        user.state = currState
    else:
        user.state = newState

    if (len(newZip) != 0):
        user.zip = newZip

    db_session.commit()

    return redirect(url_for('account'))
    #return render_template('testupdates.html', email = newEmail, password = newPassword, street = newStreet, city = newCity, state = newState, zipcode = newZip)

@app.route('/wallet')
def wallet():
    me_id = session.get("USERID")
    if me_id is None:
        return redirect(url_for('login'))

    sql_get_balance = '''SELECT balance
                         FROM users
                         WHERE id = {}'''.format(me_id)

    balance = engine.execute(sql_get_balance)

    return render_template('wallet.html', balance = balance, name = Name(), type = Type())

@app.route('/update_balance')
def update_balance():
    me_id = session.get("USERID")
    if me_id is None:
        return redirect(url_for('login'))

    to_add = request.args.get("added_balance")

    sql_update_balance = '''UPDATE users
                            SET balance = balance + {}
                            WHERE id = {}'''.format(to_add, me_id)

    engine.execute(sql_update_balance)

    return redirect(url_for('wallet'))

@app.route('/history')
def orderHistory():
    me_id = session.get("USERID")
    if me_id is None:
        return redirect(url_for('login'))

    sql_get_history = '''SELECT I.name AS name, delivered, amount
                         FROM orders O, items I
                         WHERE user_id = {} AND item_id = I.id'''.format(me_id)

    history_items = engine.execute(sql_get_history)

    return render_template('order-history.html', items = history_items, name = Name(), type = Type())

@app.route('/cart')
def cart():
    me_id = session.get("USERID")
    if me_id is None:
        return redirect(url_for('login'))

    sql_get_cart = '''SELECT I.imgurl AS img, I.name AS name, L.price AS price, C.amount AS amount, C.id AS id
                      FROM carts C, listings L, items I
                      WHERE C.user_id = {} AND C.listing_id = L.id
                      AND L.item_id = I.id'''.format(me_id)

    cart_items = engine.execute(sql_get_cart)
    count_items = engine.execute(sql_get_cart)
    rows = [r[0] for r in count_items]
    num = len(rows)
    cart_copy = engine.execute(sql_get_cart)

    return render_template('cart.html', items = cart_items, items2 = cart_copy, num = num, name = Name(), type = Type())

@app.route('/checkout', methods = ["GET", "POST"])
def checkout():
    if request.method == 'POST':
        checkout_list = request.form.getlist("cartItem")
    
    for id in checkout_list:
        cart_id = id
        cart = Cart.query.filter_by(id=cart_id).first()
        order = Order(datetime.now(),False,cart.listing.price,cart.amount)
        order.user = cart.user
        order.seller = cart.listing.seller
        order.item = cart.listing.item
        order.warehouse = cart.listing.warehouse

        admin = User.query.filter_by(type="ADMIN").first()
        money = cart.listing.price * cart.amount

        cart.listing.amount = cart.listing.amount - cart.amount

        cart.user.balance = cart.user.balance - money
        cart.listing.seller.balance = cart.listing.seller.balance + (0.9 * money)
        admin.balance = admin.balance + (0.1 * money)

        db_session.add(order)
        db_session.delete(cart)
        db_session.commit()
    
    return render_template("finished-order.html", name = Name(), type = Type())

@app.route('/delete-cart', methods = ["GET", "POST"])
def delete_cart():
    if request.method == "POST":
        delete_list = request.form.getlist("deleteId")

    for id in delete_list:
        cart_id = id
        cart = Cart.query.filter_by(id = cart_id).first()
        
        db_session.delete(cart)
        db_session.commit()

    return redirect(url_for("cart"))

@app.route('/search-results')
def results():
    query = request.args.get("searchtext")
    category = request.args.get('search-cats','ALL')

    sql_items_cat = '''SELECT *
                    FROM items I
                    WHERE I.name LIKE '%{}%' and EXISTS (SELECT * FROM categories C, inCategory A
                                  WHERE I.id=A.item_id and C.id=A.cat_id
                                  and C.name = :1)'''.format(query)

    results = engine.execute(sql_items_cat,category)
    
    sql_items_all = '''SELECT *
                         FROM items I
                         WHERE I.name LIKE '%{}%' '''.format(query)
    results1 = engine.execute(sql_items_all)

    if category == 'ALL':
      results = results1

    return render_template(
        'results.html',
        results = results, categories = Category.query.all(), name = Name(), type = Type()
        )

@app.route('/item/')
def items():
    ids = request.args.get("item_id")
  
    return render_template('item.html', 
        items = Item.query.filter_by(id=ids).first(),
        cats = InCat.query.filter_by(item_id=ids).first(),
        name = Name(), 
        type = Type()
        )

@app.route('/seller')
def  sellerpage():
    me_id = session.get("USERID")
    if me_id is None:
        return redirect(url_for('login'))

    me = User.query.filter_by(id=me_id).first()

    if me.type != 'Seller':
        return redirect(url_for('denied'))

    return render_template('seller.html',
        seller = me,
        listings = Listing.query.filter_by(seller_id=me_id).all(),
        warehouses = Warehouse.query.all(),
        cats = Category.query.all(),
        items = Item.query.all(),
        name = Name(), type = Type()
        )

@app.route('/test')
def test():
    if Type() != "ADMIN":
        return redirect(url_for('denied'))

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
        orders = Order.query.all(),
        name = Name(), type = Type()
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
    me_id = session.get("USERID")
    if me_id is None:
        return redirect(url_for('login'))

    me = User.query.filter_by(id=me_id).first()

    if me.type != 'Seller':
        return redirect(url_for('denied'))

    seller_id = me_id
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

    admin = User.query.filter_by(type="ADMIN").first()
    money = cart.listing.price * cart.amount

    cart.listing.amount = cart.listing.amount - cart.amount

    cart.user.balance = cart.user.balance - money
    cart.listing.seller.balance = cart.listing.seller.balance + (0.9 * money)
    admin.balance = admin.balance + (0.1 * money)

    db_session.add(order)
    db_session.delete(cart)
    db_session.commit()
    return redirect(url_for('test'))

if __name__ == "__main__":
    app.run()
