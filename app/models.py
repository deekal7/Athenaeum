from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(60), index=True, nullable=False)
    last_name = db.Column(db.String(60), index=True, nullable=False)
    username = db.Column(db.String(60), index=True, unique=True, nullable=False)
    email = db.Column(db.String(60), index=True, unique=True, nullable=False)
    phone = db.Column(db.String(60), index=True, unique=True)
    city = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(128))
    owns_books = db.relationship('Book', cascade="all, delete-orphan", lazy='dynamic', backref='owner',  foreign_keys='Book.owner_id')
    borrowed_books = db.relationship('Book', backref='borrower', lazy='dynamic', foreign_keys='Book.borrower_id')

    @property
    def password(self):
        raise AttributeError('password is not readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User: {}'.format(self.username)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


bookauthors = db.Table('bookauthors',
    db.Column('book_id', db.Integer, db.ForeignKey('books.id')),
    db.Column('author_id', db.Integer, db.ForeignKey('authors.id'))
)


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(17), index=True, unique=True)
    title = db.Column(db.String(60), index=True, nullable=False)
    genre = db.Column(db.String(60), index=True, nullable=False)
    is_borrowed = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    borrower_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'))
    authors = db.relationship('Author', secondary='bookauthors')

    def __repr__(self):
        return '<Book: {}'.format(self.title)


class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), index=True, nullable=False)
    books = db.relationship('Book', secondary='bookauthors')

    def __repr__(self):
        return '<Author: {}'.format(self.name)


class Publisher(db.Model):
    __tablename__ = 'publishers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), index=True, unique=True, nullable=False)
    books = db.relationship('Book', backref="publisher", cascade="all, delete-orphan", lazy='dynamic')

    def __repr__(self):
        return '<Publisher: {}'.format(self.name)
