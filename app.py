# Python standard library imports
from datetime import date, timedelta
import csv
import datetime

# Third-party imports
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from sqlalchemy import join
from apscheduler.schedulers.background import BackgroundScheduler

# Local application imports
from create_db import db, Customer, Book, Loan

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.sqlite3'
app.config['SECRET_KEY'] = "random string"
CORS(app)

db.init_app(app)

# Function to check customer activity and update 'active' field
def check_customer_activity():
    loans = Loan.query.all()
    for loan in loans:
        customer = Customer.query.get(loan.customer_id)
        if datetime.datetime.now().date() - loan.loan_date.date() > timedelta(days=30):
            customer.active = False
        else:
            customer.active = True
        db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_customer_activity, trigger="interval", days=1)
scheduler.start()


# ------------------------------------------------------------------
# BOOK ROUTES
# ------------------------------------------------------------------

# GET - List all books
@app.route('/books', methods=['GET'])
def books_list():
    books = Book.query.all()
    books_list = [
        {
            'id': book.id,
            'name': book.name,
            'author': book.author,
            'year_published': book.year_published,
            'book_type': book.book_type,
            'picture': book.picture,
        }
        for book in books
    ]
    return jsonify(books_list)

# GET - selected book
@app.route('/book/<int:book_id>', methods=['GET'])
def update_book(book_id):
    if request.method == 'GET':
     book = Book.query.get(book_id)
     
     books_data = [{
            'id': book.id,
            'name': book.name,
            'author': book.author,
            'year_published': book.year_published,
            'book_type': book.book_type,
            'picture': book.picture,
            'availability': book.availability
     } ]
    
    return jsonify(books_data) 

# POST - Add new book
@app.route('/booksnew', methods=['POST', 'GET'])
def create_book():
    data = request.json  # Get the book data from the request body

    name = data.get('name')
    author = data.get('author')
    year_published = data.get('year_published')
    picture = data.get('picture')
    book_type = data.get('book_type')

    if not all([name, author, year_published, picture, book_type]):
        response = {'message': 'Missing book information'}
        return jsonify(response), 400

    book = Book(name=name, author=author, year_published=year_published, picture=picture, book_type=book_type, availability=True)
    db.session.add(book)
    db.session.commit()

    return redirect(url_for('books_list'))

#EDIT Book
@app.route('/edit_book/<int:book_id>', methods=['PUT' ])
def edit_book(book_id):
   

    data = request.json
    book = Book.query.get(book_id)
    if book is None:
        return jsonify({'error': 'Book not found'}), 404

    # Update book attributes with the new data
    book.name = data.get('name', book.name)
    book.author = data.get('author', book.author)
    book.year_published = data.get('year_published', book.year_published)
    book.picture = data.get('picture', book.picture)
    book.book_type = data.get('book_type', book.book_type)

    db.session.commit()

    # Return updated book data
    return jsonify({
        'id': book.id,
        'name': book.name,
        'author': book.author,
        'year_published': book.year_published,
        'picture': book.picture,
        'book_type': book.book_type
    }), 200



