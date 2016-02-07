"""
"""
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy

import os

DB_DIR = "database"
db_name = 'books.sqlite'
sqlite_db = 'sqlite:////' + os.path.join(os.getcwd(), 'database', db_name)

# haven't used this in the templates, currently using exact path on a few files.
STATIC_DIR = "static"

app = Flask(__name__)

#sqlalchemy configuration
app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_db
db = SQLAlchemy(app)

# flask will reload itself on changes when debug is True
# flask can execute arbitrary code if you set this True
app.debug = True 

PAGINATE_BY_HOWMANY = 15


class Book(db.Model):
    """ Build a model based on the available fields in the openlibrary.org API.

    Notes: 
        authors - will be stored as a long string, openlibrary delivers it as a list of objects.

    Additional info:
        curl 'https://openlibrary.org/api/books?bibkeys=ISBN:9780980200447&jscmd=data&format=json'
        using jscmd=data yields less info but is more stable
        using jscmd=details will give us book cover thumbnail, preview url, table of contents, and more

    Enhancements:
        use jscmd=details to get cover thumbnail... this could be a key piece of the template
    """
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True)
    title = db.Column(db.String(200), unique=False)
    authors = db.Column(db.String(200), unique=False)
    publish_date = db.Column(db.String(20), unique=False)
    number_of_pages = db.Column(db.String(20), unique=False)

    def __init__(self, isbn, title, number_of_pages, publish_date, authors):
        self.isbn = isbn
        self.title = title
        self.authors = authors
        self.publish_date = publish_date
        self.number_of_pages = number_of_pages

    def __repr__(self):
        return '<Title: >'.format(self.title)

@app.route("/test/")
def test():
    return render_template('test.html')

@app.route("/")
def home():
    return redirect(url_for('index', page=1))

@app.route("/index/<int:page>/")
@app.route("/<isbn>")
def index(page=1, isbn=None):
    # this is a possible method for filtering or showing individual books.
    # a different template can be used if an isbn is provided.
    s = request.args.get('s')
    if s:
        books = Book.query.order_by(Book.title.asc()).filter(Book.title.contains(s)).paginate(page,PAGINATE_BY_HOWMANY,False)

    else:
        books = Book.query.order_by(Book.title.asc()).paginate(page,PAGINATE_BY_HOWMANY,False)

    return render_template('index.html', books=books, s=s)

if __name__ == "__main__":
    # flask can execute arbitrary python if you do this.
    # app.run(host='0.0.0.0') # listens on all public IPs. 

    app.run()

