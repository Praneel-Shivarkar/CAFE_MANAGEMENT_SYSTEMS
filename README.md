# ☕ Cafe Management System

A full-stack Cafe Management System built using Flask and PostgreSQL.  
This application allows admins and staff to manage customers, place orders, generate bills, and track sales with persistent database storage.

---

## 🚀 Features

- User authentication (Admin & Customer roles)
- Create new customers
- Place orders with multiple menu items
- Generate a detailed bill per session
- Store sales records in PostgreSQL
- View customer-wise sales history
- Admin dashboard for sales tracking
- Session-based order management

---

## 🛠 Tech Stack

- **Backend:** Flask (Python)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Frontend:** HTML, Bootstrap 5
- **Environment Management:** python-dotenv
- **Version Control:** Git & GitHub

---

## 🗄 Database Models

### Customer
- id (Primary Key)
- username (Unique)
- password

### Sale
- id (Primary Key)
- customer_username
- total_amount

---

## ⚙️ Setup Instructions

1. Clone the repository:

2. Create a virtual environment:

3. Install dependencies:

4. Create a `.env` file:

5. Create database tables:
  from app import db, app
  app.app_context().push()
  db.create_all()
  exit()

6. Run the application:

---

## 📌 Project Highlights

- Migrated from JSON-based storage to PostgreSQL
- Implemented relational database design
- Used SQLAlchemy ORM for clean database queries
- Secured database credentials using environment variables
- Built a session-based billing system

---

## 💼 Author

Praneel Shivarkar  
Computer Engineering Student  
