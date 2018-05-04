from flask import flash, redirect, render_template, url_for, session
from flask_login import login_required, current_user


from . import user
from .forms import AuthorForm, PublisherForm, BookForm, SearchForm, BorrowForm
from .. import db
from ..models import User, Author, Publisher, Book


@user.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = SearchForm()
    if form.validate_on_submit():
        choice = form.category.data
        query = form.query.data
        query = query.title()
        print(choice)
        print(query)
        books = []
        if choice == 'Title':
            books.extend(Book.query.filter(Book.title.contains(query), Book.owner_id != current_user.id,
                                           Book.is_borrowed == 0).all())
        elif choice == 'Author':
            authors = Author.query.filter(Author.name.contains(query)).all()
            for author in authors:
                for book in author.books:
                    if book.owner_id != current_user.id and book.is_borrowed == 0:
                        books.append(book)
        elif choice == 'Genre':
            books.extend(Book.query.filter(Book.genre.contains(query), Book.owner_id != current_user.id,
                                           Book.is_borrowed == 0).all())
        elif choice == 'City':
            owners = User.query.filter(User.city.contains(query)).all()
            for owner in owners:
                for book in owner.owns_books:
                    if book.owner_id != current_user.id and book.is_borrowed == 0:
                        books.append(book)
        elif choice == 'Publisher':
            publishers = Publisher.query.filter(Publisher.name.contains(query)).all()
            for publisher in publishers:
                for book in publisher.books:
                    if book.owner_id != current_user.id and book.is_borrowed == 0:
                        books.append(book)
        if books:
            return render_template('user/dashboard.html', books=books, show_results=True, form=form, title='Results')
        else:
            flash('No books matching your search were found.')
            return redirect(url_for('user.dashboard'))
    return render_template('user/dashboard.html', books=None, show_results=False, form=form, title='Dashboard')


