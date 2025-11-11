from flask import Flask, request, redirect, url_for, render_template, session
import json
import os

app = Flask(__name__)
app.secret_key = "cafesecret"

# File paths
sales_file = 'sales_data.json'
customers_file = 'customers_data.json'

# Load persistent data
if os.path.exists(sales_file):
    with open(sales_file, 'r') as f:
        sales = json.load(f)
else:
    sales = {}

if os.path.exists(customers_file):
    with open(customers_file, 'r') as f:
        customers = json.load(f)
else:
    customers = {}

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
users.update({u: {"password": p, "role": "customer"} for u, p in customers.items()})

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        if u in users and users[u]['password'] == p:
            session['user'] = u
            session['role'] = users[u]['role']
            session['order'] = []
            return redirect(url_for('home'))
        else:
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
            if user not in sales:
                sales[user] = []
            sales[user].append(total)
            with open(sales_file, 'w') as f:
                json.dump(sales, f)
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
        if uname in customers:
            return "Username already exists."
        customers[uname] = pword
        with open(customers_file, 'w') as f:
            json.dump(customers, f)
        users[uname] = {"password": pword, "role": "customer"}
        return redirect(url_for('home'))
    return render_template('create_customer.html')


@app.route('/view-sales')
def view_sales():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
    return render_template('view_sales.html', sales=sales)

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
    sales.clear()
    with open(sales_file, 'w') as f:
        json.dump(sales, f)
    return redirect(url_for('home'))

@app.route('/view_customer_bill', methods=['GET', 'POST'])
def view_customer_bill():
    # 'sales' is the global dict you loaded at startup
    customer_name = None

    if request.method == 'POST':
        # grab the raw input and strip whitespace
        name_in = request.form.get('customer_name', '').strip()
        # do a case‐insensitive match against your sales keys
        for real_name in sales:
            if real_name.lower() == name_in.lower():
                customer_name = real_name
                break

    # render the same template, passing sales + possibly matched name
    return render_template('view_customer_bill.html',
                           sales=sales,
                           customer_name=customer_name)



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
