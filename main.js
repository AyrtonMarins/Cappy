const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false,
        }
    });

    mainWindow.loadFile('index.html');
    // mainWindow.webContents.openDevTools();
}

app.whenReady().then(() => {
    createWindow();
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});

ipcMain.on('send-message', (event, message) => {
    console.log(`Mensagem para Python: ${message}`);
    const pythonProcess = spawn('python', ['handler.py', message]);

    let pythonResponse = '';
    pythonProcess.stdout.on('data', (data) => {
        pythonResponse += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Erro no Python: ${data}`);
        event.reply('receive-message', JSON.stringify({
            status: 'error',
            message: `Erro no backend: ${data}`
        }));
    });

    pythonProcess.on('close', (code) => {
        if (code === 0) {
            event.reply('receive-message', pythonResponse);
        }
    });
});