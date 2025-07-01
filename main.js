const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { PythonShell } = require('python-shell');

/**
 * Cria a janela principal do aplicativo.
 */
function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js') // Aponta para a nossa ponte segura
    }
  });
  mainWindow.loadFile('index.html');
}

// ==================================================================
// HANDLERS DA API (Ouvintes de eventos do Frontend)
// ==================================================================

// Handler para buscar TODAS as atividades
ipcMain.handle('get-activities', async () => {
  let options = {
    mode: 'text',
    pythonPath: 'python',
    pythonOptions: ['-u'],
    scriptPath: __dirname,
    args: ['get_activities_today']
  };
  try {
    const results = await PythonShell.run('app.py', options);
    return JSON.parse(results[0]);
  } catch (err) {
    console.error('Falha ao executar script Python (get-activities):', err);
    return [];
  }
});

// Handler para ADICIONAR uma atividade (usado pelo botão '+')
ipcMain.handle('add-activity', async (event, { name, type }) => {
  let options = {
    mode: 'text',
    pythonPath: 'python',
    pythonOptions: ['-u'],
    scriptPath: __dirname,
    args: ['add_activity', name, type]
  };
  try {
    const results = await PythonShell.run('app.py', options);
    return JSON.parse(results[0]);
  } catch (err) {
    console.error('Falha ao executar script Python (add-activity):', err);
    return { success: false, message: err.message };
  }
});

// Handler para buscar os DETALHES de uma atividade
ipcMain.handle('get-activity-details', async (event, activityId) => {
  let options = {
    mode: 'text',
    pythonPath: 'python',
    pythonOptions: ['-u'],
    scriptPath: __dirname,
    args: ['get_activity_details', activityId]
  };
  try {
    const results = await PythonShell.run('app.py', options);
    return JSON.parse(results[0]);
  } catch (err) {
    console.error(`Falha ao buscar detalhes para o ID ${activityId}:`, err);
    return null;
  }
});

// --- O HANDLER QUE FALTAVA ---
// Handler para processar uma mensagem do CHAT
ipcMain.handle('process-chat-message', async (event, userMessage) => {
  let options = {
    mode: 'text',
    pythonPath: 'python',
    pythonOptions: ['-u'],
    scriptPath: __dirname,
    args: ['process_chat_message', userMessage]
  };
  try {
    const results = await PythonShell.run('app.py', options);
    return JSON.parse(results[0]);
  } catch (err) {
    console.error('Falha ao processar mensagem no Python:', err);
    return { response_text: "Desculpe, ocorreu um erro interno ao falar com minha IA." };
  }
});


// ==================================================================
// CICLO DE VIDA DO APLICATIVO
// ==================================================================

app.whenReady().then(() => {
  createWindow();
  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});