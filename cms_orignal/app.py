from flask import Flask, request, redirect, url_for, render_template, session
import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = "cafesecret"
load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



# Menu items
menu = {
    "Espresso": 80, "Americano": 100, "Cappuccino": 120, "Latte": 130, "Mocha": 140,
    "Masala Chai": 60, "Green Tea": 70, "Hot Chocolate": 110, "Filter Coffee": 90, "Turmeric Latte": 100,
    "Iced Coffee": 110, "Cold Brew": 130, "Lemon Iced Tea": 90, "Mango Smoothie": 150, "Strawberry Shake": 140,
    "Cold Cocoa": 120, "Vanilla Frappe": 130, "Watermelon Juice": 100, "Mint Mojito": 120, "Buttermilk": 60,
    "Veg Sandwich": 100, "Grilled Chicken Sandwich": 150, "Paneer Tikka Sandwich": 140, "Club Sandwich": 160,
    "Chicken Wrap": 150, "Paneer Wrap": 130, "Falafel Wrap": 140, "Egg Mayo Sandwich": 130, "Tofu Lettuce Wrap": 145,
    "BLT Sandwich": 155, "French Fries": 90, "Cheese Garlic Bread": 120, "Chicken Nuggets": 140, "Veg Cutlet": 100,
    "Samosa": 40, "Pav Bhaji": 130, "Onion Rings": 100, "Tandoori Paneer Tikka": 160, "Chicken Wings": 170,
    "Spring Rolls": 140, "Pasta Alfredo": 180, "Pasta Arrabbiata": 170, "Chicken Biryani": 200,
    "Paneer Butter Masala with Naan": 190, "Veg Fried Rice": 150, "Hakka Noodles": 160, "Chicken Curry with Rice": 210,
    "Rajma Chawal": 130, "Chole Bhature": 140, "Mushroom Stroganoff": 180, "Chocolate Brownie": 110, "Cheesecake Slice": 140,
    "Ice Cream (2 Scoops)": 90, "Gulab Jamun": 70, "Donut": 80
}
menu_items = list(menu.items())

# Predefined users
users = {
    "admin": {"password": "admin123", "role": "admin"},
    "waiter": {"password": "waiter123", "role": "waiter"}
}


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_username = db.Column(db.String(100), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        # Check predefined users (admin, waiter)
        if u in users and users[u]['password'] == p:
            session['user'] = u
            session['role'] = users[u]['role']
            session['order'] = []
            return redirect(url_for('home'))

        # Check database customers
        customer = Customer.query.filter_by(username=u).first()
        if customer and customer.password == p:
            session['user'] = u
            session['role'] = "customer"
            session['order'] = []
            return redirect(url_for('home'))

        error = "Invalid username or password"

    return render_template('login.html', error=error)

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', user=session['user'], role=session['role'])

@app.route('/order', methods=['GET', 'POST'])
def order():
    if 'user' not in session:
        return redirect(url_for('login'))

    if 'order' not in session:
        session['order'] = []
    order_list = session['order']

    if request.method == 'POST':
        if 'add_item' in request.form:
            idx = int(request.form['item'])
            qty = int(request.form['qty'])
            name, price = menu_items[idx]
            for i, (it, q, pr) in enumerate(order_list):
                if it == name:
                    new_qty = q + qty
                    order_list[i] = (it, new_qty, price * new_qty)
                    break
            else:
                order_list.append((name, qty, price * qty))
            session['order'] = order_list

        elif 'generate_bill' in request.form:
            total = sum(p for _, _, p in order_list)
            user = session['user']

    # Save sale in database
            new_sale = Sale(
            customer_username=user,
            total_amount=total
        )

            db.session.add(new_sale)
            db.session.commit()

            temp = list(order_list)
            session['order'] = []

            return render_template('bill.html', bill=temp, total=total)

    total = sum(p for _, _, p in order_list)
    return render_template('order.html', menu_items=menu_items, bill=order_list, total=total, enumerate=enumerate)
@app.route('/create-customer', methods=['GET', 'POST'])
def create_customer():
    if request.method == 'POST':
        uname = request.form['username']
        pword = request.form['password']

        # Check if user already exists in database
        existing_user = Customer.query.filter_by(username=uname).first()

        if existing_user:
            return "Username already exists."

        # Create new customer
        new_customer = Customer(username=uname, password=pword)
        db.session.add(new_customer)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('create_customer.html')
@app.route('/view-sales')
def view_sales():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))

    all_sales = Sale.query.all()
    sales_data = {}

    for sale in all_sales:
        if sale.customer_username not in sales_data:
            sales_data[sale.customer_username] = []
        sales_data[sale.customer_username].append(sale.total_amount)

    return render_template('view_sales.html', sales=sales_data)

import json

def read_sales():
    try:
        with open('data/sales.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

@app.route('/clear-sales')
def clear_sales():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))

    Sale.query.delete()
    db.session.commit()

    return redirect(url_for('home'))

@app.route('/view_customer_bill', methods=['GET', 'POST'])
def view_customer_bill():
    customer_name = None
    customer_sales = []

    if request.method == 'POST':
        name_in = request.form.get('customer_name', '').strip()

        # Get all sales for this customer from DB
        customer_sales = Sale.query.filter_by(customer_username=name_in).all()
        customer_name = name_in

    return render_template(
        'view_customer_bill.html',
        customer_name=customer_name,
        customer_sales=customer_sales
    )


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)