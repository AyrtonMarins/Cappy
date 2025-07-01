import sys
import json
import re
from datetime import datetime
# Importação explícita e correta, incluindo as novas funções
from database import (
    add_project, delete_project, get_project_by_name, update_project_name, update_project_due_date,
    add_task, update_task_status, delete_task, update_task_name, update_task_due_date,
    get_all_projects_with_tasks,
    add_activity, get_activities_by_date, update_activity_status, delete_activity,
    get_pending_activities_by_date,
    get_dashboard_tasks # A função que estava faltando!
)

USER_NAME = "Ayrton"

def parse_due_date(text):
    match = re.search(r'\s+até\s+([0-9]{4}-[0-9]{2}-[0-9]{2})$', text)
    if match:
        return text[:match.start()].strip(), match.group(1)
    return text, None

def get_response(user_message):
    message_lower = user_message.lower()

    # --- COMANDOS ESPECIAIS (UI) ---
    if message_lower == "get_dashboard_data":
        today_str = datetime.now().strftime("%Y-%m-%d")
        tasks = get_dashboard_tasks()
        activities = get_activities_by_date(today_str)
        return json.dumps({
            "status": "success",
            "data_type": "dashboard_data",
            "data": {"tasks": tasks, "activities": activities}
        })

    if "crie um projeto:" in message_lower:
        content = user_message.split(":", 1)[1].strip()
        project_name, due_date = parse_due_date(content)
        if not project_name: return json.dumps({"status": "error", "message": "Nome do projeto não pode ser vazio."})
        if add_project(project_name, due_date):
            msg = f"Projeto '{project_name}' criado" + (f" com prazo para {due_date}" if due_date else "") + "!"
            return json.dumps({"status": "success", "message": msg, "data_type": "project_created"})
        else:
            return json.dumps({"status": "error", "message": f"Projeto '{project_name}' já existe."})

    if "crie uma tarefa:" in message_lower:
        content = user_message.split(":", 1)[1].strip()
        project_id, project_name_for_msg = None, ""
        if " para o projeto:" in content.lower():
            task_content, project_name = content.split(" para o projeto:", 1)
            task_name, due_date = parse_due_date(task_content.strip())
            project = get_project_by_name(project_name.strip())
            if not project: return json.dumps({"status": "error", "message": f"Projeto '{project_name.strip()}' não encontrado."})
            project_id, project_name_for_msg = project['id'], project['name']
        else:
            task_name, due_date = parse_due_date(content)
        if not task_name: return json.dumps({"status": "error", "message": "Nome da tarefa não pode ser vazio."})
        add_task(task_name, project_id, due_date)
        msg = f"Tarefa '{task_name}' criada" + (f" para o projeto '{project_name_for_msg}'" if project_id else "") + (f" com prazo para {due_date}" if due_date else "") + "!"
        return json.dumps({"status": "success", "message": msg, "data_type": "task_created"})

    if message_lower == "get_daily_greeting":
        pending_activities = get_pending_activities_by_date(datetime.now().strftime("%Y-%m-%d"))
        greeting = f"Olá, {USER_NAME}! Bem-vindo.\n"
        if not pending_activities: greeting += "Nenhuma atividade pendente para hoje."
        else: greeting += "Suas atividades pendentes para hoje são:\n" + "\n".join([f"- {act['name']}" for act in pending_activities])
        return json.dumps({"status": "success", "message": greeting.strip(), "data_type": "daily_greeting"})

    if message_lower.startswith("edit_project_due_date:"):
        try: _, project_id_str, new_date = user_message.split(":", 2); update_project_due_date(int(project_id_str), new_date if new_date and new_date != 'null' else None); return json.dumps({"status": "success", "data_type": "project_updated"})
        except: pass
    if message_lower.startswith("edit_task_due_date:"):
        try: _, task_id_str, new_date = user_message.split(":", 2); update_task_due_date(int(task_id_str), new_date if new_date and new_date != 'null' else None); return json.dumps({"status": "success", "data_type": "task_updated"})
        except: pass
    if message_lower.startswith("edit_project:"):
        try: _, project_id_str, new_name = user_message.split(":", 2); update_project_name(int(project_id_str), new_name); return json.dumps({"status": "success", "data_type": "project_updated"})
        except: pass
    if message_lower.startswith("edit_task:"):
        try: _, task_id_str, new_name = user_message.split(":", 2); update_task_name(int(task_id_str), new_name); return json.dumps({"status": "success", "data_type": "task_updated"})
        except: pass
    if message_lower.startswith("update_activity_status:"):
        try: _, activity_id_str, new_status = user_message.split(":"); update_activity_status(int(activity_id_str), new_status); return json.dumps({"status": "success", "data_type": "activity_updated"})
        except: pass
    if message_lower.startswith("delete_activity:"):
        try: _, activity_id_str = user_message.split(":"); delete_activity(int(activity_id_str)); return json.dumps({"status": "success", "data_type": "activity_deleted"})
        except: pass
    if message_lower.startswith("delete_project:"):
        try: _, project_id_str = user_message.split(":"); delete_project(int(project_id_str)); return json.dumps({"status": "success", "data_type": "project_deleted"})
        except: pass
    if message_lower.startswith("update_task_status:"):
        try: _, task_id_str, new_status = user_message.split(":"); update_task_status(int(task_id_str), new_status); return json.dumps({"status": "success", "data_type": "task_updated"})
        except: pass
    if message_lower.startswith("delete_task:"):
        try: _, task_id_str = user_message.split(":"); delete_task(int(task_id_str)); return json.dumps({"status": "success", "data_type": "task_deleted"})
        except: pass
    if message_lower == "get_all_projects":
        return json.dumps({"status": "success", "data_type": "project_list", "data": get_all_projects_with_tasks()})
    if message_lower == "get_daily_schedule":
        return json.dumps({"status": "success", "data_type": "daily_schedule_data", "data": get_activities_by_date(datetime.now().strftime("%Y-%m-%d"))})

    # --- FALLBACK ---
    add_activity(user_message)
    return json.dumps({"status": "success", "message": f"Atividade '{user_message}' registrada.", "data_type": "activity_created"})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(get_response(sys.argv[1]))