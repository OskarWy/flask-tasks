from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB = "tasks.db"

# Utwórz bazę danych jeśli nie istnieje
if not os.path.exists(DB):
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE tasks (id INTEGER PRIMARY KEY, name TEXT)")
    conn.close()

# Szablon HTML z JS do obsługi API
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Moja lista zadań</title>
  <style>
    body { font-family: sans-serif; max-width: 600px; margin: 30px auto; }
    input, button { font-size: 1em; padding: 0.4em; margin: 0.5em 0; }
    ul { padding-left: 1.2em; }
  </style>
</head>
<body>
  <h2>📋 Moja lista zadań</h2>
  <ul id="tasks"></ul>
  <input type="text" id="newtask" placeholder="Nowe zadanie">
  <button onclick="addTask()">➕ Dodaj</button>

<script>
async function loadTasks() {
  let res = await fetch('/tasks');
  let data = await res.json();
  let list = document.getElementById('tasks');
  list.innerHTML = '';
  data.forEach(t => {
    let li = document.createElement('li');
    li.innerText = t.name;
    list.appendChild(li);
  });
}

async function addTask() {
  let name = document.getElementById('newtask').value;
  if (name.trim() === "") return;
  await fetch('/tasks', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name})
  });
  document.getElementById('newtask').value = '';
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
    cur.execute("SELECT * FROM tasks")
    tasks = [{"id": row[0], "name": row[1]} for row in cur.fetchall()]
    conn.close()
    return jsonify(tasks)

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json(force=True)
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "name required"}), 400
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

