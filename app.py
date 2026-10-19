from flask import Flask, request
from flask import render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/contact", methods=["GET", "POST"], endpoint="contact")
def contact():
    if request.method == "GET":
        return render_template("contact.html")
    elif request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]





        conn = sqlite3.connect("database.db")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS todo_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,

        """)
        conn.execute("INSERT INTO todo_list (name, description) VALUES (?, ?)", (name, description))
        conn.commit()
        conn.close()



        return render_template(
            "answer.html",
            name=name,
            description=description,
        )



@app.route("/todo_list")
def todo_list():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    todo_list = conn.execute("SELECT * FROM todo_list").fetchall()
    print(todo_list)
    conn.close()
    return render_template("todo_list.html", todo_list=todo_list)