import sqlite3
from flask import Flask
app = Flask(__name__)

con = sqlite3.connect("database.db")
cur = con.cursor()

result = cur.execute("SELECT * FROM INTERSECTION")
path_id = result.fetchall()

@app.route("/")
def home():
    return (path_id[0][0])