@user.route('/borrow/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def borrow_book(id):
    book = Book.query.get_or_404(id)
    owner = User.query.get_or_404(book.owner_id)
    publisher = Publisher.query.get_or_404(book.publisher_id)
    form = BorrowForm()
    if form.validate_on_submit():
        book.borrower_id = current_user.id
        book.is_borrowed = 1
        current_user.borrowed_books.append(book)
        db.session.commit()
        flash('You have successfully borrowed {}.'.format(book.title))
        return redirect(url_for('user.dashboard'))
    return render_template('user/search/book_details.html', book=book, owner=owner,
                           publisher=publisher, form=form, title=book.title)


@user.route('/profile/borrowed', methods=['GET', 'POST'])
@login_required
def list_borrowed():
    form = SearchForm()
    if form.validate_on_submit():
        choice = form.category.data
        query = form.query.data
        query = query.title()
        books = []
        if choice == 'Title':
            books.extend(Book.query.filter(Book.title.contains(query), Book.borrower_id == current_user.id).all())
        elif choice == 'Author':
            authors = Author.query.filter(Author.name.contains(query)).all()
            for author in authors:
                for book in author.books:
                    if book.borrower_id == current_user.id:
                        books.append(book)
        elif choice == 'Genre':
            books.extend(Book.query.filter(Book.genre.contains(query), Book.borrower_id == current_user.id).all())
        elif choice == 'City':
            owners = User.query.filter(User.city.contains(query)).all()
            for owner in owners:
                for book in owner.owns_books:
                    if book.borrower_id == current_user.id:
                        books.append(book)
        elif choice == 'Publisher':
            publishers = Publisher.query.filter(Publisher.name.contains(query)).all()
            for publisher in publishers:
                for book in publisher.books:
                    if book.borrower_id == current_user.id:
                        books.append(book)
        if books:
            return render_template('user/search/borrowed_books.html', books=books, show_results=True,
                                   form=form, title='Borrowed')
        else:
            flash('No books matching your search were found.')
            return redirect(url_for('user.list_borrowed'))
    return render_template('user/search/borrowed_books.html', books=None, show_results=False, form=form, title='Borrowed Books')



@user.route('/profile/borrowed/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def return_book(id):
    book = Book.query.get_or_404(id)
    current_user.borrowed_books.remove(book)
    book.is_borrowed = 0
    db.session.commit()
    flash('You have successfully returned {}.'.format(book.title))
    return redirect(url_for('user.list_borrowed'))


@user.route('/authors', methods=['GET', 'POST'])
@login_required
def list_authors():
    authors = Author.query.all()
    return render_template('user/authors/authors.html', authors=authors, title='Authors')


@user.route('/authors/add', methods=['GET', 'POST'])
@login_required
def add_author():
    add_author = True
    form = AuthorForm()
    if form.validate_on_submit():
        author = Author(name=form.name.data)
        try:
            db.session.add(author)
            db.session.commit()
            flash('You have successfully added a new author.')
        except:
            flash('Error: Author already exists.')
        return redirect(url_for('user.list_authors'))
    return render_template('user/authors/author.html', action='Add',
                           add_author=add_author, form=form,
                           title="Add Author")


@user.route('/authors/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_author(id):
    add_author = False
    author = Author.query.get_or_404(id)
    form = AuthorForm(obj=author)
    if form.validate_on_submit():
        author.name = form.name.data
        db.session.commit()
        flash('You have successfully edited the author.')
        return redirect(url_for('user.list_authors'))
    form.name.data = author.name
    return render_template('user/authors/author.html', action='Edit',
                           add_author=add_author, form=form,
                           author=author, title='Edit Author')


@user.route('/authors/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_author(id):
    author = Author.query.get_or_404(id)
    if len(author.books) > 0:
        flash('Author cannot be deleted.')
        return redirect(url_for('user.list_authors'))
    db.session.delete(author)
    db.session.commit()
    flash('You have successfully deleted the author.')
    return redirect(url_for('user.list_authors'))


@user.route('/publishers', methods=['GET', 'POST'])
@login_required
def list_publishers():
    publishers = Publisher.query.all()
    return render_template('user/publishers/publishers.html', publishers=publishers, title='Publishers')


@user.route('/publishers/add', methods=['GET', 'POST'])
@login_required
def add_publisher():
    add_publisher = True
    form = PublisherForm()
    if form.validate_on_submit():
        publisher = Publisher(name=form.name.data)
        try:
            db.session.add(publisher)
            db.session.commit()
            flash('You have successfully added a new publisher.')
        except:
            flash('Error: Publisher already exists.')
        return redirect(url_for('user.list_publishers'))
    return render_template('user/publishers/publisher.html', action='Add',
                           add_publisher=add_publisher, form=form,
                           title="Add Publisher")


@user.route('/publishers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_publisher(id):
    add_publisher = False
    publisher = Publisher.query.get_or_404(id)
    form = PublisherForm(obj=publisher)
    if form.validate_on_submit():
        publisher.name = form.name.data
        db.session.commit()
        flash('You have successfully edited the publisher.')
        return redirect(url_for('user.list_publishers'))
    form.name.data = publisher.name
    return render_template('user/publishers/publisher.html', action='Edit',
                           add_publisher=add_publisher, form=form,
                           publisher=publisher, title='Edit Publisher')


@user.route('/publishers/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_publisher(id):
    publisher = Publisher.query.get_or_404(id)
    if publisher.books.count() > 0:
        flash('Publisher cannot be deleted.')
        return redirect(url_for('user.list_publishers'))
    db.session.delete(publisher)
    db.session.commit()
    flash('You have successfully deleted the publisher.')
    return redirect(url_for('user.list_publishers'))


@user.route('/books', methods=['GET', 'POST'])
@login_required
def list_books():
    books = Book.query.filter_by(owner_id=current_user.id).all()
    return render_template('user/books/books.html', books=books, title='Books')


@user.route('/books/add', methods=['GET', 'POST'])
@login_required
def add_book():
    add_book = True
    form = BookForm()
    if form.validate_on_submit():
        book = Book(isbn=form.isbn.data,
                    title=form.title.data,
                    genre=form.genre.data,
                    owner_id=current_user.id
                    )
        publisher = form.publisher.data
        authors = form.authors.data
        book.publisher_id = publisher.id
        for author in authors:
            book.authors.append(author)
        publisher.books.append(book)
        current_user.owns_books.append(book)
        try:
            db.session.add(book)
            db.session.commit()
            flash('You have successfully added a new book.')
        except:
            flash('Error: Book already exists.')
        return redirect(url_for('user.list_books'))
    return render_template('user/books/book.html', action='Add',
                           add_book=add_book, form=form,
                           title="Add Book")


@user.route('/books/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_book(id):
    add_book = False
    book = Book.query.get_or_404(id)
    form = BookForm(obj=book)
    # publisher = Publisher.query.get_or_404(book.publisher_id)
    if form.validate_on_submit():
        book.authors.clear()
        book.isbn = form.isbn.data
        book.title = form.title.data
        book.genre = form.genre.data
        book.owner_id = current_user.id
        publisher = form.publisher.data
        authors = form.authors.data
        book.publisher_id = publisher.id
        for author in authors:
            book.authors.append(author)
        db.session.commit()
        flash('You have successfully edited the book.')
        return redirect(url_for('user.list_books'))
    return render_template('user/books/book.html', action='Edit',
                           add_book=add_book, form=form,
                           book=book, title='Edit Book')


@user.route('/books/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_book(id):
    book = Book.query.get_or_404(id)
    if book.is_borrowed == 1:
        flash('This book is borrowed and cannot be removed.')
        return redirect(url_for('user.list_books'))
    db.session.delete(book)
    db.session.commit()
    flash('You have successfully deleted the book.')
    return redirect(url_for('user.list_books'))

