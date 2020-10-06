from flask import Flask, request, redirect, url_for, render_template
from models import *
from database import db_session, engine

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
  cat = request.args.get("cat")

  item = Item(name, brand, color, size)
  category = Category.query.filter_by(name=cat).first()
  assoc = InCat()
  assoc.cat = category
  item.categories.append(assoc)
  db_session.add(item)
  db_session.commit()

  return redirect(url_for('browse'))


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
    return render_template('cart.html')

if __name__ == "__main__":
    app.run()
