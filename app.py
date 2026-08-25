import sqlite3
from flask import Flask, render_template, request
app = Flask(__name__)

con = sqlite3.connect("database.db")
cur = con.cursor()

result = cur.execute("SELECT * FROM INTERSECTION")
path_id = result.fetchall()

image_map = {"img1": "img1.jpg", "img2": "img2.jpg"}

@app.route("/", methods=["GET","POST"])
def home():
    selected_image = "img1"

    if request.method == "POST":
        selected_image = request.form.get("images", "img1")
    image_file = image_map.get(selected_image, "img1.png)")

    return render_template("index.html", selected = selected_image, image = image_file)

