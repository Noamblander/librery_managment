# ---------------- Import statements and app configuration ----------------

import csv
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.sqlite3'
app.config['SECRET_KEY'] = "random string"
CORS(app)

db = SQLAlchemy(app)



# ---------------- Models ----------------

class Customer(db.Model):
    id = db.Column('customer_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(50))
    age = db.Column(db.Integer)
    active = db.Column(db.Boolean, default=False)

    def __init__(self, name, city, age, active):
        self.name = name
        self.city = city
        self.age = age
        self.active = active 
      
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'age': self.age,
            'active': self.active
        }

class Book(db.Model):
    id = db.Column('book_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    author = db.Column(db.String(50))
    year_published = db.Column(db.String(200))
    book_type = db.Column(db.String(10))
    picture = db.Column(db.String(200))
    availability = db.Column(db.Boolean, default=True)

    def __init__(self, name, author, year_published, book_type, picture, availability):
        self.name = name
        self.author = author
        self.year_published = year_published
        self.book_type = book_type
        self.picture = picture
        self.availability = availability
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'author': self.author,
            'year_published': self.year_published,
            'book_type': self.book_type,
            'picture': self.picture,
            'availability': self.availability
        }

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable=False)
    loan_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)
    returned = db.Column(db.Boolean, default=False)
    
    book = db.relationship("Book", backref="loans", foreign_keys=[book_id])
    customer = db.relationship("Customer", backref="loans", foreign_keys=[customer_id])

    def __init__(self, customer_id, book_id, loan_date, return_date,returned):
        self.customer_id = customer_id
        self.book_id = book_id
        self.loan_date = loan_date
        self.return_date = return_date
        self.returned = returned
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'book_id': self.book_id,
            'loan_date': str(self.loan_date),
            'return_date': str(self.return_date),
            'returned': self.returned
        }


# ---------------- Functions to populate data from CSV files ----------------

# Function to extract columns from a CSV file using pandas
def extract_columns(csv_file, columns, encoding='utf-8'):
    df = pd.read_csv(csv_file, encoding=encoding)
    extracted_data = df[columns].to_dict('records')
    return extracted_data

def populate_customers_from_csv():
    csv_file = 'customers.csv'
    columns = ['name', 'city', 'age']
    extracted_data = extract_columns(csv_file, columns)

    with app.app_context():
        # Check if data already exists in the table
        if Customer.query.first() is None:
            for row in extracted_data:
                customer = Customer(
                    name=row['name'],
                    city=row['city'],
                    age=row['age'],
                    active=False
                )
                db.session.add(customer)
            db.session.commit()


# Function to populate the Book table with data from CSV file
def populate_books_from_csv():
    csv_file = 'books.csv'
    columns = ['title', 'authors', 'published_year', 'categories', 'thumbnail']
    extracted_data = extract_columns(csv_file, columns)

    with app.app_context():
        # Check if data already exists in the table
        if Book.query.first() is None:
            for row in extracted_data:
                book = Book(
                    name=row['title'],
                    author=row['authors'],
                    year_published=row['published_year'],
                    book_type=row['categories'],
                    picture=row['thumbnail'],
                    availability=True  
                )
                db.session.add(book)
            db.session.commit()


# ------------------------------------------------------------------
# MAIN EXECUTION
# ------------------------------------------------------------------
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # Only populate data from CSVs if tables are empty
        if not Customer.query.first():
            populate_customers_from_csv()
        if not Book.query.first():
            populate_books_from_csv()

        app.run(debug=True)




    