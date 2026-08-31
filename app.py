import sqlite3
from flask import Flask, render_template, request
app = Flask(__name__)

con = sqlite3.connect("database.db")
cur = con.cursor()

result = cur.execute("SELECT * FROM INTERSECTION")
path_id = result.fetchall()





@app.route("/", methods=["GET", "POST"])
def index():
    # The default background image that always stays on screen
    base_image = "hello.jpg"

    # List your transparent overlay files here
    overlay_options = {
        "option1": "le_png.png",
        "option2": "img1.jpg",
    }

    selected_option = None
    overlay_image = None

    if request.method == "POST":
        # Get the option selected by the user
        selected_option = request.form.get("overlay_choice")
        # Find the matching transparent image filename
        overlay_image = overlay_options.get(selected_option)

    return render_template(
        "index.html",
        base_image=base_image,
        overlay_image=overlay_image,
        selected_option=selected_option,
    )