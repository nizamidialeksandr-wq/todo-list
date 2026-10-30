from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, jsonify, render_template_string
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/create", methods=["GET", "POST"], endpoint="create")
def create():
    if request.method == "GET":
        return render_template("create.html")
    elif request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]

        conn = sqlite3.connect("database.db")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL
            )
        """)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (name, description) VALUES (?, ?)", (name, description))
        conn.commit()
        
        # Получаем ID только что созданного списка
        new_id = cursor.lastrowid 
        conn.close()

        # Перекидываем на страницу ЭТОГО списка
        return redirect(url_for("todo", list_id=new_id))

@app.route("/todo/<int:list_id>")
def todo(list_id):
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    
    # 1. Получаем текущий список
    current_list = conn.execute("SELECT * FROM orders WHERE id = ?", (list_id,)).fetchone()
    
    # 2. Получаем ВСЕ списки для левого меню
    all_lists = conn.execute("SELECT * FROM orders").fetchall()
    conn.close()

    if current_list is None:
        return redirect(url_for("home"))

    return render_template("todo.html", current_list=current_list, all_lists=all_lists)

@app.route("/orders")
def orders():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    orders = conn.execute("SELECT * FROM orders").fetchall()
    conn.close()
    return render_template("orders.html", orders=orders)

@app.route("/api/items")
def api():
    data = {
        'name' : 'уборка',
        'description' : 'выбросить мусор, пропылесосить диван',
        'time' : '15:36',
        'date' : '26.11.2026',
        'is_done' : 'False'
    }
    return data