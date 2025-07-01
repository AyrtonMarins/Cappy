const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
    sendMessage: (message) => ipcRenderer.send('send-message', message),
    receiveMessage: (func) => {
        ipcRenderer.on('receive-message', (event, ...args) => func(...args));
    }
});