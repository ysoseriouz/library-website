#! /usr/bin/python3
import os, requests

from flask import Flask, session, render_template, flash, redirect, request, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.secret_key = "00022162"
apiKey = "I5ZmdVYnmmpu8itttI8LBA"           # API Key : Goodreads API

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

################################################################################
# Search algorithm
def isMatched(searchTerm, book):
    searchTermLowerCase = searchTerm.lower()
    if searchTermLowerCase in book["isbn"].lower():
        return True
    if searchTermLowerCase in book["title"].lower():
        return True
    if searchTermLowerCase in book["author"].lower():
        return True
    if searchTermLowerCase in str(book["year"]):
        return True
    return False
################################################################################

# Index page: log in page--------------------------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if "user_id" in session and session["user_id"] is not None:
        return redirect(url_for('library'))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = db.execute("SELECT * FROM users WHERE username = :usr AND password = :pwd", {"usr": username, "pwd": password}).fetchone()
        if user:
            session["user_id"] = [user["id"], user["username"]]
            return redirect(url_for('library'))
        else:
            flash('Incorrect username or password!', 'error')
    return render_template("signin.html")

# Register page--------------------------------------------------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmPassword = request.form.get("confirm-password")
        if password == confirmPassword:
            try:
                db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                            {"username": username, "password": password})
                db.commit()
            except:
                return render_template("error.html", message = "404 Error Page Not Found!")
            flash('Registered Successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Passwords must match!', 'error')
    return render_template("signup.html")

# Log out
@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for('index'))

# Main page-------------------------------------------------------------------------------------------------------
@app.route("/library", methods=["GET", "POST"])
def library():
    if "user_id" not in session or session["user_id"] is None:
        return render_template("error.html", message = "404 Error Page Not Found!")
    noBook = True
    booksFound = []
    if request.method == "POST":
        noBook = True
        searchTerm = request.form.get("search-book")
        if searchTerm:
            books = db.execute("SELECT * FROM books").fetchall()
            for book in books:
                if isMatched(searchTerm, book):
                    booksFound.append(book)
                    noBook = False
        else:
            booksFound = db.execute("SELECT * FROM books").fetchall()
            noBook = False
    else:
        booksFound = db.execute("SELECT * FROM books").fetchall()
        noBook = False
    return render_template("library.html", username = session["user_id"][1], books = booksFound, noBook = noBook)

# Book page--------------------------------------------------------------------------------------------------------
@app.route("/book/<int:id>", methods=["GET", "POST"])
def book(id):
    if "user_id" not in session or session["user_id"] is None:
        return render_template("error.html", message = "404 Error Page Not Found!")
    # Fetch book data base on book_id
    book = db.execute("SELECT * FROM books WHERE id=:id", {"id": id}).fetchone()
    if book is None:
        return render_template("error.html", message = "404 Page Not Found")
    # Fetch all reviews of the book
    reviews = db.execute("SELECT username, review, rating_score, time FROM users u INNER JOIN reviews r ON u.id=r.user_id WHERE r.book_id=:id ORDER BY time DESC",
                                {"id": book['id']}).fetchall()
    # Call Goodreads API
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": apiKey, "isbns": book["isbn"]})
    book_data = res.json()
    # Check whether user submited a review
    reviewable = True
    for review in reviews:
        if review["username"] == session["user_id"][1]:
            reviewable = False
            break
    if request.method == "POST":
        userRating = int(request.form.get("rating-score"))
        userReview = request.form.get("review")
        if userRating and userReview and reviewable:
            db.execute("INSERT INTO reviews (user_id, book_id, review, rating_score) VALUES (:user_id, :book_id, :review, :rating_score)",
                        {"user_id": session["user_id"][0], "book_id": id, "review": userReview, "rating_score": userRating})
            db.commit()
            return redirect(url_for('book', id = id))
    # Render page
    return render_template("book.html", username = session["user_id"][1], book = book,  reviewable = reviewable, reviews = reviews, average_rating = book_data["books"][0]["average_rating"], number_of_ratings = book_data["books"][0]["work_ratings_count"])

# My own API-------------------------------------------------------------------------------------------------------
@app.route("/api/<string:isbn>")
def bookDetailsInJSON(isbn):
    # Fetch book data by book_isbn
    book = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return render_template("error.html", message = "404 Page Not Found")
    review_data = db.execute("SELECT COUNT(review), SUM(rating_score) FROM reviews WHERE book_id=:book_id", {"book_id": book["id"]}).fetchone()
    review_count = review_data["count"]
    if review_count == 0:
        review_average_score = 0
    else:
        review_average_score = review_data["sum"] * 1.0 / review_count
    return jsonify({
                        "title": book["title"],
                        "author": book["author"],
                        "year": book["year"],
                        "isbn": book["isbn"],
                        "review_count": review_count,
                        "average_score": review_average_score
                    }), 200

# if __name__ == '__main__':
#     # app.debug = True
#     app.run(host = '0.0.0.0')
