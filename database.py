import sqlite3
from datetime import datetime

DB_NAME = 'cappy_data.db'

def _execute(query, params=(), commit=False):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute(query, params)
    result = cursor.fetchall()
    if commit: conn.commit()
    conn.close()
    return [dict(row) for row in result]

def init_db():
    # ... (código init sem alterações)
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL, due_date TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, project_id INTEGER, name TEXT NOT NULL, status TEXT DEFAULT 'A Fazer', created_at TEXT NOT NULL, due_date TEXT, FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS activities (id INTEGER PRIMARY KEY, name TEXT NOT NULL, date TEXT, status TEXT DEFAULT 'A Fazer')''')
    conn.commit(); conn.close()

# --- NOVA FUNÇÃO para o Painel ---
def get_dashboard_tasks():
    """Busca tarefas atrasadas e para hoje."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    overdue = _execute("SELECT t.*, p.name as project_name FROM tasks t JOIN projects p ON t.project_id = p.id WHERE t.status = 'A Fazer' AND t.due_date < ?", (today_str,))
    due_today = _execute("SELECT t.*, p.name as project_name FROM tasks t JOIN projects p ON t.project_id = p.id WHERE t.status = 'A Fazer' AND t.due_date = ?", (today_str,))
    return {"overdue": overdue, "due_today": due_today}

# --- Funções existentes (sem alterações) ---
def add_project(name, due_date=None):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try: cursor.execute("INSERT INTO projects (name, created_at, due_date) VALUES (?, ?, ?)", (name, created_at, due_date)); conn.commit(); return {"id": cursor.lastrowid}
    except sqlite3.IntegrityError: return None
    finally: conn.close()
def delete_project(project_id): _execute("DELETE FROM projects WHERE id = ?", (project_id,), commit=True)
def update_project_name(project_id, new_name):
    try: _execute("UPDATE projects SET name = ? WHERE id = ?", (new_name, project_id), commit=True); return True
    except: return False
def update_project_due_date(project_id, due_date): _execute("UPDATE projects SET due_date = ? WHERE id = ?", (due_date, project_id), commit=True)
def get_project_by_name(name): result = _execute("SELECT * FROM projects WHERE name = ? COLLATE NOCASE", (name,)); return result[0] if result else None
def add_task(name, project_id=None, due_date=None):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO tasks (project_id, name, status, created_at, due_date) VALUES (?, ?, 'A Fazer', ?, ?)", (project_id, name, created_at, due_date)); conn.commit(); conn.close()
def update_task_status(task_id, new_status): _execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id), commit=True)
def update_task_name(task_id, new_name): _execute("UPDATE tasks SET name = ? WHERE id = ?", (new_name, task_id), commit=True)
def delete_task(task_id): _execute("DELETE FROM tasks WHERE id = ?", (task_id,), commit=True)
def update_task_due_date(task_id, due_date): _execute("UPDATE tasks SET due_date = ? WHERE id = ?", (due_date, task_id), commit=True)
def get_all_projects_with_tasks():
    projects = _execute("SELECT * FROM projects ORDER BY due_date ASC, created_at DESC")
    for p in projects: p['tasks'] = _execute("SELECT * FROM tasks WHERE project_id = ? ORDER BY due_date ASC, created_at ASC", (p['id'],))
    return projects
def add_activity(name): _execute("INSERT INTO activities (name, date, status) VALUES (?, ?, 'A Fazer')", (name, datetime.now().strftime("%Y-%m-%d")), commit=True)
def get_activities_by_date(date_str): return _execute("SELECT * FROM activities WHERE date = ? ORDER BY id ASC", (date_str,))
def get_pending_activities_by_date(date_str): return _execute("SELECT * FROM activities WHERE date = ? AND status = 'A Fazer' ORDER BY id ASC", (date_str,))
def update_activity_status(activity_id, new_status): _execute("UPDATE activities SET status = ? WHERE id = ?", (new_status, activity_id), commit=True)
def delete_activity(activity_id): _execute("DELETE FROM activities WHERE id = ?", (activity_id,), commit=True)

init_db()