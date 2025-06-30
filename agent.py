import streamlit as st
import openai
import os
import requests
import json
import threading
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- Configuração do Backend com FastAPI ---
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

# Cria uma instância do FastAPI
fastapi_app = FastAPI()

# Pega a chave da API das variáveis de ambiente
api_key_from_env = os.getenv("OPENAI_API_KEY")

# --- Configuração do Frontend com Streamlit ---

st.set_page_config(layout="wide")
st.title("Chat com IA")

# Verifica se a chave da API foi carregada ANTES de continuar
if not api_key_from_env:
    st.error("A variável de ambiente OPENAI_API_KEY não foi encontrada! Verifique seu arquivo .env e reinicie o app.")
    st.stop() # Para a execução do app se a chave não for encontrada

# Inicializa o histórico do chat na sessão do Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Você é um assistente prestativo."}]

# Botão para limpar a conversa
if st.button("Limpar Conversa"):
    st.session_state.messages = [{"role": "system", "content": "Você é um assistente prestativo."}]
    st.rerun()

# Exibe as mensagens do histórico (ignorando a mensagem do sistema)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Input do usuário
if prompt := st.chat_input("Qual a sua dúvida?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                # Faz a chamada para o backend FastAPI
                response = requests.post("http://localhost:8000/chat", json={"history": st.session_state.messages})
                response.raise_for_status()

                response_data = response.json()
                
                if "error" in response_data:
                    ai_response = f"Erro no servidor: {response_data['error']}"
                else:
                    ai_response = response_data.get("response", "Desculpe, ocorreu um erro na resposta.")
                
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.markdown(ai_response)

            except requests.exceptions.RequestException as e:
                st.error(f"Erro de Comunicação com o backend: {e}")
            except Exception as e:
                st.error(f"Ocorreu um erro inesperado: {e}")
    
    st.rerun()

# --- Lógica do Backend ---

@fastapi_app.post("/chat")
async def chat_endpoint(request: Request):
    try:
        body = await request.json()
        messages_history = body.get("history", [])

        if not messages_history:
            return JSONResponse(status_code=400, content={"error": "O histórico de mensagens não pode ser vazio."})

        # A PARTE MAIS IMPORTANTE - A CORREÇÃO DO ERRO
        client = openai.OpenAI(api_key=api_key_from_env)
        response_object = client.chat.completions.create(
            model="gpt-4o",
            messages=messages_history
        )

        # 1. ABRE O PACOTE: acessa a lista de 'choices'
        # 2. PEGA O PRIMEIRO ITEM: [0]
        # 3. ACESSA A MENSAGEM: .message
        # 4. PEGA APENAS O TEXTO: .content
        ai_message_text = response_object.choices[0].message.content

        # Retorna APENAS o texto em um formato JSON simples
        return JSONResponse(content={"response": ai_message_text})

    except Exception as e:
        print(f"Erro no endpoint /chat: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

def run_fastapi_server():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)

# Inicia o servidor FastAPI em background
if "fastapi_thread_started" not in st.session_state:
    threading.Thread(target=run_fastapi_server, daemon=True).start()
    st.session_state.fastapi_thread_started = True
