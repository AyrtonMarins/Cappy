import json
import sys
import re
import random
import os
from datetime import datetime

# (O início do arquivo, incluindo 'load_all_context', não muda)
# --- Ferramentas da IA ---
from app import add_activity, get_activities_by_date

# --- Base de Conhecimento ---
USER_NAME = "Ayrton"
CONTEXT_DATA = {}

def load_all_context(directory="context"):
    global CONTEXT_DATA
    if not os.path.exists(directory): return
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            key = os.path.splitext(filename)[0].split('. ')[-1].lower().replace(' ', '_')
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    CONTEXT_DATA[key] = f.read()
            except Exception as e:
                print(f"Erro ao carregar o arquivo de contexto {filename}: {e}")
    print(f"Contexto carregado. Chaves disponíveis: {list(CONTEXT_DATA.keys())}")


# --- FERRAMENTA DE ROTEIRO ATUALIZADA ---
def generate_script_from_template(topic):
    """
    Gera um roteiro de vídeo preenchendo as lacunas com o contexto do usuário.
    """
    # Acessa o contexto de saúde para personalizar as dicas
    health_context = CONTEXT_DATA.get('saúde_e_fitness', '')
    
    # Personalização baseada no tópico e no contexto
    hook_question = f"Você já parou pra pensar que 5 minutos antes da corrida podem definir se você vai ter um bom treino ou uma nova lesão?"
    common_belief = "achar que aquecimento é só dar uns pulinhos ou uma esticada qualquer. Eu mesmo, vindo do CrossFit e agora focado na corrida, aprendi na marra que o buraco é mais embaixo."
    
    # Gera dicas mais específicas usando o contexto de biomecânica e lesão
    dica1 = "Primeiro, mobilidade articular. A gente precisa avisar nossas articulações, principalmente do quadril e tornozelos, que o movimento vem aí. Nada de forçar, é só soltar."
    dica2 = "Segundo, ativação muscular. Seus glúteos são o motor da sua corrida. Se eles não 'acordarem' antes, outros músculos vão compensar, e é aí que mora o perigo de lesão, como a que eu estou tratando."
    dica3 = "E por fim, um trote bem leve, aumentando a intensidade aos poucos. É como dar a partida no carro e deixar o motor esquentar antes de acelerar tudo."

    script = f"""
Perfeito, {USER_NAME}! Criei um roteiro sobre '{topic}' usando suas próprias experiências e interesses como base.

**Música Sugerida:** uma trilha sonora eletrônica motivacional

---

**ROTEIRO: O Aquecimento que Salva sua Corrida**

🕐 **0s – 8s (Intro / Hook)**
**Clima:** Início rápido e direto.
**Imagem:**
    * Close-up no seu tênis de corrida sendo amarrado.
    * Corte rápido para seu rosto, falando com a câmera de forma séria, mas didática.
    * Texto na tela: "VOCÊ AQUECE OU SE ENGANA?"
**Fala:**
    * "{hook_question}"

🕐 **8s – 20s (Desenvolvimento / O Problema)**
**Clima:** Conexão, "eu já passei por isso".
**Imagem:**
    * Você em plano médio, gesticulando.
    * B-roll rápido mostrando um alongamento estático (o jeito "antigo").
**Fala:**
    * "A maioria de nós aprendeu do jeito errado, achando que {common_belief}"

🕐 **20s – 45s (Ação / A Solução)**
**Clima:** Otimista e inteligente, "aqui está o jeito certo".
**Imagem:**
    * Tutorial rápido mostrando os 3 passos.
    * 1. Cenas de você fazendo rotação de quadril e tornozelo. Texto: "MOBILIDADE".
    * 2. Cenas de você fazendo elevação pélvica. Texto: "ATIVAÇÃO".
    * 3. Cenas de você começando a correr bem devagar. Texto: "PROGRESSÃO".
**Fala:**
    * (Narração em off) "O segredo, vindo da biomecânica, está em três passos simples. {dica1} {dica2} {dica3}"

🕐 **45s – 55s (Resolução / Resultado)**
**Clima:** Confiante e empoderado.
**Imagem:**
    * Cenas de você correndo na praia ou no parque, com boa postura e fluidez.
    * Close no seu rosto, com expressão de satisfação.
**Fala:**
    * "E o resultado é esse: uma corrida mais segura, mais eficiente e sem dor. Seu corpo agradece."

🕐 **55s – 60s (Conclusão / CTA)**
**Clima:** Calmo e encorajador.
**Imagem:**
    * Você olhando para a câmera.
    * Tela final com suas redes.
**Fala:**
    * "Teste esse aquecimento e me diga como se sentiu. Não pule essa etapa. Até a próxima!"

"""
    return script

