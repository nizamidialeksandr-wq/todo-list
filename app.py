from datetime import datetime
import sqlite3

from flask import Flask, request, render_template, redirect, url_for, jsonify

app = Flask(__name__)
DB = "database.db"


def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)
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




@app.route("/")
def lists():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    all_lists = conn.execute("SELECT * FROM lists ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("lists.html", all_lists=all_lists)


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "GET":
        return render_template("create.html")

    name = request.form["name"].strip()
    description = request.form["description"].strip()

    conn = sqlite3.connect(DB)
    cur = conn.execute(
        "INSERT INTO lists (name, description) VALUES (?, ?)",
        (name, description),
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()

    return redirect(url_for("todo", list_id=new_id))


@app.route("/todo/<int:list_id>")
def todo(list_id):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    current_list = conn.execute(
        "SELECT * FROM lists WHERE id = ?", (list_id,)
    ).fetchone()
    tasks = conn.execute(
        "SELECT * FROM tasks WHERE list_id = ?", (list_id,)
    ).fetchall()
    conn.close()

    if current_list is None:
        return redirect(url_for("lists"))

    return render_template("todo.html", current_list=current_list, tasks=tasks)


@app.route("/todo/<int:list_id>/add_task", methods=["POST"])
def add_task(list_id):
    task_text = request.form["task_text"].strip()
    if task_text:
        conn = sqlite3.connect(DB)
        conn.execute(
            "INSERT INTO tasks (list_id, text) VALUES (?, ?)",
            (list_id, task_text),
        )
        conn.commit()
        conn.close()
    return redirect(url_for("todo", list_id=list_id))


@app.route("/toggle_task/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
    conn = sqlite3.connect(DB)
    task = conn.execute(
        "SELECT is_done, list_id FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    if task:
        new_status = 0 if task[0] == 1 else 1
        conn.execute(
            "UPDATE tasks SET is_done = ? WHERE id = ?", (new_status, task_id)
        )
        conn.commit()
        list_id = task[1]
    else:
        conn.close()
        return redirect(url_for("lists"))
    conn.close()
    return redirect(url_for("todo", list_id=list_id))


@app.route("/delete_task/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    conn = sqlite3.connect(DB)
    task = conn.execute(
        "SELECT list_id FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    if task:
        list_id = task[0]
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        return redirect(url_for("todo", list_id=list_id))
    conn.close()
    return redirect(url_for("lists"))


@app.route("/delete_list/<int:list_id>", methods=["POST"])
def delete_list(list_id):
    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM lists WHERE id = ?", (list_id,))
    conn.execute("DELETE FROM tasks WHERE list_id = ?", (list_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("lists"))


@app.route("/last_todo")
def last_todo():
    return redirect(url_for("lists"))


@app.route("/api/items")
def api():
    return jsonify({
        "name": "уборка",
        "description": "выбросить мусор, пропылесосить диван",
        "time": "15:36",
        "date": "26.11.2026",
        "is_done": False,
    })