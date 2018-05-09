from flask import render_template
from sqlalchemy import func

from . import home
from ..models import Book, User


@home.route('/')
def homepage():
    users = User.query.all()
    books = Book.query.all()
    borrowed_books = Book.query.filter(Book.is_borrowed == 1).all()
    return render_template('home/index.html', title="Welcome", users=len(users), books=len(books),
                           borrowed_books=len(borrowed_books))
