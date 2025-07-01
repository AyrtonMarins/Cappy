import sqlite3
import sys
import json
from database import get_db_connection, create_tables
from datetime import datetime
import handler # <-- CORRIGIDO para corresponder ao seu nome de arquivo

# --- Funções do Banco de Dados (sem alterações) ---

def add_activity(name, type):
    conn = get_db_connection()
    cursor = conn.cursor()
    scheduled_for = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute( "INSERT INTO activities (name, type, scheduled_for) VALUES (?, ?, ?)", (name, type, scheduled_for) )
    activity_id = cursor.lastrowid
    conn.commit()
    conn.close()
    # MUDANÇA AQUI: Retorna um dicionário completo
    return {"id": activity_id, "name": name, "type": type}

def get_activities_by_date(date_str):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row 
    activities = [dict(row) for row in conn.execute( "SELECT id, name, type, status FROM activities WHERE date(scheduled_for) = ?", (date_str,) ).fetchall()]
    conn.close()
    return activities

def get_activity_details(activity_id):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    details = conn.execute( "SELECT id, name, type, status, scheduled_for, created_at FROM activities WHERE id = ?", (activity_id,) ).fetchone()
    conn.close()
    return dict(details) if details else None

# --- Roteador de Comandos ---

def main():
    if len(sys.argv) < 2: return

    command = sys.argv[1]

    if command == "get_activities_today":
        today_str = datetime.now().strftime("%Y-%m-%d")
        activities = get_activities_by_date(today_str)
        print(json.dumps(activities))
    
    elif command == "add_activity":
        name = sys.argv[2]
        activity_type = sys.argv[3]
        activity_id = add_activity(name, activity_type)
        print(json.dumps({"success": True, "activity_id": activity_id}))

    elif command == "get_activity_details":
        activity_id = sys.argv[2]
        details = get_activity_details(activity_id)
        print(json.dumps(details))
    
    elif command == "process_chat_message":
        user_message = sys.argv[2]
        # CORRIGIDO para usar o nome de módulo 'handler'
        ai_response = handler.process_user_prompt(user_message)
        print(json.dumps(ai_response))

# --- Bloco de Execução Principal ---
if __name__ == '__main__':
    create_tables()
    main()