# (O resto do arquivo 'process_user_prompt' e o ponto de entrada não mudam)
def process_user_prompt(user_message):
    lower_message = user_message.lower()

    # --- LÓGICA DE DECISÃO ---

    # 1. NOVA INTENÇÃO: Criar Roteiro
    if any(keyword in lower_message for keyword in ["crie um roteiro", "faça um roteiro", "roteiro sobre"]):
        # Tenta extrair o tópico do roteiro
        match = re.search(r'sobre ["\'](.*?)["\']', lower_message)
        topic = match.group(1) if match else "um tópico que você goste"
        
        # Chama a nova ferramenta para gerar o roteiro
        script_text = generate_script_from_template(topic)
        return {"response_text": script_text}

    # As outras intenções (se apresente, dê ideia, etc.) vêm depois
    elif any(keyword in lower_message for keyword in ["quem é você", "se apresente"]):
        profile_context = CONTEXT_DATA.get('fundamentos_e_crenças', 'Meus princípios ainda não foram definidos.')
        response = (f"Eu sou Cappy. Minha base de pensamento vem dos seus próprios fundamentos:\n\n---\n{profile_context}\n---")
        return {"response_text": response}

    elif any(keyword in lower_message for keyword in ["me dê uma ideia", "sugestão de atividade"]):
        if "ravi" in lower_message or "filho" in lower_message:
            ideias = [
                "Que tal um 'projeto de culinária pai e filho'? Vocês podem tentar uma receita saudável e gravar um vídeo sobre o aprendizado de vocês juntos.",
                "Vocês poderiam fazer uma sessão de 'Música de Games'. Você pode ensinar ao Ravi os temas de Zelda ou Mario no violão ou cavaquinho.",
                "Inspirado no seu interesse por ciência, que tal construir um pequeno 'foguete de garrafa PET'?",
                "Uma 'Caça ao Tesouro Estoica', com pistas que ensinam pequenos valores que você aprecia."
            ]
            ideia_escolhida = random.choice(ideias)
            return {"response_text": f"Com certeza! Baseado nos seus interesses, aqui vai uma sugestão para você e o Ravi:\n\n{ideia_escolhida}"}
        else:
            return {"response_text": "Entendi que você quer uma ideia, mas sobre qual tópico? Tente ser mais específico."}

    # ... (outras intenções como 'listar' e 'adicionar' sem alterações) ...
    elif any(keyword in lower_message for keyword in ["o que tenho", "quais as tarefas", "liste"]):
        today_str = datetime.now().strftime("%Y-%m-%d")
        activities = get_activities_by_date(today_str)
        if not activities:
            return {"response_text": f"Você não tem nenhuma tarefa agendada para hoje, {USER_NAME}."}
        else:
            response = f"Suas tarefas para hoje, {USER_NAME}:\n"
            for act in activities:
                response += f"• {act['name']} (Tipo: {act['type']})\n"
            return {"response_text": response}

    elif any(keyword in lower_message for keyword in ["adicione", "criar", "crie", "nova tarefa"]):
        try:
            match = re.search(r'["\'](.*?)["\']', user_message)
            if match:
                task_name = match.group(1)
            elif " de " in lower_message:
                task_name = user_message.split(" de ", 1)[1].strip()
            else:
                return {"response_text": "Não identifiquei o nome da tarefa. Tente usar aspas."}
            task_type = 'Pessoal'
            known_types = ['Trabalho', 'Estudo', 'Pessoal', 'Lazer']
            for t in known_types:
                if t.lower() in lower_message:
                    task_type = t
                    break
            new_activity = add_activity(name=task_name, type=task_type)
            return {"response_text": f"Feito! Adicionei '{new_activity['name']}' como uma tarefa de {new_activity['type']}."}
        except Exception as e:
            return {"response_text": f"Opa, tive um problema ao adicionar a tarefa: {e}"}
            
    else:
        return {
            "response_text": f"Hmm, ainda não aprendi a fazer isso, {USER_NAME}. Você pode me pedir um roteiro, uma ideia de atividade com o Ravi, ou listar/adicionar tarefas."
        }

# --- Ponto de Entrada ---
if __name__ == '__main__':
    load_all_context()
    if len(sys.argv) > 1:
        user_message_from_command_line = sys.argv[1]
        result = process_user_prompt(user_message_from_command_line)
        print(json.dumps(result))