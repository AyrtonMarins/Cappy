const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
// A linha 'require('electron-store')' foi removida daqui.

const createWindow = () => {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  win.loadFile('index.html');
};

// A função dentro de .then() agora é 'async' para permitir o uso de 'await'
app.whenReady().then(async () => {
  // 1. A CORREÇÃO: Usamos import() dinâmico para carregar o módulo ES.
  const { default: Store } = await import('electron-store');
  
  // 2. O resto do código agora fica aqui dentro, após o módulo ser carregado.
  const store = new Store();

  ipcMain.handle('get-store', (event, key) => {
    return store.get(key);
  });

  ipcMain.on('set-store', (event, key, value) => {
    store.set(key, value);
  });

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});