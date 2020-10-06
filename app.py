from flask import Flask, request, redirect, url_for, render_template
from models import *
from database import db_session

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/database')
def database():
  return render_template(
    'database.html',
    items = Item.query.all(),
    cats = InCat.query.all()
  )

@app.route('/add_item')
def add_item():
  name = request.args.get("name")
  brand = request.args.get("brand")
  color = request.args.get("color")
  size = request.args.get("size")

  item = Item(name, brand, color, size)
  db_session.add(item)
  db_session.commit()

  return redirect(url_for('database'))


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
