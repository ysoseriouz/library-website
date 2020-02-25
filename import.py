# manage PostgraSQL database
# import books.csv into PostgreSQL database
import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

tables = ["users", "books", "reviews"]

# Run a custom sql command
def runSqlCmd():
    print("------------------------------------")
    cmd = input("sql: ")
    db.execute(cmd)
    db.commit()
    print("Completed!!!")
    print("------------------------------------")

# Create tables and load books.csv
def importData():
    print("------------------------------------")
    db.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username VARCHAR (50) UNIQUE NOT NULL, password VARCHAR (50) NOT NULL, register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);");
    db.execute("CREATE TABLE IF NOT EXISTS books (id SERIAL PRIMARY KEY, isbn VARCHAR UNIQUE NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year INTEGER);")
    db.execute("CREATE TABLE IF NOT EXISTS reviews (id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users, book_id INTEGER REFERENCES books, review VARCHAR, rating_score INT NOT NULL CHECK (rating_score >= 0 AND rating_score <= 5), time TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
    f = open("books.csv")
    # skip first line
    f.readline()
    reader = csv.reader(f)
    i = 1
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"{i}: Added {isbn}")
        i += 1
    db.commit()
    f.close()
    print("Completed!!!")
    print("------------------------------------")

# Show all data of table
def showTable():
    print("------------------------------------")
    for i in range(len(tables)):
        print(str(i + 1) + ". " + tables[i])
    option = int(input("Which table: "))
    table = db.execute("SELECT * FROM " + tables[option - 1]).fetchall()
    for data in table:
        print(data)
    if len(table) == 0:
        print("No data")
    print("------------------------------------")

# Delete all data of table
def deleteTable():
    print("------------------------------------")
    for i in range(len(tables)):
        print(str(i + 1) + ". " + tables[i])
    option = int(input("Which table: "))
    db.execute("DELETE FROM " + tables[option - 1])
    db.execute("ALTER SEQUENCE " + tables[option - 1] + "_id_seq RESTART WITH 1")
    db.commit()
    print(f"Deleted {tables[option - 1]}")
    print("------------------------------------")

def main():
    print("------------------------------------")
    print("0. Run sql command")
    print("1. Import books.csv")
    print("2. Show table")
    print("3. Delete table")
    print("Press any key to exit.")
    print("------------------------------------")
    while True:
        try:
            option = int(input("Choose option: "))
            if option == 0:
                runSqlCmd()
            elif option == 1:
                importData()
            elif option == 2:
                showTable()
            elif option == 3:
                deleteTable()
            else:
                return
        except:
            return

if __name__ == "__main__":
    main()
