from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

basedir = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'books.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

api = Api(app, doc='/', title="A book API", description="A simple REST API for books")

db = SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    author = db.Column(db.String(40), nullable=False)
    date_added = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return self.title


book_model = api.model(
    'Book',
    {
        'id': fields.Integer(),
        'title': fields.String(),
        'author': fields.String(),
        'date_joined': fields.String(),
    }
)


@api.route('/books')
@api.response(200, 'Success', book_model)
class Books(Resource):
    @api.marshal_list_with(book_model, envelope='books')
    def get(self):
        """ Get all books """
        books = Book.query.all()
        return books

    @api.response(201, 'Success', book_model)
    @api.doc('Provide title and author to create a book')
    @api.marshal_with(book_model, envelope="book")
    def post(self):
        """ Create a new book """
        data = request.get_json()
        title = data.get('title')
        author = data.get('author')
        new_book = Book(title=title, author=author)
        db.session.add(new_book)
        db.session.commit()
        return new_book


@api.route('/book/<int:id>')
@api.response(200, 'Success', book_model)
class BookResource(Resource):
    @api.marshal_with(book_model, envelope="book")
    def get(self, ids):
        """ Get a book by id """
        book = Book.query.get_or_404(ids)
        return book

    @api.marshal_with(book_model, envelope="book")
    def put(self, ids):
        """ Update a book"""
        book_to_update = Book.query.get_or_404(ids)
        data = request.get_json()
        book_to_update.title = data.get('title')
        book_to_update.author = data.get('author')
        db.session.commit()
        return book_to_update

    @api.marshal_with(book_model, envelope="book to delete")
    def delete(self, ids):
        """Delete a book"""
        book_to_delete = Book.query.get_or_404(ids)
        db.session.delete(book_to_delete)
        db.session.commit()
        return book_to_delete


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Book': Book
    }


if __name__ == '__main__':
    app.run(debug=True)
