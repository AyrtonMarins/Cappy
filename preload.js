const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  // Esta é a função que o index.html chama
  streamText: async (messages, model, onData, onError, onComplete) => {
    try {
      // 1. A URL foi corrigida para '/api/chat'
      const response = await fetch('http://127.0.0.1:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: messages }), // Enviando o histórico
      });

      // 2. Verifica se a requisição falhou
      if (!response.ok) {
        const errorText = await response.text();
        onError(`Erro do servidor (${response.status}): ${errorText}`);
        return;
      }

      // 3. Pega a resposta JSON completa de uma vez
      const data = await response.json();

      // 4. "Finge" ser um stream, enviando o dado completo para a função onData
      // Isso se alinha com o que o index.html espera receber.
      // O objeto é encapsulado para corresponder à estrutura original.
      onData({ message: { content: data.response } });

      // 5. Chama a função que finaliza o processo
      if (onComplete) {
        onComplete();
      }

    } catch (error) {
      // Erro de conexão (backend desligado, etc.)
      console.error('Erro de conexão:', error);
      onError(`Não foi possível conectar ao servidor local. Verifique se o backend (app.py) está em execução. Detalhes: ${error.message}`);
    }
  },

  // Funções de armazenamento (sem alteração)
  getStore: (key) => ipcRenderer.invoke('get-store', key),
  setStore: (key, value) => ipcRenderer.send('set-store', key, value),
});