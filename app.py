from flask import Flask, request, jsonify, render_template_string, redirect
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)
DB = "tasks.db"

if not os.path.exists(DB):
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE tasks (id INTEGER PRIMARY KEY, name TEXT, done INTEGER DEFAULT 0)")
    conn.close()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8">
  <title>Lista zadań</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5">
  <h2 class="mb-4 text-center">📝 Moja lista zadań</h2>
  <form class="d-flex mb-4" onsubmit="addTask(); return false;">
    <input class="form-control me-2" type="text" id="newtask" placeholder="Nowe zadanie">
    <button class="btn btn-primary" type="submit">Dodaj</button>
  </form>
  <ul class="list-group" id="tasks"></ul>
</div>

<script>
async function loadTasks() {
  const res = await fetch('/tasks');
  const data = await res.json();
  const list = document.getElementById('tasks');
  list.innerHTML = '';
  data.forEach(task => {
    const li = document.createElement('li');
    li.className = 'list-group-item d-flex justify-content-between align-items-center';

    const text = document.createElement('span');
    text.textContent = task.name;
    if (task.done) text.style.textDecoration = "line-through";
    text.style.cursor = "pointer";
    text.onclick = () => toggleDone(task.id);

    const del = document.createElement('button');
    del.className = 'btn btn-danger btn-sm';
    del.textContent = '🗑️';
    del.onclick = () => deleteTask(task.id);

    li.appendChild(text);
    li.appendChild(del);
    list.appendChild(li);
  });
}

async function addTask() {
  const input = document.getElementById('newtask');
  const name = input.value.trim();
  if (!name) return;
  await fetch('/tasks', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name})
  });
  input.value = '';
  loadTasks();
}

async function deleteTask(id) {
  await fetch('/delete/' + id, { method: 'DELETE' });
  loadTasks();
}

async function toggleDone(id) {
  await fetch('/complete/' + id, { method: 'PATCH' });
  loadTasks();
}

loadTasks();
</script>
</body>
</html>
'''

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id, name, done FROM tasks")
    tasks = [{"id": row[0], "name": row[1], "done": bool(row[2])} for row in cur.fetchall()]
    conn.close()
    return jsonify(tasks)

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json(force=True)
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "name required"}), 400
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO tasks (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"}), 201

@app.route("/delete/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})

@app.route("/complete/<int:task_id>", methods=["PATCH"])
def complete_task(task_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT done FROM tasks WHERE id = ?", (task_id,))
    row = cur.fetchone()
    if row is None:
        return jsonify({"error": "not found"}), 404
    new_status = 0 if row[0] else 1
    cur.execute("UPDATE tasks SET done = ? WHERE id = ?", (new_status, task_id))
    conn.commit()
    conn.close()
    return jsonify({"status": "updated"})
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
nano app.py
