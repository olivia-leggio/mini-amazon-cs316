from flask import Flask, request, redirect, url_for, render_template, session, flash
from models import *
from database import db_session, engine
from datetime import datetime
import secrets
from flask_mail import Mail, Message
from sqlalchemy.sql import func, text

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='miniamazongroup20@gmail.com',
    MAIL_PASSWORD='ilovecs12!'
)

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = secrets.token_urlsafe(15)
mail = Mail(app)

def Name():
    return session.get('NAME')

def Type():
    return session.get('TYPE')

def ID():
    return session.get('USERID')

def Cats():
    return Category.query.all()

regions = {
    "AK": 10,"AL": 3,"AR": 7, "AZ": 8, "CA": 9, "CO": 8, "CT":0, "DC":2, "DE":1,
     "FL":3, "GA":3, "HI":11, "IA":5, "ID":8, "IL":6, "IN":4, "KS":6, "KY":4,
     "LA": 7, "MD": 2, "ME": 0, "MA": 0, "MI": 4, "MN": 5, "MS": 3, "MO": 8,
     "MT": 5, "NE": 6, "NV": 8, "NH": 0, "NJ": 0,"NC": 2, "ND": 5, "NM": 8,
     "NY": 1, "OH": 4, "OK": 7, "OR": 9, "PA": 1, "RI": 0, "SC": 2, "SD": 5,
     "TN": 3, "TX": 7, "UT": 8, "VA": 2, "VT": 0, "WA": 9,"WI": 5,"WV":2, "WY":8
}


@app.route('/')
def index():
    reviews = Review.query.filter_by(item_rating=5).order_by(func.random()).limit(5).all()
    all_reviews = Review.query.all()
    return render_template('index.html', toprevs = reviews, allrevs = all_reviews, categories = Cats(), name = Name(), type = Type())

@app.route('/databaseview')
def databaseview():
    # Use the following code to delet anything you want. All you have to do is visit the /databaseview url and it will
    # delete the entry

    # user = User.query.filter_by(email='amrbedawi26@gmail.com').first()
    # db_session.delete(user)
    # db_session.commit()
    return render_template('databaseview.html', values=User.query.all())

@app.route('/forgotpassword', methods=['POST', 'GET'])
def forgotpassword():
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(email = request.form['email']).first()

        if user is None:
            error= 'Sorry, we cannot find an account with this email. Please try a different one!'
            return render_template('forgotpassword.html', error=error)

        msg = Message('Forgot password!', sender='miniamazongroup20@gmail.com', recipients=[user.email])
        msg.body = 'Hello '+user.name+',\nYou or someone else has requested the password for your account. \nYour password is '+user.password+'. \nIf you made this request, then login with the provided password. If you did not make this request, then you can ignore this email.'
        msg.html = render_template('retrieve_password_email.html', name=user.name, password=user.password)
        mail.send(msg)
        flash('We found your password! It may take a few minutes for the email to arrive. If you don\'t see it, check your spam folder')
        return render_template('forgotpassword.html')
    else:
        return render_template('forgotpassword.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        input_email = request.form['username']
        input_pw = request.form['password']
        user = User.query.filter_by(email = input_email).first()
        if user is None or user.password != input_pw:
            flash('Invalid Credentials. Please try again.')
            return render_template('login.html')
        else:
            session["USERID"] = user.id
            session["NAME"] = user.name
            session["TYPE"] = user.type
            return redirect(url_for('index'))

    # If you get here from a get request, render the page unless already logged in
    if session.get('USERID') is None:
        return render_template('login.html', categories = Cats())
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    if session.get('USERID') is not None:
        session.pop('NAME',None)
        session.pop('TYPE',None)
        session.pop('USERID',None)
        flash("You have been logged out", 'success')
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
        if req.get('userTypeSeller'):
            type_ = 'Seller'


        confirm_email = req['confirm_email']
        confirm_password = req['confirm_password']

        valid = True
        if '@' not in email:
            flash('Please enter a valid email')
            valid = False

        if email != confirm_email:
            flash('Emails do not match')
            valid = False

        exists = User.query.filter_by(email=email).first()
        if exists:
            flash('An account with this email already exists. Login with your existing email or use a different one.')
            valid = False

        if password != confirm_password:
            flash('Password do not match.')
            valid = False

        if len(str(zipcode)) != 5:
            flash('Please enter a valid zipcode.')
            valid = False

        if not valid:
            return render_template('signup.html')

        new_user = User(email, password, name, balance, type_, street, city, zipcode, state)
        db_session.add(new_user)
        db_session.commit()

        session["USERID"] = new_user.id
        session["NAME"] = new_user.name
        session["TYPE"] = new_user.type

        flash("New account successfully made", 'info')
        return redirect(url_for('index'))

    # If you get here from a get request, render the page unless already logged in
    if session.get('USERID') is None:
        return render_template('signup.html', categories = Cats())
    else:
        return redirect(url_for('index'))

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
    name = Name(), type = Type(), categories = Cats())

