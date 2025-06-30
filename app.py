# Importações necessárias
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import openai
import os

# Carrega as variáveis de ambiente (necessário para pegar a OPENAI_API_KEY)
load_dotenv()

# Inicializa o aplicativo Flask
app = Flask(__name__)

# Configura o cliente da OpenAI
# Ele vai procurar a variável de ambiente "OPENAI_API_KEY" automaticamente
try:
    client = openai.OpenAI()
except openai.OpenAIError as e:
    # Se a chave não for encontrada, o programa não vai nem iniciar.
    # Isso é melhor do que dar erro durante uma requisição.
    print("Erro: A variável de ambiente OPENAI_API_KEY não foi encontrada.")
    print("Por favor, crie um arquivo .env e adicione a linha: OPENAI_API_KEY='sua_chave_aqui'")
    client = None

# Define a rota da API para o chat
@app.route('/api/chat', methods=['POST'])
def chat():
    # Verifica se o cliente da OpenAI foi inicializado corretamente
    if client is None:
        return jsonify({"error": "O servidor não está configurado com uma chave de API da OpenAI."}), 500

    # Pega os dados JSON enviados pelo frontend
    data = request.get_json()
    if not data or 'messages' not in data:
        return jsonify({"error": "O corpo da requisição precisa ser um JSON com uma chave 'messages'."}), 400

    messages_history = data['messages']

    try:
        # Faz a chamada para a API da OpenAI
        response_object = client.chat.completions.create(
            model="gpt-4o",  # Ou o modelo que você preferir
            messages=messages_history
        )

        # --- A CORREÇÃO ESTÁ AQUI ---
        # Em vez de retornar o objeto inteiro, nós extraímos apenas o texto da resposta.
        ai_message_text = response_object.choices[0].message.content

        # Retornamos um JSON simples que o frontend consegue entender.
        return jsonify({"response": ai_message_text})

    except openai.APIError as e:
        # Captura erros específicos da API da OpenAI
        return jsonify({"error": f"Erro na API da OpenAI: {str(e)}"}), 500
    except Exception as e:
        # Captura qualquer outro erro inesperado no servidor
        return jsonify({"error": f"Um erro inesperado ocorreu: {str(e)}"}), 500

# Bloco para rodar o aplicativo diretamente
# Inclui a correção 'use_reloader=False' para evitar erros no Windows
if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
