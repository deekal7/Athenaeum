from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField

from ..models import Author, Publisher


class AuthorForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')


class PublisherForm(FlaskForm):
    name = StringField('Publisher Name', validators=[DataRequired()])
    submit = SubmitField('Submit')


class BookForm(FlaskForm):
    isbn = StringField('ISBN', validators=[DataRequired()])
    title = StringField('Book Title', validators=[DataRequired()])
    genre = StringField('Genre', validators=[DataRequired()])
    authors = QuerySelectMultipleField(query_factory=lambda: Author.query.all(), get_label="name",
                                       validators=[DataRequired()])
    publisher = QuerySelectField(query_factory=lambda: Publisher.query.all(), get_label="name",
                                 validators=[DataRequired()])
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    choices = [('Title', 'Title'),
               ('Author', 'Author'),
               ('Genre', 'Genre'),
               ('City', 'Lender City'),
               ('Publisher', 'Publisher')]
    category = SelectField('', choices=choices)
    query = StringField('', validators=[Length(min=0, max=100)])
    submit = SubmitField('Submit')


class BorrowForm(FlaskForm):
    submit = SubmitField('Borrow')