@app.route('/add_item')
def add_item():
  name = request.args.get("name")
  brand = request.args.get("brand")
  desc = request.args.get("desc")
  cat = request.args.get("cat")
  image_url = "img/no_image_available.jpg"

  item = Item(name, brand,desc,image_url)
  category = Category.query.filter_by(name=cat).first()
  assoc = InCat()
  assoc.cat = category
  item.categories.append(assoc)
  db_session.add(item)
  db_session.commit()

  return redirect(url_for('browse'))

@app.route('/denied')
def denied():
     return render_template('denied.html', categories = Cats())

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
    listings = Listing.query.filter_by(warehouse_id=me.warehouse.warehouse_id)

    filled = 0
    for l in listings:
        filled = filled + l.amount

    return render_template(
      'warehouse.html',
      past_orders = past_orders,
      new_orders = new_orders,
      me = me,
      filled = filled,
      warehouse = Warehouse.query.filter_by(id=me.warehouse.warehouse_id).first(),
      name = Name(), type = Type(), categories = Cats()
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

    return render_template('account.html', user = user, name = Name(), type = Type(), categories = Cats())

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

    sql_get_balance = text('''SELECT balance
                         FROM users
                         WHERE id = :id''')

    balance = engine.execute(sql_get_balance,id=me_id)

    return render_template('wallet.html', balance = balance, name = Name(), type = Type(), categories = Cats())

@app.route('/update_balance')
def update_balance():
    me_id = session.get("USERID")
    if me_id is None:
        return redirect(url_for('login'))

    to_add = request.args.get("added_balance")

    sql_update_balance = text('''UPDATE users
                            SET balance = balance + :add
                            WHERE id = :id''')

    engine.execute(sql_update_balance,add=to_add,id=me_id)

    return redirect(url_for('wallet'))

@app.route('/history')
def orderHistory():
    me_id = session.get("USERID")
    if me_id is None:
        return redirect(url_for('login'))

    sql_get_history = text('''SELECT I.name AS name, delivered, amount, price, date, I.id AS id, I.imgurl AS imgurl, U.name AS other_name
                         FROM orders O, items I, Users U
                         WHERE user_id = :id AND item_id = I.id AND seller_id = U.id''')

    history_items = engine.execute(sql_get_history,id=me_id)

    return render_template('order-history.html', other = "Seller",title = 'Previous Orders',items = history_items, name = Name(), type = Type(), categories = Cats())

@app.route('/trade-history')
def tradeHistory():
    me_id = session.get("USERID")
    if me_id is None:
        return redirect(url_for('login'))

    sql_get_sell_history = text('''SELECT I.name AS name, delivered, amount, price, date, I.id AS id, I.imgurl AS imgurl, U.name AS other_name
                         FROM orders O, items I, Users U
                         WHERE seller_id = :id AND item_id = I.id AND O.user_id = U.id''')
    history_items = engine.execute(sql_get_sell_history,id=me_id)

    return render_template('order-history.html', other = "Buyer", title = 'Previously Sold Items', items = history_items, name = Name(), type = Type(), categories = Cats())

@app.route('/cart')
def cart():
    me_id = session.get("USERID")
    if me_id is None:
        return redirect(url_for('login'))

    me = User.query.filter_by(id=me_id).first()

    sql_get_cart = '''SELECT I.imgurl AS img, I.name AS name, L.price AS price, C.amount AS amount, C.id AS id,
                             W.street AS street, W.city AS city, W.zip AS zip, W.state AS state, I.id AS item_id
                      FROM carts C, listings L, items I, warehouses W
                      WHERE C.user_id = :id AND C.listing_id = L.id AND L.warehouse_id = W.id
                      AND L.item_id = I.id'''

    cart_items = engine.execute(sql_get_cart,id=me_id)
    count_items = engine.execute(sql_get_cart,id=me_id)
    rows = [r[0] for r in count_items]
    num = len(rows)
    cart_copy = engine.execute(sql_get_cart,id=me_id)

    return render_template('cart.html', items = cart_items, items2 = cart_copy,
    num = num, name = Name(), type = Type(), categories = Cats(),me=me,regions=regions)

@app.route('/checkout', methods = ["GET", "POST"])
def checkout():
    me_id = session.get("USERID")
    if me_id is None:
        return redirect(url_for('login'))

    me = User.query.filter_by(id=me_id).first()
    if request.method == 'POST':
        checkout_list = me.carts

    money = 0
    for cart in checkout_list:
        money = money + cart.listing.price * cart.amount
        if cart.amount > cart.listing.amount:
            item_name = cart.listing.item.name[:40]
            flash("There aren't enough of "+ item_name + "!!!")
            return(redirect(url_for('cart')))

    if money > me.balance:
        flash("You don't have enough money!!!")
        return(redirect(url_for('cart')))


    for cart in checkout_list:
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

    return render_template("finished-order.html", name = Name(), type = Type(), categories = Cats())

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

    sql_items_cat = text('''SELECT *
                    FROM items I
                    WHERE I.name LIKE :term and EXISTS (SELECT * FROM categories C, inCategory A
                                  WHERE I.id=A.item_id and C.id=A.cat_id
                                  and C.name = :cat)''')
    sql_listings1 = text('''SELECT L.price, L.id
                    FROM items I, listings L
                    WHERE I.name LIKE :term and L.item_id = I.id and EXISTS (SELECT * FROM categories C, inCategory A
                                  WHERE I.id=A.item_id and C.id=A.cat_id
                                  and C.name = :cat)''')

    results = engine.execute(sql_items_cat,term='%'+query+'%',cat=category)
    listings = engine.execute(sql_listings1,term='%'+query+'%',cat=category)

    sql_items_all = text('''SELECT *
                        FROM items I
                        WHERE I.name LIKE :term ''')

    sql_listings2 = text('''SELECT L.price, L.id
                        FROM items I, listings L
                        WHERE I.name LIKE :term and L.item_id = I.id ''')
    results1 = engine.execute(sql_items_all,term='%'+query+'%')
    listings1 = engine.execute(sql_listings2,term='%'+query+'%')

    if category == 'ALL':
        results = results1
        listings = listings1

    return render_template(
        'results.html',
        results = results, name = Name(), type = Type(), categories = Cats()
        )

@app.route('/item/')
def items():
    ids = request.args.get("item_id")

    listings = Listing.query.filter_by(item_id=ids).all()
    reviews = Review.query.filter_by(item_id=ids).all()
    cost = 0; rating = 0; num = 0
    for l in listings:
        cost = cost + l.price
        num = num + 1
    if num != 0:
        cost = round(cost/num)
    num = 0
    for r in reviews:
        rating = rating + r.item_rating
        num = num + 1
    if num != 0:
        rating = round(rating/num)

    return render_template('item.html',
        items = Item.query.filter_by(id=ids).first(),
        cats = InCat.query.filter_by(item_id=ids).first(),
        sellers = listings, reviews = reviews,
        avg_p = cost, avg_r = rating,
        name = Name(), type = Type(), categories = Cats()
        )

@app.route('/seller')
def seller():
    me_id = session.get("USERID")
    if me_id is None:
        return redirect(url_for('login'))

    me = User.query.filter_by(id=me_id).first()

    if me.type != 'Seller':
        return redirect(url_for('denied'))

    results = None
    if request.args.get("searchtext"):
        query = request.args.get("searchtext")
        sql_items_all = text('''SELECT *
                         FROM items I
                         WHERE I.name LIKE :term ''')
        results = engine.execute(sql_items_all,term='%'+query+'%')

    return render_template('seller.html',
        seller = me,
        listings = Listing.query.filter_by(seller_id=me_id).all(),
        warehouses = Warehouse.query.all(),
        cats = Category.query.all(),
        items = Item.query.all(),
        results = results,
        name = Name(), type = Type(), categories = Cats()
        )

@app.route('/test')
def test():
    if Type() != "ADMIN":
        return redirect(url_for('denied'))

    return render_template(
        'test.html',
        users = User.query.order_by(func.random()).limit(30).all(),
        all_users = User.query.all(),
        sellers = User.query.filter_by(type="Seller"),
        warehouses = Warehouse.query.all(),
        locations = ManagerLocation.query.all(),
        cats = Category.query.all(),
        incats = InCat.query.order_by(func.random()).limit(30).all(),
        items = Item.query.order_by(func.random()).limit(30).all(),
        reviews = Review.query.order_by(func.random()).limit(30).all(),
        listings = Listing.query.order_by(func.random()).limit(30).all(),
        all_listings = Listing.query.all(),
        carts = Cart.query.order_by(func.random()).limit(30).all(),
        orders = Order.query.order_by(func.random()).limit(30).all(),
        name = Name(), type = Type(), categories = Cats()
    )

@app.route('/change_manager')
def change_manager():

    wid = request.args.get("whouse_id")
    email = request.args.get("email")

    whouse = Warehouse.query.filter_by(id=wid).first()
    newManager = User.query.filter_by(email=email).first()

    oldloc = ManagerLocation.query.filter_by(warehouse_id=wid).first()

    if oldloc is not None:
        oldloc.manager.type = 'User'
        db_session.delete(oldloc)

    newloc = ManagerLocation()
    newloc.warehouse = whouse
    newloc.manager = newManager
    whouse.manager.append(newloc)
    newManager.warehouse = newloc
    newManager.type = 'Manager'
    db_session.add(newloc)

    db_session.commit()

    return redirect(url_for('test'))

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
    me_id = session.get("USERID")
    if me_id is None:
        return redirect(url_for('login'))

    user_id = ID()
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

    return redirect(url_for('account'))

@app.route('/addlistingpage')
def addlistingpage():
    me_id = session.get("USERID")
    if me_id is None:
        return redirect(url_for('login'))

    me = User.query.filter_by(id=me_id).first()

    if me.type != 'Seller':
        return redirect(url_for('denied'))

    item_id = request.args.get("item_id")

    listing = None
    if request.args.get("listing_id"):
        listing = Listing.query.filter_by(id = request.args.get("listing_id")).first()
        item_id = listing.item_id

    return render_template(
        'addlistingpage.html',
        seller = me,
        item = Item.query.filter_by(id=item_id).first(),
        warehouses = Warehouse.query.all(),
        listing = listing,
        name = Name(), type = Type()
        )

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

    other_listings = Listing.query.filter_by(warehouse_id=wh_id).all()
    current_full = 0
    for ol in other_listings:
        current_full = current_full + ol.amount

    if current_full + int(amount) > listing.warehouse.capacity:
        flash("That warehouse cannot take that many items")
        return(redirect(url_for('seller')))


    db_session.add(listing)
    db_session.commit()

    return redirect(url_for('seller'))

@app.route('/edit_listing')
def edit_listing():
    me_id = session.get("USERID")
    if me_id is None:
        return redirect(url_for('login'))

    me = User.query.filter_by(id=me_id).first()

    if me.type != 'Seller':
        return redirect(url_for('denied'))

    seller_id = me_id
    listing_id = request.args.get("listing_id")
    new_wh_id = request.args.get("updated_warehouse_id")
    new_price = request.args.get("updated_price")
    new_amount = request.args.get("updated_amount")

    listing = Listing.query.filter_by(id=listing_id).first()

    listing.warehouse_id = new_wh_id
    listing.price = new_price
    listing.amount = new_amount

    db_session.commit()

    return redirect(url_for('seller'))

@app.route('/delete_listing')
def delete_listing():
    listing_id = request.args.get("listing_id")
    listing = Listing.query.filter_by(id=listing_id).first()
    db_session.delete(listing)
    db_session.commit()

    return redirect(url_for('seller'))

@app.route('/add_cart')
def add_cart():
    user_id = ID()
    listing_id = request.args.get("listing_id")
    amount = request.args.get("amount")

    cart = Cart(amount)
    cart.listing = Listing.query.filter_by(id=listing_id).first()
    cart.user = User.query.filter_by(id=user_id).first()

    db_session.add(cart)
    db_session.commit()

    return redirect(url_for('cart'))

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
