from flask import Flask, render_template
from models import Item
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
    items = Item.query.all()
  )

@app.route('/account')
def account():
    return render_template('account.html',items = Item.query.all())

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
