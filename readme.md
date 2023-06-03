# Library Management System

## About the Project
This project is a library management system developed using Flask, SQLAlchemy, and APScheduler. It includes models for Customers, Books, and Loans, as well as routes for handling various operations related to these models. The system also automatically checks customer activity and updates the 'active' field of a customer daily.

The project includes two main Python files:
- `app.py`
- `create_db.py`



## Setup and Installation

1. Clone the repository.
2. Install the dependencies by running `pip install -r requirements.txt` in your virtual environment.
3. Create the database by using the command `python create_db.py`.
4. Run the app by using command `python app.py`.

## Usage

Use the following routes for API interaction:

- `GET /books`: List all books.
- `GET /book/<int:book_id>`: Get details about a specific book.
- `POST /booksnew`: Add a new book.
- `PUT /edit_book/<int:book_id>`: Edit a book's details.
- `DELETE /delete_book/<int:book_id>`: Delete a specific book.
- `GET /customers`: List all customers.
- `POST /customersnew`: Add a new customer.
- `PUT /edit_customers/<int:customer_id>`: Edit a customer's details.
- `DELETE /customers/<int:customer_id>`: Delete a specific customer.
- `GET /actions`: List all loans.
- `POST /create_loan/<int:book_id>`: Create a new loan.
- `PUT /return_book/<int:book_id>`: Return a book.
- `GET /late_returns`: List all late returns.
