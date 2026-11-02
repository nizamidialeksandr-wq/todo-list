from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, jsonify, render_template_string
import sqlite3

app = Flask(__name__)

# --- ФУНКЦИЯ ДЛЯ СОЗДАНИЯ ТАБЛИЦ (ВЫЗЫВАЕТСЯ 1 РАЗ ПРИ СТАРТЕ) ---
def init_db():
    conn = sqlite3.connect("database.db")
    # Создаем таблицу списков
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)
    # Создаем таблицу задач
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            list_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            is_done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

# Вызываем инициализацию базы данных сразу при запуске
init_db()
# ------------------------------------------------------------------

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
    
    # 3. ПОЛУЧАЕМ ЗАДАЧИ для этого списка
    tasks = conn.execute("SELECT * FROM tasks WHERE list_id = ?", (list_id,)).fetchall()
    
    conn.close()

    if current_list is None:
        return redirect(url_for("home"))

    # Передаем tasks в HTML
    return render_template("todo.html", current_list=current_list, all_lists=all_lists, tasks=tasks)

@app.route("/todo/<int:list_id>/add_task", methods=["POST"])
def add_task(list_id):
    task_text = request.form["task_text"]
    
    if task_text.strip(): # Если поле не пустое
        conn = sqlite3.connect("database.db")
        conn.execute("INSERT INTO tasks (list_id, text) VALUES (?, ?)", (list_id, task_text))
        conn.commit()
        conn.close()
        
    return redirect(url_for("todo", list_id=list_id))





@app.route("/delete_list/<int:list_id>", methods=["POST"])
def delete_list(list_id):
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row  # <--- ВОТ ЭТА СТРОЧКА ИСПРАВЛЯЕТ ОШИБКУ
    
    # Удаляем сам список и его задачи
    conn.execute("DELETE FROM orders WHERE id = ?", (list_id,))
    conn.execute("DELETE FROM tasks WHERE list_id = ?", (list_id,))
    conn.commit()
    
    # Проверяем, остались ли еще списки в базе
    remaining = conn.execute("SELECT id FROM orders ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    
    if remaining:
        # Теперь remaining['id'] сработает, потому что мы включили row_factory
        return redirect(url_for("todo", list_id=remaining['id']))
    else:
        # Если списков не осталось, перекидываем на страницу "Мои списки"
        return redirect(url_for("last_todo"))






# ФУНКЦИЯ ДЛЯ КНОПКИ "МОИ СПИСКИ"
@app.route("/last_todo")
def last_todo():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    # Ищем самый последний созданный список
    last = conn.execute("SELECT id FROM orders ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    
    if last:
        return redirect(url_for("todo", list_id=last['id']))
    else:
        return redirect(url_for("create"))

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

@app.route("/toggle_task/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
    conn = sqlite3.connect("database.db")
    

    task = conn.execute("SELECT is_done FROM tasks WHERE id = ?", (task_id,)).fetchone()
    
    if task:
        new_status = 0 if task[0] == 1 else 1
        conn.execute("UPDATE tasks SET is_done = ? WHERE id = ?", (new_status, task_id))
        conn.commit()
        
    conn.close()
    return "", 204  


@app.route("/delete_task/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    conn = sqlite3.connect("database.db")


    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()

    return "", 204


