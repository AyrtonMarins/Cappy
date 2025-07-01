# handler.py

import json
import sys
import re
from datetime import datetime

# --- Ferramentas da IA (IMPORTAÇÃO NOVA) ---
from app import add_activity, get_activities_by_date

# --- Base de Conhecimento ---
USER_NAME = "Ayrton"

def process_user_prompt(user_message):
    """
    Analisa a mensagem do usuário e decide o que fazer.
    """
    lower_message = user_message.lower()

    # --- LÓGICA DE DECISÃO MELHORADA ---

    # 1. Intenção: Saudação (com um toque de proatividade!)
    if lower_message in ["oi", "olá", "ola", "e aí", "e ai", "bom dia", "boa tarde", "boa noite"]:
        # Usando o contexto de que hoje é 1º de Julho e você planejava focar em conteúdo.
        return {"response_text": f"Olá, {USER_NAME}! Bem-vindo a Julho. Ótimo mês para focar na criação de conteúdo, como planejamos. O que vamos organizar hoje?"}

    # 2. Intenção: Listar Tarefas
    list_keywords = ["o que tenho", "quais as tarefas", "minhas tarefas", "liste", "lista de hoje"]
    if any(keyword in lower_message for keyword in list_keywords):
        today_str = datetime.now().strftime("%Y-%m-%d")
        activities = get_activities_by_date(today_str)
        if not activities:
            return {"response_text": f"Você não tem nenhuma tarefa agendada para hoje, {USER_NAME}. Quer adicionar uma?"}
        else:
            # Formata a lista de tarefas para uma resposta clara
            response = f"Claro, {USER_NAME}. Aqui estão suas tarefas para hoje:\n"
            for act in activities:
                response += f"• {act['name']} (Tipo: {act['type']})\n"
            return {"response_text": response}

    # 3. Intenção: Adicionar Tarefa (agora mais inteligente)
    add_keywords = ["adicione", "criar", "crie", "nova tarefa", "lembrete"]
    if any(keyword in lower_message for keyword in add_keywords):
        try:
            # Extrai o nome da tarefa
            match = re.search(r'["\'](.*?)["\']', user_message)
            if match:
                task_name = match.group(1)
            elif " de " in lower_message:
                task_name = user_message.split(" de ", 1)[1].strip()
            else:
                return {"response_text": "Entendi que você quer adicionar algo, mas não identifiquei o nome. Tente usar aspas."}
            
            # NOVO: Tenta extrair o tipo da tarefa
            task_type = 'Pessoal' # Padrão
            known_types = ['Trabalho', 'Estudo', 'Pessoal', 'Lazer']
            for t in known_types:
                if t.lower() in lower_message:
                    task_type = t
                    break

            # CHAMA A FERRAMENTA
            new_activity = add_activity(name=task_name, type=task_type)
            
            # Responde com base no que foi realmente criado
            return {"response_text": f"Feito! Adicionei '{new_activity['name']}' como uma tarefa de {new_activity['type']}. O que mais?"}

        except Exception as e:
            return {"response_text": f"Opa, tive um problema ao adicionar a tarefa: {e}"}

    # 4. Resposta Padrão (Fallback)
    else:
        return {
            "response_text": f"Hmm, ainda não aprendi a fazer isso, {USER_NAME}. Por enquanto, sei adicionar e listar tarefas. Que tal tentar 'o que tenho pra hoje?'"
        }

# --- Ponto de Entrada (sem alterações) ---
if __name__ == '__main__':
    if len(sys.argv) > 1:
        user_message_from_command_line = sys.argv[1]
        result = process_user_prompt(user_message_from_command_line)
        print(json.dumps(result))