# DELETE - Delete specific book
@app.route('/delete_book/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get(book_id)
   

    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'})



# ------------------------------------------------------------------
# CUSTOMER ROUTES
# ------------------------------------------------------------------

# GET - List all customers
@app.route('/customers', methods=['GET'])
def customers_list():
    customers = Customer.query.all()
    customers_list = [
        {
            'id': customer.id,
            'name': customer.name,
            'city': customer.city,
            'age': customer.age,
            'active': customer.active
        }
        for customer in customers
    ]
    return jsonify(customers_list)

# POST - Add new customer
@app.route('/customersnew', methods=['POST','GET'])
def add_customer():
    data = request.json 

    name = data.get('name')
    city = data.get('city')
    age = int(data.get('age'))

    # Create a new Customer object and add it to the database
    customer = Customer(name=name, city=city, age=age, active=False)
    db.session.add(customer)
    db.session.commit()

    return redirect(url_for('books_list'))

# PUT - Update specific customer
@app.route('/edit_customers/<int:customer_id>', methods=['PUT', 'GET'])
def update_customer(customer_id):
    customer = Customer.query.get(customer_id)
    
    data = request.json
    name = data.get('name')
    city = data.get('city')
    age = data.get('age')


    if not all([name, city, age]):
        return jsonify({'error': 'Missing customer information'}), 400

    # Update customer details
    customer.name = name
    customer.city = city
    customer.age = age

    db.session.commit()
    return "customer updated"

# DELETE - Delete specific customer
@app.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = Customer.query.get(customer_id)
    db.session.delete(customer)
    db.session.commit()

    return ("customer deleted")  

# LOANS

# ------------------------------------------------------------------
# LOAN ROUTES
# ------------------------------------------------------------------

# GET - List all loans
@app.route('/actions', methods=['GET'])
def get_loans():
    query = db.session.query(Loan, Customer.name, Book.name).join(Customer).join(Book)
    results = query.all()

    loan_data = []
    for loan, customer_name, book_name in results:
        loan_info = {
            'id': loan.id,
            'customer_name': customer_name,
            'book_name': book_name,
            'loan_date': loan.loan_date.strftime('%Y-%m-%d'),
            'return_date': loan.return_date.strftime('%Y-%m-%d')
        }
        loan_data.append(loan_info)
    return jsonify(loan_data)

# POST - Add new loan
@app.route('/create_loan/<int:book_id>', methods= ['POST'])
def create_loan(book_id):
    data = request.json    
    customer_name = data.get('customer_name')
    customer_city = data.get('city')  # Get city from the request body
    customer_age = data.get('age')  # Get age from the request body
    book = Book.query.filter_by(id=book_id).first()
    customer = Customer.query.filter_by(name=customer_name).first()
    customer.city = customer_city
    customer.age = customer_age
    
    
    if book.availability:
        book.availability = False
        db.session.commit()
    
    if book.book_type == '1':
        return_date = date.today() + timedelta(days=-5)
    elif book.book_type == '2':
        return_date = date.today() + timedelta(days=5)
    elif book.book_type == '3':
        return_date = date.today() + timedelta(days=10)

    new_loan = Loan(
        customer_id=customer.id,
        book_id=book_id,
        loan_date=date.today(),
        return_date=return_date,
        returned=False
    )
   
    db.session.add(new_loan)
    customer.active = True
    db.session.commit()
    
    return "Loan created successfully", 201

# PUT - Update specific loan (return book)
@app.route('/return_book/<int:book_id>', methods=['PUT'])
def return_book(book_id):
    # Query for the loan related to the given book_id which is not returned yet
    loan = Loan.query.filter_by(book_id=book_id, returned=False).first()

    # Check if the loan exists
    if loan is None:
        return jsonify({'error': 'Loan not found'})

    # Set the return_date to today and mark the loan as returned
    loan.return_date = datetime.date.today()
    loan.returned = True

    # Set the associated book as available
    loan.book.availability = True

    db.session.commit()
    return jsonify({'message': 'Book returned successfully'})

# GET - List all late returns
@app.route('/late_returns', methods=['GET'])
def get_late_returns():
    today = date.today()

    # Get all loans where the return date is earlier than today and the book has not been returned
    late_loans = Loan.query.filter(Loan.return_date < today, Loan.returned == False).all()

    late_returns = []
    for loan in late_loans:
        # Get customer and book details for each late loan
        customer = Customer.query.get(loan.customer_id)
        book = Book.query.get(loan.book_id)

        late_return = {
            'loan_id': loan.id,
            'customer_name': customer.name,
            'book_name': book.name,
            'loan_date': loan.loan_date.strftime('%Y-%m-%d'),
            'return_date': loan.return_date.strftime('%Y-%m-%d')
        }
        late_returns.append(late_return)
    
    return jsonify(late_returns)


# ------------------------------------------------------------------
# MAIN EXECUTION
# ------------------------------------------------------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
