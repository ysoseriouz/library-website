# Project 1

Web Programming with Python using Flask framework and PostgreSQL database on Heroku

# Database configuration
Host: ec2-174-129-255-57.compute-1.amazonaws.com
Database: d6bbcnaojfmt0u
User: wmlbfudqisvzpp
Port: 5432
Password: 89bb39ed8a020b82d38cbb57f1f26d21582a3b481d63ca68cd253f0cfde5b530
URI: postgres://wmlbfudqisvzpp:89bb39ed8a020b82d38cbb57f1f26d21582a3b481d63ca68cd253f0cfde5b530@ec2-174-129-255-57.compute-1.amazonaws.com:5432/d6bbcnaojfmt0u
Heroku CLI: heroku pg:psql postgresql-corrugated-12003 --app book-review-website-thanh2612

# import.py
Extract data from books.csv and store into database
Using only raw sqlalchemy

# main.py
Define functions for routes
- index(): render sign-in page
- register(): render sign-up page
- logout(): clear user's session and logout
- library(): render main page of library with data stored in database
- book(id): go to detail page of a book by id
- bookDetailsInJSON(): create my own simple API
